"""Spark UDFs for the OpenAI and Azure OpenAI APIs.

This module provides a builder class for creating Spark UDFs that
communicate with either the public OpenAI API or Azure OpenAI. It
supports UDFs for generating responses, creating embeddings,
and counting tokens.  The UDFs operate on Spark DataFrames and are
optimised for processing large data volumes.

First, obtain a Spark session:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
```

Next, instantiate a UDF builder with your OpenAI API key and model
name, then register the desired UDFs:

```python
import os
from openaivec.spark import UDFBuilder
from pydantic import BaseModel

udf = UDFBuilder.of_openai(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-4.1-nano",
)

class Translation(BaseModel):
    en: str
    fr: str
    ja: str
    es: str
    de: str
    it: str
    pt: str
    ru: str

spark.udf.register(
    "translate",
    udf.responses(
        instructions=(
            "Translate the following text to English, French, Japanese, Spanish, German, Italian, Portuguese, and Russian."
        ),
        response_format=Translation,
    ),
)
```

You can now invoke the UDF from Spark SQL:

```sql
SELECT
    name,
    translate(name) AS t,
    t.en,
    t.fr,
    t.ja,
    t.es,
    t.de,
    t.it,
    t.pt,
    t.ru
FROM fruits;
```

A sample result looks like this:

| name       | t                          | en         | fr     | ja         | es       | de        | it       | pt       | ru        |
|------------|----------------------------|------------|--------|------------|----------|-----------|----------|----------|-----------|
| apple      | {apple, pomme, リン…}      | apple      | pomme  | リンゴ     | manzana  | Apfel     | mela     | maçã     | яблоко    |
| banana     | {banana, banane, …}        | banana     | banane | バナナ     | plátano  | Banane    | banana   | banana   | банан     |
| cherry     | {cherry, cerise, …}        | cherry     | cerise | さくらんぼ | cereza   | Kirsche   | ciliegia | cereja   | вишня     |
| mango      | {mango, mangue, マ…}       | mango      | mangue | マンゴー   | mango    | Mango     | mango    | manga    | манго     |
| orange     | {orange, orange, …}        | orange     | orange | オレンジ   | naranja  | Orange    | arancia  | laranja  | апельсин  |
"""

from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Iterator, List, Optional, Type, TypeVar, Union, get_args, get_origin

import httpx
import pandas as pd
import tiktoken
from openai import AzureOpenAI, OpenAI
from pydantic import BaseModel
from pyspark.sql.pandas.functions import pandas_udf
from pyspark.sql.types import ArrayType, BooleanType, FloatType, IntegerType, StringType, StructField, StructType

from openaivec import VectorizedEmbeddingsOpenAI, VectorizedResponsesOpenAI
from openaivec.log import observe
from openaivec.serialize import deserialize_base_model, serialize_base_model
from openaivec.util import TextChunker
from openaivec.responses import VectorizedResponses

__all__ = [
    "UDFBuilder",
    "count_tokens_udf",
]

_logger: Logger = getLogger(__name__)

# Global Singletons
_openai_client: Optional[OpenAI] = None
_vectorized_client: Optional[VectorizedResponses] = None
_embedding_client: Optional[VectorizedEmbeddingsOpenAI] = None

T = TypeVar("T")


def _get_openai_client(conf: "UDFBuilder", http_client: httpx.Client) -> OpenAI:
    global _openai_client
    if _openai_client is None:
        if conf.endpoint is None:
            _openai_client = OpenAI(
                api_key=conf.api_key,
                http_client=http_client,
            )
        else:
            _openai_client = AzureOpenAI(
                api_key=conf.api_key,
                api_version=conf.api_version,
                azure_endpoint=conf.endpoint,
                http_client=http_client,
            )
    return _openai_client


def _get_vectorized_openai_client(
    conf: "UDFBuilder",
    system_message: str,
    response_format: Type[T],
    temperature: float,
    top_p: float,
    http_client: httpx.Client,
) -> VectorizedResponses:
    global _vectorized_client
    if _vectorized_client is None:
        _vectorized_client = VectorizedResponsesOpenAI(
            client=_get_openai_client(conf, http_client),
            model_name=conf.model_name,
            system_message=system_message,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
            is_parallel=conf.is_parallel,
        )
    return _vectorized_client


def _get_vectorized_embedding_client(conf: "UDFBuilder", http_client: httpx.Client) -> VectorizedEmbeddingsOpenAI:
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = VectorizedEmbeddingsOpenAI(
            client=_get_openai_client(conf, http_client),
            model_name=conf.model_name,
        )
    return _embedding_client


def _safe_dump(x: BaseModel) -> Optional[dict]:
    try:
        return x.model_dump()
    except Exception as e:
        _logger.error(f"Error during model_dump: {e}")
        return None


def _safe_cast_str(x: str) -> Optional[str]:
    try:
        return str(x)
    except Exception as e:
        _logger.error(f"Error during casting to str: {e}")
        return None


def _python_type_to_spark(python_type):
    origin = get_origin(python_type)

    # For list types (e.g., List[int])
    if origin is list or origin is List:
        # Retrieve the inner type and recursively convert it
        inner_type = get_args(python_type)[0]
        return ArrayType(_python_type_to_spark(inner_type))

    # For Optional types (Union[..., None])
    elif origin is Union:
        non_none_args = [arg for arg in get_args(python_type) if arg is not type(None)]
        if len(non_none_args) == 1:
            return _python_type_to_spark(non_none_args[0])
        else:
            raise ValueError(f"Unsupported Union type with multiple non-None types: {python_type}")

    # For nested Pydantic models (to be treated as Structs)
    elif isinstance(python_type, type) and issubclass(python_type, BaseModel):
        return _pydantic_to_spark_schema(python_type)

    # Basic type mapping
    elif python_type is int:
        return IntegerType()
    elif python_type is float:
        return FloatType()
    elif python_type is str:
        return StringType()
    elif python_type is bool:
        return BooleanType()
    else:
        raise ValueError(f"Unsupported type: {python_type}")


def _pydantic_to_spark_schema(model: Type[BaseModel]) -> StructType:
    fields = []
    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        # Use outer_type_ to correctly handle types like Optional
        spark_type = _python_type_to_spark(field_type)
        # Set nullable to True (adjust logic as needed)
        fields.append(StructField(field_name, spark_type, nullable=True))
    return StructType(fields)


@dataclass(frozen=True)
class UDFBuilder:
    """Builder for Spark pandas‑UDFs that talk to the OpenAI / Azure OpenAI API.

    An instance stores authentication parameters and batching behaviour so that
    the same object can be reused on worker nodes.  The helper exposes factory
    methods for creating completion‑ and embedding‑oriented UDFs while hiding
    the low‑level HTTP and model‑selection details.

    Attributes:
        api_key: OpenAI / Azure API key.
        endpoint: Azure endpoint base URL or ``None`` for public OpenAI.
        api_version: Azure API version, ignored for public OpenAI.
        model_name: Deployment (Azure) or model (OpenAI) name.
        batch_size: Number of rows sent in one request to the backend.
        is_parallel: Whether vectorized requests are executed concurrently.
        http2: Enable HTTP/2 in the underlying ``httpx.Client``.
        ssl_verify: Toggle TLS certificate verification in ``httpx``.
    """

    # Params for Constructor
    api_key: str
    endpoint: Optional[str]
    api_version: Optional[str]

    # Params for chat_completion
    model_name: str  # it would be the name of deployment for Azure

    # Params for minibatch
    batch_size: int = 256
    is_parallel: bool = False

    # Params for httpx.Client
    http2: bool = True
    ssl_verify: bool = False

    @classmethod
    def of_azureopenai(
        cls,
        api_key: str,
        api_version: str,
        endpoint: str,
        model_name: str,
        batch_size: int = 256,
        http2: bool = True,
        ssl_verify: bool = False,
        is_parallel: bool = False,
    ) -> "UDFBuilder":
        """Create a builder configured for Azure OpenAI."""
        return cls(
            api_key=api_key,
            api_version=api_version,
            endpoint=endpoint,
            model_name=model_name,
            batch_size=batch_size,
            http2=http2,
            ssl_verify=ssl_verify,
            is_parallel=is_parallel,
        )

    @classmethod
    def of_openai(
        cls,
        api_key: str,
        model_name: str,
        batch_size: int = 256,
        http2: bool = True,
        ssl_verify: bool = False,
        is_parallel: bool = False,
    ) -> "UDFBuilder":
        """Create a builder configured for the public OpenAI API."""
        return cls(
            api_key=api_key,
            api_version=None,
            endpoint=None,
            model_name=model_name,
            batch_size=batch_size,
            http2=http2,
            ssl_verify=ssl_verify,
            is_parallel=is_parallel,
        )

    def __post_init__(self):
        assert self.api_key, "api_key must be set"
        assert self.model_name, "model_name must be set"

    @observe(_logger)
    def responses(
        self, instructions: str, response_format: Type[T] = str, temperature: float = 0.0, top_p: float = 1.0
    ):
        """Return a pandas‑UDF that produces chat completions.

        Args:
            instructions: The system prompt prepended to every request.
            response_format: ``str`` or a *pydantic* model describing the
                JSON structure expected from the model.
            temperature: Sampling temperature.
            top_p: Nucleus‑sampling parameter.

        Returns:
            A pandas UDF whose output schema is either ``StringType`` or the
                struct derived from ``response_format``.
        """
        if issubclass(response_format, BaseModel):
            spark_schema = _pydantic_to_spark_schema(response_format)
            json_schema_string = serialize_base_model(response_format)

        elif issubclass(response_format, str):
            spark_schema = StringType()
            json_schema_string = None

        else:
            raise ValueError(f"Unsupported response_format: {response_format}")

        @pandas_udf(spark_schema)
        def fn_struct(col: Iterator[pd.Series]) -> Iterator[pd.DataFrame]:
            cls = str
            if json_schema_string:
                cls = deserialize_base_model(json_schema_string)

            http_client = httpx.Client(http2=self.http2, verify=self.ssl_verify)
            client_vec = _get_vectorized_openai_client(
                conf=self,
                system_message=instructions,
                response_format=cls,
                temperature=temperature,
                top_p=top_p,
                http_client=http_client,
            )

            for part in col:
                predictions = client_vec.parse(part.tolist(), self.batch_size)
                result = pd.Series(predictions)
                yield pd.DataFrame(result.map(_safe_dump).tolist())

        @pandas_udf(spark_schema)
        def fn_str(col: Iterator[pd.Series]) -> Iterator[pd.Series]:
            http_client = httpx.Client(http2=self.http2, verify=self.ssl_verify)
            client_vec = _get_vectorized_openai_client(
                conf=self,
                system_message=instructions,
                response_format=str,
                temperature=temperature,
                top_p=top_p,
                http_client=http_client,
            )

            for part in col:
                predictions = client_vec.parse(part.tolist(), self.batch_size)
                result = pd.Series(predictions)
                yield result.map(_safe_cast_str)

        if issubclass(response_format, str):
            return fn_str

        else:
            return fn_struct

    @observe(_logger)
    def embeddings(self):
        """Return a pandas‑UDF that generates embedding vectors.

        The UDF accepts a column of strings and yields an
        ``ArrayType(FloatType())`` column containing model embeddings.
        """

        @pandas_udf(ArrayType(FloatType()))
        def fn(col: Iterator[pd.Series]) -> Iterator[pd.Series]:
            http_client = httpx.Client(http2=self.http2, verify=self.ssl_verify)
            client_emb = _get_vectorized_embedding_client(self, http_client)

            for part in col:
                yield pd.Series(client_emb.create(part.tolist(), self.batch_size))

        return fn


# singleton for tiktoken
_tiktoken_enc: Optional[tiktoken.Encoding] = None


def count_tokens_udf(model_name: str = "gpt-4o"):
    """Create a pandas‑UDF that counts tokens for every string cell.

    The UDF uses *tiktoken* to approximate tokenisation and caches the
    resulting ``Encoding`` object per executor.

    Args:
        model_name: Model identifier understood by ``tiktoken``.

    Returns:
        A pandas UDF producing an ``IntegerType`` column with token counts.
    """

    @pandas_udf(IntegerType())
    def fn(col: Iterator[pd.Series]) -> Iterator[pd.Series]:
        global _tiktoken_enc
        if _tiktoken_enc is None:
            _tiktoken_enc = tiktoken.encoding_for_model(model_name)

        for part in col:
            yield part.map(lambda x: len(_tiktoken_enc.encode(x)) if isinstance(x, str) else 0)

    return fn


def split_to_chunks_udf(model_name: str, max_tokens: int, sep: List[str]):
    """Create a pandas‑UDF that splits text into token‑bounded chunks.

    Args:
        model_name: Model identifier passed to *tiktoken*.
        max_tokens: Maximum tokens allowed per chunk.
        sep: Ordered list of separator strings used by ``TextChunker``.

    Returns:
        A pandas UDF producing an ``ArrayType(StringType())`` column whose
            values are lists of chunks respecting the ``max_tokens`` limit.
    """

    @pandas_udf(ArrayType(StringType()))
    def fn(col: Iterator[pd.Series]) -> Iterator[pd.Series]:
        global _tiktoken_enc
        if _tiktoken_enc is None:
            _tiktoken_enc = tiktoken.encoding_for_model(model_name)

        chunker = TextChunker(_tiktoken_enc)

        for part in col:
            yield part.map(lambda x: chunker.split(x, max_tokens=max_tokens, sep=sep) if isinstance(x, str) else [])

    return fn
