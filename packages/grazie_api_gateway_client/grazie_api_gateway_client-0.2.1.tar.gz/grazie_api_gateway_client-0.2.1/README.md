# Grazie Api Gateway Client

> Note, this package is deprecated, please refer to [Grazie Api Gateway Client V2](#Grazie-Api-Gateway-Client-V2) first and check if the new client library supports functionality you need.

This package provides api client for JetBrains AI Platform llm functionality.
Supported methods are chat, completion and embeddings.

Support for Grazie NLP services is planned in the future.

You can try models in the browser by going to https://try.ai.intellij.net/
or using the command-line interface.

```shell
poetry run -C libs/grazie_api_gateway_client python3 -m grazie.api.client -p openai-gpt-4 chat 'Who was the most famous pop star in the 90s?'
```

## Usage

First you have to create an instance of client,
please check class documentation to know more about parameters:

```
client = GrazieApiGatewayClient(
    grazie_agent=GrazieAgent(name="grazie-api-gateway-client-readme", version="dev"),
    url=GrazieApiGatewayUrls.STAGING,
    auth_type=AuthType.USER,
    grazie_jwt_token=***
)
```

Below are examples of usage by method:

### Completion
Without suffix:
```
client.complete(
    prompt=CompletionPrompt("Once upon a time there was a unicorn. "),
    profile=Profile.GRAZIE_GPT_NEO_TINY_TEXT,
)
```

With suffix:
```
client.complete(
    prompt=CompletionPrompt(
        prompt="Once upon a time there was a unicorn. ", 
        suffix=" And they lived happily ever after!"
    ),
    profile=Profile.GRAZIE_GPT_NEO_TINY_TEXT,
)
```

### Chat

```
client.chat(
    chat=ChatPrompt()
        .add_system("You are a helpful assistant.")
        .add_user("Who won the world series in 2020?"),
    profile=Profile.OPENAI_CHAT_GPT
)
```

Additionally you can pass id of your prompt or feature via `prompt_id` parameter.
This identifier can later be used to check spending and calculate price of the feature per user or
per call.

If you develop prompt which should answer in a structured format (i.e. JSON) it's better to pass
temperature = 0.
This makes generation deterministic (almost) and will provide parsable responses more reliably.

```
client.chat(
    chat=ChatPrompt()
        .add_system("You are a helpful assistant.")
        .add_user("Who won the world series in 2020?"),
    profile=Profile.OPENAI_CHAT_GPT,
    parameters={
        LLMParameters.Temperature: Parameters.FloatValue(0.0)
    }
)
```

Note: this parameter is currently only supported for OpenAI models.

#### Streaming

Outputs from chat models can be slow, to show progress to a user you can call chat_stream.
The output would be a stream of text chunks.

```
response = ""
for chunk in client.chat_stream(
    chat=ChatPrompt()
        .add_user("Who won the world series in 2020?")
        .add_assistant("The Los Angeles Dodgers won the World Series in 2020.")
        .add_user("Where was it played? Write a small poem about it!"),
    profile=Profile.OPENAI_CHAT_GPT
):
    response += chunk.chunk
```

### Embeddings

You can also use api to build float vector embeddings for sentences and texts.

```
client.embed(
    request=EmbeddingRequest(texts=["Sky is blue."], model="sentence-transformers/LaBSE", format_cbor=True)
)
```

Note: use cbor format for production applications. Pass `format_cbor=False` only to simplify
development initially as the answer will be provided as json.

Additionally, you can use openai embeddings:

```
client.llm_embed(
    request=LLMEmbeddingRequest(
        texts=["Sky is blue."],
        profile=Profile.OPENAI_EMBEDDING_LARGE,
        dimensions=768
    )
)
```

### Question Answering

You can run question answering against corpus of documents, like documentation or Youtrack issues.

```
response = ""
for chunk in grazie_api.answer_stream(
    query="How to write a coroutine?", 
    data_source="kotlin_1.9.23"
):
    if chunk.chunk.summaryChunk:
        response += chunk.chunk.summaryChunk
```

You can find the list of available data sources on https://try.ai.intellij.net/qa

#### Plain Retrieval

You can also run question answering against a corpus of documents, retrieving only raw documents:

```
client.retrieve(
    query="How to change a font size in Fleet?",
    data_source="jetbrains-fleet-1.36",
    profile=Profile.OPENAI_GPT_4_TURBO,
    size=10,
)
```

Or providing a list of prioritized data sources:

```
client.retrieve_v2(
    query="How to change a font size in Fleet?",
    config_name="fleet-ide",
    data_source_lists=[
        [
            PrioritizedSource(name="jetbrains-fleet-1.45", priority=0), 
            PrioritizedSource(name="jetbrains-fleet-1.46", priority=1), 
        ]
    ],
    profile=Profile.OPENAI_GPT_4_TURBO,
    size=10,
)
```


# Grazie Api Gateway Client V2

The api client V2 for JetBrains AI Platform.

## Implemented features

* [Tasks](#TaskAPI)

## Basic usage

Client is available in two flavours `APIGatewayClient` and `AsyncAPIGatewayClient`.

### ApiGatewayClient
```python
import os

from grazie.api.client_v2 import APIGatewayClient, GatewayEndpoint

api_key = os.getenv("GRAZIE_JWT_TOKEN")
client = APIGatewayClient(
    api_key=api_key,
    endpoint=GatewayEndpoint.STAGING,
)

# Fetch all available tasks in TaskAPI
print(client.tasks.roster())
```

### AsyncApiGatewayClient
```python
import asyncio
import os

from grazie.api.client_v2 import AsyncAPIGatewayClient, GatewayEndpoint


async def main():
    api_key = os.getenv("GRAZIE_JWT_TOKEN")
    client = AsyncAPIGatewayClient(
        api_key=api_key,
        endpoint=GatewayEndpoint.STAGING,
    )

    # Fetch all available tasks in TaskAPI
    print(await client.tasks.roster())

asyncio.run(main())
```

## TaskAPI

Please refer to the `client.tasks.roster()` for the list of available task IDs.
The roster output is in the format of `<task-id>:<task-tag>`

See the [Swagger page](https://api.app.stgn.grazie.aws.intellij.net/swagger-ui/index.html?urls.primaryName=Tasks)
to find parameters for the specific task.

### Execute a task

```python
from grazie.api.client_v2 import APIGatewayClient

client = APIGatewayClient()
client.tasks.execute(
    id="code-generate:default",
    parameters=dict(
        instructions="Write me a simple python script",
        prefix="",
        suffix="",
        language="python",
    )
)
```
