# nws-api-client

Type-safe and developer-friendly Python client for the National Weather Service API.

> [!INFO]
> The first pass was built with Speakeasy, and I've been making some major quality-of-life adjustments.

> [!NOTE]
> The National Weather Service would like to know who is using their API. Please include a user agent with all API requests where value = your company name and email (a contactable email address). This is the same as the HTTP header 'User-Agent'. They'd also like to be able to contact you if there's an issue with your use of the API.

<!-- Start Summary [summary] -->
## Summary

weather.gov API: OpenAPI Client SDK for National Weather Service API (NWS / weather.gov)

For more information about the API: [Full API documentation](https://www.weather.gov/documentation/services-web-api)
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [nws-api-client](https://github.com/spdustin/nws-api-client-python/blob/master/#nws-api-client)
  * [SDK Installation](https://github.com/spdustin/nws-api-client-python/blob/master/#sdk-installation)
  * [SDK Example Usage](https://github.com/spdustin/nws-api-client-python/blob/master/#sdk-example-usage)
  * [Available Resources and Operations](https://github.com/spdustin/nws-api-client-python/blob/master/#available-resources-and-operations)
  * [Error Handling](https://github.com/spdustin/nws-api-client-python/blob/master/#error-handling)
  * [Custom HTTP Client](https://github.com/spdustin/nws-api-client-python/blob/master/#custom-http-client)
  * [Resource Management](https://github.com/spdustin/nws-api-client-python/blob/master/#resource-management)
  * [Debugging](https://github.com/spdustin/nws-api-client-python/blob/master/#debugging)
* [Development](https://github.com/spdustin/nws-api-client-python/blob/master/#development)
  * [Maturity](https://github.com/spdustin/nws-api-client-python/blob/master/#maturity)
  * [Contributions](https://github.com/spdustin/nws-api-client-python/blob/master/#contributions)

<!-- End Table of Contents [toc] -->


## SDK Installation

### uv

[uv](https://docs.astral.sh/uv/) is the Python package manager I use and recommend.

```bash
uv add nws-api-client
```

### PIP

```bash
pip install nws-api-client
```

### Poetry

```bash
poetry add nws-api-client
```
<!-- No SDK Installation [installation] -->
<!-- No IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Get Locations for a Text Product Type

Get a list of locations that issue a particular forecast text product (like "AFD" for "Area Forecast Discussion")

```python
# Synchronous Example
from nws_api_client import NwsClient
import os


with NwsClient(
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:

    res = nws_client.products.get_locations_by_type(type_id="AFD")

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

        res = await nws_client.products.get_locations_by_type_async(type_id="AFD")

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->


<!-- No Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [alerts](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md)

* [get](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get) - Returns a specific alert
* [list_active](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_active) - Returns all currently active alerts
* [list_active_by_area](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_active_by_area) - Returns active alerts for the given area (state or marine area)
* [list_active_by_region](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_active_by_region) - Returns active alerts for the given marine region
* [list_active_by_zone](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_active_by_zone) - Returns active alerts for the given NWS public zone or county
* [list_active_count](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_active_count) - Returns info on the number of active alerts
* [list_types](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_types) - Returns a list of alert types

### [aviation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md)

* [get_cwsu](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_cwsu) - Returns metadata about a Center Weather Service Unit
* [get_sigmet](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_sigmet) - Returns a specific SIGMET/AIRMET
* [get_sigmets](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_sigmets) - Returns a list of SIGMET/AIRMETs
* [list_cwas](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#list_cwas) - Returns a list of Center Weather Advisories from a CWSU
* [list_cwas_by_date_and_sequence](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#list_cwas_by_date_and_sequence) - Returns a list of Center Weather Advisories from a CWSU
* [list_sigmets](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#list_sigmets) - Returns a list of SIGMET/AIRMETs for the specified ATSU
* [list_sigmets_by_atsu_and_date](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#list_sigmets_by_atsu_and_date) - Returns a list of SIGMET/AIRMETs for the specified ATSU for the specified date

### [glossary](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/glossarysdk/README.md)

* [list_terms](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/glossarysdk/README.md#list_terms) - Returns glossary terms

### [gridpoints](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/gridpoints/README.md)

* [get_forecast](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/gridpoints/README.md#get_forecast) - Returns a textual forecast for a 2.5km grid area
* [get_hourly_forecast](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/gridpoints/README.md#get_hourly_forecast) - Returns a textual hourly forecast for a 2.5km grid area
* [get_raw_forecast](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/gridpoints/README.md#get_raw_forecast) - Returns raw numerical forecast data for a 2.5km grid area
* [list_observation_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/gridpoints/README.md#list_observation_stations) - Returns a list of observation stations usable for a given 2.5km grid area


### [observations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observations/README.md)

* [list_by_station](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observations/README.md#list_by_station) - Returns a list of observations for a given station

### [observationstations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md)

* [get_by_station](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md#get_by_station) - Returns a single observation.
* [get_latest_observation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md#get_latest_observation) - Returns the latest observation for a station
* [get_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md#get_metadata) - Returns metadata about a given observation station
* [get_taf](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md#get_taf) - Returns a single Terminal Aerodrome Forecast.
* [list](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md#list) - Returns a list of observation stations.
* [list_tafs](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/observationstations/README.md#list_tafs) - Returns Terminal Aerodrome Forecasts for the specified airport station.

### [offices](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/offices/README.md)

* [get_headline](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/offices/README.md#get_headline) - Returns a specific news headline for a given NWS office
* [get_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/offices/README.md#get_metadata) - Returns metadata about a NWS forecast office
* [list_headlines](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/offices/README.md#list_headlines) - Returns a list of news headlines for a given NWS office

### [points](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/points/README.md)

* [get_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/points/README.md#get_metadata) - Returns metadata about a given latitude/longitude point

### [products](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md)

* [get_by_id](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#get_by_id) - Returns a specific text product
* [get_locations_by_type](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#get_locations_by_type) - Returns a list of valid text product issuance locations for a given product type
* [list](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list) - Returns a list of text products
* [list_by_type](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_by_type) - Returns a list of text products of a given type
* [list_by_type_and_location](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_by_type_and_location) - Returns a list of text products of a given type for a given issuance location
* [list_locations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_locations) - Returns a list of valid text product issuance locations
* [list_types](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_types) - Returns a list of valid text product types and codes
* [list_types_by_location](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_types_by_location) - Returns a list of valid text product types for a given issuance location

### [radar](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md)

* [get_queue_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_queue_metadata) - Returns metadata about a given radar queue
* [get_server_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_server_metadata) - Returns metadata about a given radar server
* [get_station_alarms_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_station_alarms_metadata) - Returns metadata about a given radar station alarms
* [get_station_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_station_metadata) - Returns metadata about a given radar station
* [get_wind_profiler_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_wind_profiler_metadata) - Returns metadata about a given radar wind profiler
* [list_servers](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#list_servers) - Returns a list of radar servers
* [list_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#list_stations) - Returns a list of radar stations

### [zones](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md)

* [get_forecast](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md#get_forecast) - Returns the current zone forecast for a given zone
* [get_metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md#get_metadata) - Returns metadata about a given zone
* [list](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md#list) - Returns a list of zones
* [list_by_type](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md#list_by_type) - Returns a list of zones of a given type
* [list_observations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md#list_observations) - Returns a list of observations for a given zone
* [list_stations_by_zone](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/zones/README.md#list_stations_by_zone) - Returns a list of observation stations for a given zone

</details>
<!-- End Available Resources and Operations [operations] -->


<!-- No Retries [retries] -->

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

When custom error responses are specified for an operation, the SDK may also raise their associated exceptions. You can refer to respective *Errors* tables in SDK docs for more details on possible exception types for each operation. For example, the `get_async` method may raise the following exceptions:

| Error Type                 | Status Code                  | Content Type     |
| -------------------------- | ---------------------------- | ---------------- |
| errors.NotFoundError       | 404                          | application/json |
| errors.UnauthorizedError   | 401, 403, 407                | application/json |
| errors.TimeoutErrorT       | 408                          | application/json |
| errors.RateLimitedError    | 429                          | application/json |
| errors.BadRequestError     | 400, 413, 414, 415, 422, 431 | application/json |
| errors.TimeoutErrorT       | 504                          | application/json |
| errors.NotFoundError       | 501, 505                     | application/json |
| errors.InternalServerError | 500, 502, 503, 506, 507, 508 | application/json |
| errors.BadRequestError     | 510                          | application/json |
| errors.UnauthorizedError   | 511                          | application/json |
| errors.APIError            | 4XX, 5XX                     | \*/\*            |

### Example

```python
from nws_api_client import NwsClient, errors
import os


with NwsClient(
    user_agent=os.getenv("NWSCLIENT_USER_AGENT", ""),
) as nws_client:
    res = None
    try:

        res = nws_client.alerts.get(id="<id>")

        # Handle response
        print(res)

    except errors.NotFoundError as e:
        # handle e.data: errors.NotFoundErrorData
        raise(e)
    except errors.UnauthorizedError as e:
        # handle e.data: errors.UnauthorizedErrorData
        raise(e)
    except errors.TimeoutErrorT as e:
        # handle e.data: errors.TimeoutErrorTData
        raise(e)
    except errors.RateLimitedError as e:
        # handle e.data: errors.RateLimitedErrorData
        raise(e)
    except errors.BadRequestError as e:
        # handle e.data: errors.BadRequestErrorData
        raise(e)
    except errors.TimeoutErrorT as e:
        # handle e.data: errors.TimeoutErrorTData
        raise(e)
    except errors.NotFoundError as e:
        # handle e.data: errors.NotFoundErrorData
        raise(e)
    except errors.InternalServerError as e:
        # handle e.data: errors.InternalServerErrorData
        raise(e)
    except errors.BadRequestError as e:
        # handle e.data: errors.BadRequestErrorData
        raise(e)
    except errors.UnauthorizedError as e:
        # handle e.data: errors.UnauthorizedErrorData
        raise(e)
    except errors.APIError as e:
        # handle exception
        raise(e)
```
<!-- End Error Handling [errors] -->

<!-- No Server Selection [server] -->

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

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, I recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While I value open-source contributions to this SDK, this library is *currently* generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### Initial SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=nws-api-client&utm_campaign=python)
