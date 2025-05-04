"""Pandas Series / DataFrame extension for asynchronous OpenAI operations.

## Setup
```python
from openai import AsyncOpenAI
from openaivec.aio import pandas_ext

# Set up the AsyncOpenAI client to use with pandas_ext
pandas_ext.use(AsyncOpenAI())

# Set up the model_name for responses and embeddings
pandas_ext.responses_model("gpt-4.1-nano")
pandas_ext.embeddings_model("text-embedding-3-small")
```

"""

import inspect
import json
import os
import logging
from typing import Awaitable, Callable, Type, TypeVar

import pandas as pd
from openai import AsyncAzureOpenAI, AsyncOpenAI
from pydantic import BaseModel
import tiktoken

from openaivec.aio import AsyncBatchEmbeddings, AsyncBatchResponses

__all__ = [
    "use",
    "responses_model",
    "embeddings_model",
    "use_openai",
    "use_azure_openai",
]

_LOGGER = logging.getLogger(__name__)


T = TypeVar("T")

_CLIENT: AsyncOpenAI | None = None
_RESPONSES_MODEL_NAME = "gpt-4o-mini"
_EMBEDDINGS_MODEL_NAME = "text-embedding-3-small"

_TIKTOKEN_ENCODING = tiktoken.encoding_for_model(_RESPONSES_MODEL_NAME)


def use(client: AsyncOpenAI) -> None:
    """Register a custom asynchronous OpenAI‑compatible client.

    Args:
        client (AsyncOpenAI): A pre‑configured `openai.AsyncOpenAI` or
            `openai.AsyncAzureOpenAI` instance.
            The same instance is reused by every helper in this module.
    """
    if not isinstance(client, (AsyncOpenAI, AsyncAzureOpenAI)):
        raise TypeError("The client must be an instance of `openai.AsyncOpenAI` or `openai.AsyncAzureOpenAI`.")

    global _CLIENT
    _CLIENT = client


def use_openai(api_key: str) -> None:
    """Create and register a default `openai.AsyncOpenAI` client.

    Args:
        api_key (str): Value forwarded to the ``api_key`` parameter of
            `openai.AsyncOpenAI`.
    """
    global _CLIENT
    _CLIENT = AsyncOpenAI(api_key=api_key)


def use_azure_openai(api_key: str, endpoint: str, api_version: str) -> None:
    """Create and register an `openai.AsyncAzureOpenAI` client.

    Args:
        api_key (str): Azure OpenAI subscription key.
        endpoint (str): Resource endpoint, e.g.
            ``https://<resource>.openai.azure.com``.
        api_version (str): REST API version such as ``2024‑02‑15-preview``.
    """
    global _CLIENT
    _CLIENT = AsyncAzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
    )


def responses_model(name: str) -> None:
    """Override the model used for text responses.

    Args:
        name (str): Model name as listed in the OpenAI API
            (for example, ``gpt-4o-mini``).
    """
    global _RESPONSES_MODEL_NAME, _TIKTOKEN_ENCODING
    _RESPONSES_MODEL_NAME = name

    try:
        _TIKTOKEN_ENCODING = tiktoken.encoding_for_model(name)

    except KeyError:
        _LOGGER.warning(
            "The model name '%s' is not supported by tiktoken. Instead, using the 'o200k_base' encoding.",
            name,
        )
        _TIKTOKEN_ENCODING = tiktoken.get_encoding("o200k_base")


def embeddings_model(name: str) -> None:
    """Override the model used for text embeddings.

    Args:
        name (str): Embedding model name, e.g. ``text-embedding-3-small``.
    """
    global _EMBEDDINGS_MODEL_NAME
    _EMBEDDINGS_MODEL_NAME = name


def _get_openai_client() -> AsyncOpenAI:
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    if "OPENAI_API_KEY" in os.environ:
        _CLIENT = AsyncOpenAI()
        return _CLIENT

    aoai_param_names = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
    ]

    if all(param in os.environ for param in aoai_param_names):
        _CLIENT = AsyncAzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        )

        return _CLIENT

    raise ValueError(
        "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable or provide Azure OpenAI parameters."
        "If using Azure OpenAI, ensure AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_API_VERSION are set."
        "If using OpenAI, ensure OPENAI_API_KEY is set."
        " Alternatively, register a client using `openaivec.aio.pandas_ext.use(client)`."
    )


def _extract_value(x, series_name):
    """Return a homogeneous ``dict`` representation of any Series value.

    Args:
        x: Single element taken from the Series.
            series_name (str): Name of the Series (only used for logging).

    Returns:
        dict: A dictionary representation or an empty ``dict`` if ``x`` cannot
            be coerced.
    """
    if x is None:
        return {}
    elif isinstance(x, BaseModel):
        return x.model_dump()
    elif isinstance(x, dict):
        return x

    _LOGGER.warning(f"The value '{x}' in the series is not a dict or BaseModel. Returning an empty dict.")
    return {}


@pd.api.extensions.register_series_accessor("aio")
class OpenAIVecSeriesAccessor:
    """pandas Series accessor (``.aio``) that adds OpenAI helpers."""

    def __init__(self, series_obj: pd.Series):
        self._obj = series_obj

    async def responses(
        self,
        instructions: str,
        response_format: Type[T] = str,
        batch_size: int = 128,
        temperature: float = 0.0,
        top_p: float = 1.0,
    ) -> pd.Series:
        """Call an LLM once for every Series element (asynchronously).

        Example:
            ```python
            animals = pd.Series(["cat", "dog", "elephant"])
            # Must be awaited
            results = await animals.aio.responses("translate to French")
            ```
            This method returns a Series of strings, each containing the
            assistant's response to the corresponding input.
            The model used is set by the `responses_model` function.
            The default model is `gpt-4o-mini`.

        Args:
            instructions (str): System prompt prepended to every user message.
            response_format (Type[T], optional): Pydantic model or built‑in
                type the assistant should return. Defaults to ``str``.
            batch_size (int, optional): Number of prompts grouped into a single
                request. Defaults to ``128``.
            temperature (float, optional): Sampling temperature. Defaults to ``0``.
            top_p (float, optional): Nucleus sampling parameter. Defaults to ``1``.

        Returns:
            pandas.Series: Series whose values are instances of ``response_format``.

        Note:
            This is an asynchronous method and must be awaited.
        """
        client: AsyncBatchResponses = AsyncBatchResponses(
            client=_get_openai_client(),
            model_name=_RESPONSES_MODEL_NAME,
            system_message=instructions,
            response_format=response_format,
            temperature=temperature,
            top_p=top_p,
        )

        # Await the async operation
        results = await client.parse(self._obj.tolist(), batch_size=batch_size)

        return pd.Series(
            results,
            index=self._obj.index,
            name=self._obj.name,
        )

    async def embeddings(self, batch_size: int = 128) -> pd.Series:
        """Compute OpenAI embeddings for every Series element (asynchronously).

        Example:
            ```python
            animals = pd.Series(["cat", "dog", "elephant"])
            # Must be awaited
            embeddings = await animals.aio.embeddings()
            ```
            This method returns a Series of numpy arrays, each containing the
            embedding vector for the corresponding input.
            The embedding model is set by the `embeddings_model` function.
            The default embedding model is `text-embedding-3-small`.

        Args:
            batch_size (int, optional): Number of inputs grouped into a
                single request. Defaults to ``128``.

        Returns:
            pandas.Series: Series whose values are ``np.ndarray`` objects
                (dtype ``float32``).

        Note:
            This is an asynchronous method and must be awaited.
        """
        client: AsyncBatchEmbeddings = AsyncBatchEmbeddings(
            client=_get_openai_client(),
            model_name=_EMBEDDINGS_MODEL_NAME,
        )

        # Await the async operation
        results = await client.create(self._obj.tolist(), batch_size=batch_size)

        return pd.Series(
            results,
            index=self._obj.index,
            name=self._obj.name,
        )

    def count_tokens(self) -> pd.Series:
        """Count `tiktoken` tokens per row.

        Example:
            ```python
            animals = pd.Series(["cat", "dog", "elephant"])
            # Note: count_tokens is synchronous and remains under the .ai accessor
            # if the synchronous pandas_ext is imported.
            # If only aio.pandas_ext is imported, this method is available under .aio
            animals.aio.count_tokens()
            ```
            This method uses the `tiktoken` library to count tokens based on the
            model name set by `responses_model`.

        Returns:
            pandas.Series: Token counts for each element.
        """
        return self._obj.map(_TIKTOKEN_ENCODING.encode).map(len).rename("num_tokens")

    def extract(self) -> pd.DataFrame:
        """Expand a Series of Pydantic models/dicts into columns.

        Example:
            ```python
            animals = pd.Series([
                {"name": "cat", "legs": 4},
                {"name": "dog", "legs": 4},
                {"name": "elephant", "legs": 4},
            ])
            # Note: extract is synchronous and remains under the .ai accessor
            # if the synchronous pandas_ext is imported.
            # If only aio.pandas_ext is imported, this method is available under .aio
            animals.aio.extract()
            ```
            This method returns a DataFrame with the same index as the Series,
            where each column corresponds to a key in the dictionaries.
            If the Series has a name, extracted columns are prefixed with it.

        Returns:
            pandas.DataFrame: Expanded representation.
        """
        extracted = pd.DataFrame(
            self._obj.map(lambda x: _extract_value(x, self._obj.name)).tolist(),
            index=self._obj.index,
        )

        if self._obj.name:
            # If the Series has a name and all elements are dict or BaseModel, use it as the prefix for the columns
            extracted.columns = [f"{self._obj.name}_{col}" for col in extracted.columns]
        return extracted


@pd.api.extensions.register_dataframe_accessor("aio")
class OpenAIVecDataFrameAccessor:
    """pandas DataFrame accessor (``.aio``) that adds OpenAI helpers."""

    def __init__(self, df_obj: pd.DataFrame):
        self._obj = df_obj

    def extract(self, column: str) -> pd.DataFrame:
        """Flatten one column of Pydantic models/dicts into top‑level columns.

        Example:
            ```python
            df = pd.DataFrame([
                {"animal": {"name": "cat", "legs": 4}},
                {"animal": {"name": "dog", "legs": 4}},
                {"animal": {"name": "elephant", "legs": 4}},
            ])
            # Note: extract is synchronous and remains under the .ai accessor
            # if the synchronous pandas_ext is imported.
            # If only aio.pandas_ext is imported, this method is available under .aio
            df.aio.extract("animal")
            ```
            This method returns a DataFrame with the same index as the original,
            where each column corresponds to a key in the dictionaries.
            The source column is dropped.

        Args:
            column (str): Column to expand.

        Returns:
            pandas.DataFrame: Original DataFrame with the extracted columns; the source column is dropped.
        """
        if column not in self._obj.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

        return (
            self._obj.pipe(lambda df: df.reset_index(drop=True))
            # Use .aio.extract here as we are within the aio accessor class
            .pipe(lambda df: df.join(df[column].aio.extract()))
            .pipe(lambda df: df.set_index(self._obj.index))
            .pipe(lambda df: df.drop(columns=[column], axis=1))
        )

    async def responses(
        self,
        instructions: str,
        response_format: Type[T] = str,
        batch_size: int = 128,
        temperature: float = 0.0,
        top_p: float = 1.0,
    ) -> pd.Series:
        """Generate a response for each row after serialising it to JSON (asynchronously).

        Example:
            ```python
            df = pd.DataFrame([
                {"name": "cat", "legs": 4},
                {"name": "dog", "legs": 4},
                {"name": "elephant", "legs": 4},
            ])
            # Must be awaited
            results = await df.aio.responses("what is the animal's name?")
            ```
            This method returns a Series of strings, each containing the
            assistant's response to the corresponding input.
            Each row is serialised to JSON before being sent to the assistant.
            The model used is set by the `responses_model` function.
            The default model is `gpt-4o-mini`.

        Args:
            instructions (str): System prompt for the assistant.
            response_format (Type[T], optional): Desired Python type of the
                responses. Defaults to ``str``.
            batch_size (int, optional): Number of requests sent in one batch.
                Defaults to ``128``.
            temperature (float, optional): Sampling temperature. Defaults to ``0``.
            top_p (float, optional): Nucleus sampling parameter. Defaults to ``1``.

        Returns:
            pandas.Series: Responses aligned with the DataFrame’s original index.

        Note:
            This is an asynchronous method and must be awaited.
        """
        series_of_json = self._obj.pipe(
            lambda df: (
                pd.Series(df.to_dict(orient="records"), index=df.index, name="record").map(
                    lambda x: json.dumps(x, ensure_ascii=False)
                )
            )
        )
        # Await the call to the async Series method using .aio
        return await series_of_json.aio.responses(
            instructions=instructions,
            response_format=response_format,
            batch_size=batch_size,
            temperature=temperature,
            top_p=top_p,
        )

    async def pipe(self, func: Callable[[pd.DataFrame], Awaitable[T] | T]) -> T:
        """
        Apply a function to the DataFrame, supporting both synchronous and asynchronous functions.

        This method allows chaining operations on the DataFrame, similar to pandas' `pipe` method,
        but with support for asynchronous functions.

        Args:
            func (Callable[[pd.DataFrame], Awaitable[T] | T]): A function that takes a DataFrame
                as input and returns either a result or an awaitable result.

        Returns:
            T: The result of applying the function, either directly or after awaiting it.

        Note:
            This is an asynchronous method and must be awaited if the function returns an awaitable.
        """
        result = func(self._obj)
        if inspect.isawaitable(result):
            return await result
        else:
            return result

    async def assign(self, **kwargs):
        """Asynchronously assign new columns to the DataFrame, evaluating sequentially.

        This method extends pandas' `assign` method by supporting asynchronous
        functions as column values and evaluating assignments sequentially, allowing
        later assignments to refer to columns created earlier in the same call.

        For each key-value pair in `kwargs`:
        - If the value is a callable, it is invoked with the current state of the DataFrame
          (including columns created in previous steps of this `assign` call).
          If the result is awaitable, it is awaited; otherwise, it is used directly.
        - If the value is not callable, it is assigned directly to the new column.

        Example:
            ```python
            async def compute_column(df):
                # Simulate an asynchronous computation
                await asyncio.sleep(1)
                return df["existing_column"] * 2

            async def use_new_column(df):
                # Access the column created in the previous step
                await asyncio.sleep(1)
                return df["new_column"] + 5


            df = pd.DataFrame({"existing_column": [1, 2, 3]})
            # Must be awaited
            df = await df.aio.assign(
                new_column=compute_column,
                another_column=use_new_column
            )
            ```

        Args:
            **kwargs: Column names as keys and either static values or callables
                (synchronous or asynchronous) as values.

        Returns:
            pandas.DataFrame: A new DataFrame with the assigned columns.

        Note:
            This is an asynchronous method and must be awaited.
        """
        df_current = self._obj.copy()
        for key, value in kwargs.items():
            if callable(value):
                result = value(df_current)
                if inspect.isawaitable(result):
                    column_data = await result
                else:
                    column_data = result
            else:
                column_data = value

            df_current[key] = column_data

        return df_current
