# pay-python
Nkwa Pay SDK for Python

<!-- Start Summary [summary] -->
## Summary

Nkwa Pay API: Use this API to integrate mobile money across your payment flows, create and manage payments, collections, and disbursements.

Read the docs at https://docs.mynkwa.com/api-reference
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [pay-python](https://github.com/nkwa/pay-python/blob/master/#pay-python)
  * [SDK Installation](https://github.com/nkwa/pay-python/blob/master/#sdk-installation)
  * [IDE Support](https://github.com/nkwa/pay-python/blob/master/#ide-support)
  * [SDK Example Usage](https://github.com/nkwa/pay-python/blob/master/#sdk-example-usage)
  * [Authentication](https://github.com/nkwa/pay-python/blob/master/#authentication)
  * [Available Resources and Operations](https://github.com/nkwa/pay-python/blob/master/#available-resources-and-operations)
  * [Retries](https://github.com/nkwa/pay-python/blob/master/#retries)
  * [Error Handling](https://github.com/nkwa/pay-python/blob/master/#error-handling)
  * [Server Selection](https://github.com/nkwa/pay-python/blob/master/#server-selection)
  * [Custom HTTP Client](https://github.com/nkwa/pay-python/blob/master/#custom-http-client)
  * [Resource Management](https://github.com/nkwa/pay-python/blob/master/#resource-management)
  * [Debugging](https://github.com/nkwa/pay-python/blob/master/#debugging)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with either *pip* or *poetry* package managers.

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install nkwa-pay-sdk
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add nkwa-pay-sdk
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from nkwa-pay-sdk python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "nkwa-pay-sdk",
# ]
# ///

from nkwa_pay_sdk import Pay

sdk = Pay(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
from nkwa_pay_sdk import Pay
import os


with Pay(
    api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
) as pay:

    res = pay.payments.get(id="96e9ed79-9fef-44a6-9435-0625338ca86a")

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from nkwa_pay_sdk import Pay
import os

async def main():

    async with Pay(
        api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
    ) as pay:

        res = await pay.payments.get_async(id="96e9ed79-9fef-44a6-9435-0625338ca86a")

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name           | Type   | Scheme  | Environment Variable |
| -------------- | ------ | ------- | -------------------- |
| `api_key_auth` | apiKey | API key | `PAY_API_KEY_AUTH`   |

To authenticate with the API the `api_key_auth` parameter must be set when initializing the SDK client instance. For example:
```python
from nkwa_pay_sdk import Pay
import os


with Pay(
    api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
) as pay:

    res = pay.payments.get(id="96e9ed79-9fef-44a6-9435-0625338ca86a")

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>


### [payments](https://github.com/nkwa/pay-python/blob/master/docs/sdks/payments/README.md)

* [get](https://github.com/nkwa/pay-python/blob/master/docs/sdks/payments/README.md#get) - Get the payment (collection or disbursement) with the specified ID.
* [collect](https://github.com/nkwa/pay-python/blob/master/docs/sdks/payments/README.md#collect) - Collect a payment from a phone number.
* [disburse](https://github.com/nkwa/pay-python/blob/master/docs/sdks/payments/README.md#disburse) - Disburse a payment from your balance to a phone number.

### [service](https://github.com/nkwa/pay-python/blob/master/docs/sdks/service/README.md)

* [availability](https://github.com/nkwa/pay-python/blob/master/docs/sdks/service/README.md#availability) - Check which operators and operations are currently available.

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from nkwa_pay_sdk import Pay
from nkwa_pay_sdk.utils import BackoffStrategy, RetryConfig
import os


with Pay(
    api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
) as pay:

    res = pay.payments.get(id="96e9ed79-9fef-44a6-9435-0625338ca86a",
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from nkwa_pay_sdk import Pay
from nkwa_pay_sdk.utils import BackoffStrategy, RetryConfig
import os


with Pay(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
) as pay:

    res = pay.payments.get(id="96e9ed79-9fef-44a6-9435-0625338ca86a")

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations. All operations return a response object or raise an exception.

By default, an API error will raise a models.APIError exception, which has the following properties:

| Property        | Type             | Description           |
|-----------------|------------------|-----------------------|
| `.status_code`  | *int*            | The HTTP status code  |
| `.message`      | *str*            | The error message     |
| `.raw_response` | *httpx.Response* | The raw HTTP response |
| `.body`         | *str*            | The response content  |

When custom error responses are specified for an operation, the SDK may also raise their associated exceptions. You can refer to respective *Errors* tables in SDK docs for more details on possible exception types for each operation. For example, the `get_async` method may raise the following exceptions:

| Error Type       | Status Code | Content Type     |
| ---------------- | ----------- | ---------------- |
| models.HTTPError | 401, 404    | application/json |
| models.HTTPError | 500         | application/json |
| models.APIError  | 4XX, 5XX    | \*/\*            |

### Example

```python
from nkwa_pay_sdk import Pay, models
import os


with Pay(
    api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
) as pay:
    res = None
    try:

        res = pay.payments.get(id="96e9ed79-9fef-44a6-9435-0625338ca86a")

        # Handle response
        print(res)

    except models.HTTPError as e:
        # handle e.data: models.HTTPErrorData
        raise(e)
    except models.HTTPError as e:
        # handle e.data: models.HTTPErrorData
        raise(e)
    except models.APIError as e:
        # handle exception
        raise(e)
```
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from nkwa_pay_sdk import Pay
import os


with Pay(
    server_url="https://api.pay.staging.mynkwa.com",
    api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
) as pay:

    res = pay.payments.get(id="96e9ed79-9fef-44a6-9435-0625338ca86a")

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from nkwa_pay_sdk import Pay
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = Pay(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from nkwa_pay_sdk import Pay
from nkwa_pay_sdk.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = Pay(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `Pay` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from nkwa_pay_sdk import Pay
import os
def main():

    with Pay(
        api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
    ) as pay:
        # Rest of application here...


# Or when using async:
async def amain():

    async with Pay(
        api_key_auth=os.getenv("PAY_API_KEY_AUTH", ""),
    ) as pay:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from nkwa_pay_sdk import Pay
import logging

logging.basicConfig(level=logging.DEBUG)
s = Pay(debug_logger=logging.getLogger("nkwa_pay_sdk"))
```

You can also enable a default debug logger by setting an environment variable `PAY_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->
