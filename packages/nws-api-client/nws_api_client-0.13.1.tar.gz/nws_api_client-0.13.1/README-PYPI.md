# nws-api-client

Type-safe and developer-friendly Python client for the National Weather Service API.

> [!INFO]
> The first pass was built with Speakeasy, and I've been making some major quality-of-life adjustments.

> [!NOTE]
> The National Weather Service would like to know who is using their API. Please include a user agent with all API requests where value = your company name and email (a contactable email address). This is the same as the HTTP header 'User-Agent'. They'd also like to be able to contact you if there's an issue with your use of the API.

<!-- Start Summary [summary] -->
## Summary

MODIFIED National Weather Service weather.gov API: OpenAPI Client SDK for National Weather Service API (NWS / weather.gov)

For more information about the API: [Full API documentation](https://www.weather.gov/documentation/services-web-api)
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [nws-api-client](https://github.com/spdustin/nws-api-client-python/blob/master/#nws-api-client)
  * [SDK Installation](https://github.com/spdustin/nws-api-client-python/blob/master/#sdk-installation)
  * [SDK Example Usage](https://github.com/spdustin/nws-api-client-python/blob/master/#sdk-example-usage)
  * [Available Resources and Operations](https://github.com/spdustin/nws-api-client-python/blob/master/#available-resources-and-operations)
  * [Global Parameters](https://github.com/spdustin/nws-api-client-python/blob/master/#global-parameters)
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

### Text Products

Get your local NWS office's Area Forecast Discussion

```python
# Synchronous Example
from nws_api_client import NwsAPIClient
import os


with NwsAPIClient(
    user_agent=os.getenv("NWS_API_CLIENT_USER_AGENT", ""),
) as nac_client:

    res = nac_client.products.get_available(type_id="AFD", location_id="LOT")

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from nws_api_client import NwsAPIClient
import os

async def main():

    async with NwsAPIClient(
        user_agent=os.getenv("NWS_API_CLIENT_USER_AGENT", ""),
    ) as nac_client:

        res = await nac_client.products.get_available_async(type_id="AFD", location_id="LOT")

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
* [get_active](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_active) - Returns filtered (or all) currently active alerts
* [get_active_by_region](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_active_by_region) - Returns active alerts for the given marine region
* [get_active_count](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_active_count) - Returns info on the number of active alerts
* [get_active_for_zone](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_active_for_zone) - Returns active alerts for the given NWS public zone/county identifier
* [get_aviation_cwa](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_aviation_cwa) - Returns a list of CWAs from a CWSU for a specific date and sequence
* [get_aviation_sigmet](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_aviation_sigmet) - Returns a specific SIGMET/AIRMET
* [get_aviation_sigmets_by_atsu_for_date](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_aviation_sigmets_by_atsu_for_date) - Returns a list of SIGMET/AIRMETs for the specified ATSU for the specified date
* [get_center_weather_advisories](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_center_weather_advisories) - Returns a list of Center Weather Advisories from a CWSU
* [get_sigmets_by_atsu](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#get_sigmets_by_atsu) - Returns a list of SIGMET/AIRMETs for the specified ATSU
* [list_active_for_area](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_active_for_area) - Returns active alerts for the given state or marine area
* [list_sigmets](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_sigmets) - Returns a list of SIGMET/AIRMETs
* [list_types](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/alerts/README.md#list_types) - Returns a list of alert types

### [aviation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md)

* [get_aviation_cwa](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_aviation_cwa) - Returns a list of CWAs from a CWSU for a specific date and sequence
* [get_aviation_sigmet](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_aviation_sigmet) - Returns a specific SIGMET/AIRMET
* [get_aviation_sigmets_by_atsu_for_date](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_aviation_sigmets_by_atsu_for_date) - Returns a list of SIGMET/AIRMETs for the specified ATSU for the specified date
* [get_center_weather_advisories](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_center_weather_advisories) - Returns a list of Center Weather Advisories from a CWSU
* [get_cwsu](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_cwsu) - Returns metadata about a Center Weather Service Unit
* [get_sigmets_by_atsu](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_sigmets_by_atsu) - Returns a list of SIGMET/AIRMETs for the specified ATSU
* [get_taf](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_taf) - Returns a single Terminal Aerodrome Forecast
* [get_tafs](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#get_tafs) - Returns Terminal Aerodrome Forecasts for the specified airport station.
* [list_sigmets](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/aviation/README.md#list_sigmets) - Returns a list of SIGMET/AIRMETs

### [conditions](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/conditions/README.md)

* [get_latest_observation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/conditions/README.md#get_latest_observation) - Returns the latest observation for a station
* [get_observation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/conditions/README.md#get_observation) - Returns a single observation
* [list_zone_observations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/conditions/README.md#list_zone_observations) - Returns a list of observations for a given zone

### [forecasts](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md)

* [get](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md#get) - Returns a textual forecast for a 2.5km grid area
* [get_hourly](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md#get_hourly) - Returns a textual hourly forecast for a 2.5km grid area
* [get_raw](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md#get_raw) - Returns raw numerical forecast data for a 2.5km grid area
* [get_taf](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md#get_taf) - Returns a single Terminal Aerodrome Forecast
* [get_tafs](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md#get_tafs) - Returns Terminal Aerodrome Forecasts for the specified airport station.
* [get_zone_forecast](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/forecasts/README.md#get_zone_forecast) - Returns the current zone forecast for a given zone

### [geographic](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md)

* [get](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get) - Returns a textual forecast for a 2.5km grid area
* [get_active](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_active) - Returns filtered (or all) currently active alerts
* [get_active_by_region](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_active_by_region) - Returns active alerts for the given marine region
* [get_active_for_zone](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_active_for_zone) - Returns active alerts for the given NWS public zone/county identifier
* [get_cwsu](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_cwsu) - Returns metadata about a Center Weather Service Unit
* [get_hourly](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_hourly) - Returns a textual hourly forecast for a 2.5km grid area
* [get_latest_observation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_latest_observation) - Returns the latest observation for a station
* [get_observation](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_observation) - Returns a single observation
* [get_office](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_office) - Returns metadata about a NWS forecast office
* [get_point_info](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_point_info) - Returns metadata (inc. forecast gridpoint) about a given lat,long pair
* [get_raw](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_raw) - Returns raw numerical forecast data for a 2.5km grid area
* [get_zone](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_zone) - Returns metadata about a given zone
* [get_zone_forecast](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_zone_forecast) - Returns the current zone forecast for a given zone
* [get_zone_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_zone_stations) - Returns a list of observation stations for a given zone
* [get_zones_by_type](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#get_zones_by_type) - Returns a list of zones of a given type
* [list_active_for_area](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#list_active_for_area) - Returns active alerts for the given state or marine area
* [list_gridpoint_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#list_gridpoint_stations) - Returns a list of observation stations usable for a given 2.5km grid area
* [list_observation_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#list_observation_stations) - Returns a list of observation stations.
* [list_zone_observations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#list_zone_observations) - Returns a list of observations for a given zone
* [list_zones](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/geographic/README.md#list_zones) - Returns a list of zones

### [metadata](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md)

* [get_office](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_office) - Returns metadata about a NWS forecast office
* [get_point_info](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_point_info) - Returns metadata (inc. forecast gridpoint) about a given lat,long pair
* [get_profiler](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_profiler) - Returns metadata about a given radar wind profiler
* [get_queue](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_queue) - Returns metadata about a given radar queue
* [get_radar_station](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_radar_station) - Returns metadata about a given radar station
* [get_server](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_server) - Returns metadata about a given radar server
* [get_station_alarms](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_station_alarms) - Returns metadata about a given radar station alarms
* [get_zone](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_zone) - Returns metadata about a given zone
* [get_zone_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#get_zone_stations) - Returns a list of observation stations for a given zone
* [list_observation_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#list_observation_stations) - Returns a list of observation stations.
* [list_servers](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#list_servers) - Returns a list of radar servers
* [list_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/metadata/README.md#list_stations) - Returns a list of radar stations


### [products](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md)

* [get](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#get) - Returns a specific text product
* [get_available](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#get_available) - Returns a list of text products of a given type for a given issuance location
* [get_office_headline](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#get_office_headline) - Returns a specific news headline for a given NWS office
* [list_by_type](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_by_type) - Returns a list of text products of a given type
* [list_glossary_terms](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_glossary_terms) - List glossary terms
* [list_issuing_locations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_issuing_locations) - Returns a list of valid text product issuance locations
* [list_locations_by_type](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_locations_by_type) - Returns a list of valid text product issuance locations for a given product type
* [list_office_headlines](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_office_headlines) - Returns a list of news headlines for a given NWS office
* [list_products](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_products) - Returns a list of text products
* [list_types](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_types) - Returns a list of valid text product types and codes
* [list_types_by_location](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/products/README.md#list_types_by_location) - Returns a list of valid text product types for a given issuance location

### [radar](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md)

* [get_profiler](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_profiler) - Returns metadata about a given radar wind profiler
* [get_queue](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_queue) - Returns metadata about a given radar queue
* [get_radar_station](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_radar_station) - Returns metadata about a given radar station
* [get_server](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_server) - Returns metadata about a given radar server
* [get_station_alarms](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#get_station_alarms) - Returns metadata about a given radar station alarms
* [list_servers](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#list_servers) - Returns a list of radar servers
* [list_stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/radar/README.md#list_stations) - Returns a list of radar stations

### [stations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/stations/README.md)

* [get_observations](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/stations/README.md#get_observations) - Returns a list of observations for a given station
* [get_station](https://github.com/spdustin/nws-api-client-python/blob/master/docs/sdks/stations/README.md#get_station) - Returns metadata about a given observation station

</details>
<!-- End Available Resources and Operations [operations] -->


<!-- No Retries [retries] -->

<!-- Start Global Parameters [global-parameters] -->
## Global Parameters

A parameter is configured globally. This parameter may be set on the SDK client instance itself during initialization. When configured as an option during SDK initialization, This global value will be used as the default on the operations that use it. When such operations are called, there is a place in each to override the global value, if needed.

For example, you can set `officeId` to `components.NWSOfficeID.MSO` at SDK initialization and then you do not have to pass the same value on calls to operations like `get_office`. But if you want to do so you may, which will locally override the global setting. See the example code below for a demonstration.


### Available Globals

The following global parameter is available.
Global parameters can also be set via environment variable.

| Name      | Type                   | Description   | Environment              |
| --------- | ---------------------- | ------------- | ------------------------ |
| office_id | components.NWSOfficeID | NWS office ID | NWS_API_CLIENT_OFFICE_ID |

### Example

```python
from nws_api_client import NwsAPIClient
from nws_api_client.models import components
import os


with NwsAPIClient(
    user_agent=os.getenv("NWS_API_CLIENT_USER_AGENT", ""),
) as nac_client:

    res = nac_client.geographic.get_office(office_id=components.NWSOfficeID.GGW)

    # Handle response
    print(res)

```
<!-- End Global Parameters [global-parameters] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations. All operations return a response object or raise an exception.

By default, an API error will raise a errors.NWSAPIError exception, which has the following properties:

| Property        | Type             | Description           |
|-----------------|------------------|-----------------------|
| `.status_code`  | *int*            | The HTTP status code  |
| `.message`      | *str*            | The error message     |
| `.raw_response` | *httpx.Response* | The raw HTTP response |
| `.body`         | *str*            | The response content  |

When custom error responses are specified for an operation, the SDK may also raise their associated exceptions. You can refer to respective *Errors* tables in SDK docs for more details on possible exception types for each operation. For example, the `get_async` method may raise the following exceptions:

| Error Type                | Status Code | Content Type             |
| ------------------------- | ----------- | ------------------------ |
| errors.ProblemDetailError | 400         | application/problem+json |
| errors.NWSAPIError        | 4XX, 5XX    | \*/\*                    |

### Example

```python
from nws_api_client import NwsAPIClient
from nws_api_client.models import errors
import os


with NwsAPIClient(
    user_agent=os.getenv("NWS_API_CLIENT_USER_AGENT", ""),
) as nac_client:
    res = None
    try:

        res = nac_client.alerts.get(id="urn:oid:2.49.0.1.840.0.404b3149af6da23b497bb9705fadc6ead564a967.005.1")

        # Handle response
        print(res)

    except errors.ProblemDetailError as e:
        # handle e.data: errors.ProblemDetailErrorData
        raise(e)
    except errors.NWSAPIError as e:
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
from nws_api_client import NwsAPIClient
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = NwsAPIClient(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from nws_api_client import NwsAPIClient
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

s = NwsAPIClient(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `NwsAPIClient` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from nws_api_client import NwsAPIClient
import os
def main():

    with NwsAPIClient(
        user_agent=os.getenv("NWS_API_CLIENT_USER_AGENT", ""),
    ) as nac_client:
        # Rest of application here...


# Or when using async:
async def amain():

    async with NwsAPIClient(
        user_agent=os.getenv("NWS_API_CLIENT_USER_AGENT", ""),
    ) as nac_client:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from nws_api_client import NwsAPIClient
import logging

logging.basicConfig(level=logging.DEBUG)
s = NwsAPIClient(debug_logger=logging.getLogger("nws_api_client"))
```

You can also enable a default debug logger by setting an environment variable `NWS_API_CLIENT_DEBUG` to true.
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
