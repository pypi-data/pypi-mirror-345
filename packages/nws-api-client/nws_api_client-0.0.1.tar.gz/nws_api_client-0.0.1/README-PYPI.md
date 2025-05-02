# nws-client

Developer-friendly & type-safe Python SDK specifically catered to leverage *nws-client* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=nws-client&utm_campaign=python"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<!-- Start Summary [summary] -->
## Summary

weather.gov API: weather.gov API

For more information about the API: [Full API documentation](https://www.weather.gov/documentation/services-web-api)
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [nws-client](#nws-client)
  * [SDK Installation](#sdk-installation)
  * [IDE Support](#ide-support)
  * [SDK Example Usage](#sdk-example-usage)
  * [Authentication](#authentication)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [Retries](#retries)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Custom HTTP Client](#custom-http-client)
  * [Resource Management](#resource-management)
  * [Debugging](#debugging)
* [Development](#development)
  * [Maturity](#maturity)
  * [Contributions](#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!TIP]
> To finish publishing your SDK to PyPI you must [run your first generation action](https://www.speakeasy.com/docs/github-setup#step-by-step-guide).


> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with either *pip* or *poetry* package managers.

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install git+<UNSET>.git
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add git+<UNSET>.git
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from nws-api-client python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "nws-api-client",
# ]
# ///

from nws_api_client import NwsClient

sdk = NwsClient(
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
from nws_api_client import NwsClient
import os


with NwsClient(
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:

    res = nws_client.alerts_query()

    assert res is not None

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from nws_api_client import NwsClient
import os

async def main():

    async with NwsClient(
        user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
    ) as nws_client:

        res = await nws_client.alerts_query_async()

        assert res is not None

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name         | Type   | Scheme  | Environment Variable   |
| ------------ | ------ | ------- | ---------------------- |
| `user_agent` | apiKey | API key | `NWSCLIENT_USER_AGENT` |

To authenticate with the API the `user_agent` parameter must be set when initializing the SDK client instance. For example:
```python
from nws_api_client import NwsClient
import os


with NwsClient(
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:

    res = nws_client.alerts_query()

    assert res is not None

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [NwsClient SDK](docs/sdks/nwsclient/README.md)

* [alerts_query](docs/sdks/nwsclient/README.md#alerts_query) - Returns all alerts
* [alerts_active](docs/sdks/nwsclient/README.md#alerts_active) - Returns all currently active alerts
* [alerts_active_count](docs/sdks/nwsclient/README.md#alerts_active_count) - Returns info on the number of active alerts
* [alerts_active_zone](docs/sdks/nwsclient/README.md#alerts_active_zone) - Returns active alerts for the given NWS public zone or county
* [alerts_active_area](docs/sdks/nwsclient/README.md#alerts_active_area) - Returns active alerts for the given area (state or marine area)
* [alerts_active_region](docs/sdks/nwsclient/README.md#alerts_active_region) - Returns active alerts for the given marine region
* [alerts_types](docs/sdks/nwsclient/README.md#alerts_types) - Returns a list of alert types
* [alerts_single](docs/sdks/nwsclient/README.md#alerts_single) - Returns a specific alert
* [cwsu](docs/sdks/nwsclient/README.md#cwsu) - Returns metadata about a Center Weather Service Unit
* [cwas](docs/sdks/nwsclient/README.md#cwas) - Returns a list of Center Weather Advisories from a CWSU
* [cwa](docs/sdks/nwsclient/README.md#cwa) - Returns a list of Center Weather Advisories from a CWSU
* [sigmet_query](docs/sdks/nwsclient/README.md#sigmet_query) - Returns a list of SIGMET/AIRMETs
* [sigmets_by_atsu](docs/sdks/nwsclient/README.md#sigmets_by_atsu) - Returns a list of SIGMET/AIRMETs for the specified ATSU
* [sigmets_by_atsu_by_date](docs/sdks/nwsclient/README.md#sigmets_by_atsu_by_date) - Returns a list of SIGMET/AIRMETs for the specified ATSU for the specified date
* [sigmet](docs/sdks/nwsclient/README.md#sigmet) - Returns a specific SIGMET/AIRMET
* [glossary](docs/sdks/nwsclient/README.md#glossary) - Returns glossary terms
* [gridpoint](docs/sdks/nwsclient/README.md#gridpoint) - Returns raw numerical forecast data for a 2.5km grid area
* [gridpoint_forecast](docs/sdks/nwsclient/README.md#gridpoint_forecast) - Returns a textual forecast for a 2.5km grid area
* [gridpoint_forecast_hourly](docs/sdks/nwsclient/README.md#gridpoint_forecast_hourly) - Returns a textual hourly forecast for a 2.5km grid area
* [gridpoint_stations](docs/sdks/nwsclient/README.md#gridpoint_stations) - Returns a list of observation stations usable for a given 2.5km grid area
* [station_observation_list](docs/sdks/nwsclient/README.md#station_observation_list) - Returns a list of observations for a given station
* [station_observation_latest](docs/sdks/nwsclient/README.md#station_observation_latest) - Returns the latest observation for a station
* [station_observation_time](docs/sdks/nwsclient/README.md#station_observation_time) - Returns a single observation.
* [tafs](docs/sdks/nwsclient/README.md#tafs) - Returns Terminal Aerodrome Forecasts for the specified airport station.
* [taf](docs/sdks/nwsclient/README.md#taf) - Returns a single Terminal Aerodrome Forecast.
* [obs_stations](docs/sdks/nwsclient/README.md#obs_stations) - Returns a list of observation stations.
* [obs_station](docs/sdks/nwsclient/README.md#obs_station) - Returns metadata about a given observation station
* [office](docs/sdks/nwsclient/README.md#office) - Returns metadata about a NWS forecast office
* [office_headline](docs/sdks/nwsclient/README.md#office_headline) - Returns a specific news headline for a given NWS office
* [office_headlines](docs/sdks/nwsclient/README.md#office_headlines) - Returns a list of news headlines for a given NWS office
* [point](docs/sdks/nwsclient/README.md#point) - Returns metadata about a given latitude/longitude point
* [radar_servers](docs/sdks/nwsclient/README.md#radar_servers) - Returns a list of radar servers
* [radar_server](docs/sdks/nwsclient/README.md#radar_server) - Returns metadata about a given radar server
* [radar_stations](docs/sdks/nwsclient/README.md#radar_stations) - Returns a list of radar stations
* [radar_station](docs/sdks/nwsclient/README.md#radar_station) - Returns metadata about a given radar station
* [radar_station_alarms](docs/sdks/nwsclient/README.md#radar_station_alarms) - Returns metadata about a given radar station alarms
* [radar_queue](docs/sdks/nwsclient/README.md#radar_queue) - Returns metadata about a given radar queue
* [radar_profiler](docs/sdks/nwsclient/README.md#radar_profiler) - Returns metadata about a given radar wind profiler
* [products_query](docs/sdks/nwsclient/README.md#products_query) - Returns a list of text products
* [product_locations](docs/sdks/nwsclient/README.md#product_locations) - Returns a list of valid text product issuance locations
* [product_types](docs/sdks/nwsclient/README.md#product_types) - Returns a list of valid text product types and codes
* [product](docs/sdks/nwsclient/README.md#product) - Returns a specific text product
* [products_type](docs/sdks/nwsclient/README.md#products_type) - Returns a list of text products of a given type
* [products_type_locations](docs/sdks/nwsclient/README.md#products_type_locations) - Returns a list of valid text product issuance locations for a given product type
* [location_products](docs/sdks/nwsclient/README.md#location_products) - Returns a list of valid text product types for a given issuance location
* [products_type_location](docs/sdks/nwsclient/README.md#products_type_location) - Returns a list of text products of a given type for a given issuance location
* [zone_list](docs/sdks/nwsclient/README.md#zone_list) - Returns a list of zones
* [zone_list_type](docs/sdks/nwsclient/README.md#zone_list_type) - Returns a list of zones of a given type
* [zone](docs/sdks/nwsclient/README.md#zone) - Returns metadata about a given zone
* [zone_forecast](docs/sdks/nwsclient/README.md#zone_forecast) - Returns the current zone forecast for a given zone
* [zone_obs](docs/sdks/nwsclient/README.md#zone_obs) - Returns a list of observations for a given zone
* [zone_stations](docs/sdks/nwsclient/README.md#zone_stations) - Returns a list of observation stations for a given zone

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from nws_api_client import NwsClient
from nws_api_client.utils import BackoffStrategy, RetryConfig
import os


with NwsClient(
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:

    res = nws_client.alerts_query(,
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    assert res is not None

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from nws_api_client import NwsClient
from nws_api_client.utils import BackoffStrategy, RetryConfig
import os


with NwsClient(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:

    res = nws_client.alerts_query()

    assert res is not None

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations. All operations return a response object or raise an exception.

By default, an API error will raise a errors.APIError exception, which has the following properties:

| Property        | Type             | Description           |
|-----------------|------------------|-----------------------|
| `.status_code`  | *int*            | The HTTP status code  |
| `.message`      | *str*            | The error message     |
| `.raw_response` | *httpx.Response* | The raw HTTP response |
| `.body`         | *str*            | The response content  |

When custom error responses are specified for an operation, the SDK may also raise their associated exceptions. You can refer to respective *Errors* tables in SDK docs for more details on possible exception types for each operation. For example, the `alerts_query_async` method may raise the following exceptions:

| Error Type      | Status Code | Content Type |
| --------------- | ----------- | ------------ |
| errors.APIError | 4XX, 5XX    | \*/\*        |

### Example

```python
from nws_api_client import NwsClient, errors
import os


with NwsClient(
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:
    res = None
    try:

        res = nws_client.alerts_query()

        assert res is not None

        # Handle response
        print(res)

    except errors.APIError as e:
        # handle exception
        raise(e)
```
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from nws_api_client import NwsClient
import os


with NwsClient(
    server_url="https://api.weather.gov",
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:

    res = nws_client.alerts_query()

    assert res is not None

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
from nws_api_client import NwsClient
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = NwsClient(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from nws_api_client import NwsClient
from nws_api_client.httpclient import AsyncHttpClient
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

s = NwsClient(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `NwsClient` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from nws_api_client import NwsClient
import os
def main():

    with NwsClient(
        user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
    ) as nws_client:
        # Rest of application here...


# Or when using async:
async def amain():

    async with NwsClient(
        user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
    ) as nws_client:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from nws_api_client import NwsClient
import logging

logging.basicConfig(level=logging.DEBUG)
s = NwsClient(debug_logger=logging.getLogger("nws_api_client"))
```

You can also enable a default debug logger by setting an environment variable `NWSCLIENT_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=nws-client&utm_campaign=python)
