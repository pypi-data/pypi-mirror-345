## What is Crypticorn?

Crypticorn is at the forefront of cutting-edge crypto trading with Machine Learning.

Use this API Client to access valuable data sources, contribute to the Hive AI - a community driven AI Meta Model for predicting the
crypto market - and programmatically interact with the entire Crypticorn ecosystem.

## Installation

>Python 3.10+ required

You can install the latest stable version from PyPi:
```bash
pip install crypticorn
```

If you want the latest version, which could be a pre release, run:
```bash
pip install --pre crypticorn
```

You can install extra dependencies grouped in the extras `extra` (heavy dependencies that do not come with the default version) `dev` (development) and `test` (testing). The `extra` dependencies include heavy libraries like `pandas`, which is only used in a few custom API operations (suffixed with `_fmt`), which preprocess the response data as a pandas Dataframe for convenience.

## Structure

Our API is available as an asynchronous Python SDK. The main entry point you need is the `ApiClient` class, which you would import like this:
```python
from crypticorn import ApiClient
```
The ApiClient serves as the central interface for API operations. It instantiates multiple API wrappers corresponding to our micro services.

Request and response models for API operations should be accessed through the appropriate sub package.

Note: All symbols are re-exported at the sub package level for convenience.

```python
from crypticorn.trade import BotStatus
```

The `common` submodule contains shared classes not bound to a specific API.
```python
from crypticorn.common import Scope, Exchange
```

## Authentication

To get started, [create an API key in your dashboard](https://app.crypticorn.com/account/developer). Then instantiate the `ApiClient` class with your copied key.

## Basic Usage

### With Async Context Protocol
```python
async with ApiClient(base_url=BaseUrl.Prod, api_key="your-api-key") as client:
        await client.pay.products.get_products()
```

### Without Async Context Protocol
Without the context you need to close the session manually.
```python
client = ApiClient(base_url=BaseUrl.Prod, api_key="your-api-key")
asyncio.run(client.pay.models.get_products())
asyncio.run(client.close())
```
...or wrapped in a function
async def main():
    await client.pay.products.get_products()

asyncio.run(main())
asyncio.run(client.close())

## Response Types

There are three different available output formats you can choose from:

### Serialized Response
You can get fully serialized responses as pydantic models. Using this, you get the full benefits of pydantic's type checking.
```python
response = await client.pay.products.get_products()
print(response)
```
The output would look like this:
```python
[ProductModel(id='67e8146e7bae32f3838fe36a', name='Awesome Product', price=5.0, scopes=None, duration=30, description='You need to buy this', is_active=True)]
```

### Serialized Response with HTTP Info
```python
await client.pay.products.get_products_with_http_info()
print(res)
```
The output would look like this:
```python
status_code=200 headers={'Date': 'Wed, 09 Apr 2025 19:15:19 GMT', 'Content-Type': 'application/json'} data=[ProductModel(id='67e8146e7bae32f3838fe36a', name='Awesome Product', price=5.0, scopes=None, duration=30, description='You need to buy this', is_active=True)] raw_data=b'[{"id":"67e8146e7bae32f3838fe36a","name":"Awesome Product","price":5.0,"duration":30,"description":"You need to buy this","is_active":true}]'
```
You can then access the data of the response (as serialized output (1) or as JSON string in bytes (2)) with:
```python
print(res.data)
print(res.raw_data)
```
On top of that you get some information about the request:
```python
print(res.status_code)
print(res.headers)
```

### JSON Response
You can receive a classical JSON response by suffixing the function name with `_without_preload_content`
```python
response = await client.pay.products.get_products_without_preload_content()
print(await response.json())
```
The output would look like this:
```python
[{'id': '67e8146e7bae32f3838fe36a', 'name': 'Awesome Product', 'price': 5.0, 'duration': 30, 'description': 'You need to buy this', 'is_active': True}]
```

## Advanced Usage

You can override some configuration for specific services. If you just want to use the API as is, you don't need to configure anything.
This might be of use if you are testing a specific API locally.

To override e.g. the host for the Hive client to connect to http://localhost:8000 instead of the default proxy, you would do:
```python
from crypticorn.hive import Configuration as Hiveconfig
from crypticorn.common import Service
async with ApiClient(base_url=BaseUrl.DEV) as client:
        client.configure(config=HiveConfig(host="http://localhost:8000"), client=Service.HIVE)
```