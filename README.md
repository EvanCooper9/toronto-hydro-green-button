# toronto-hydro-green-button

Export [Green Button](https://green-button.github.io/) ([ESPI](https://www.naesb.org//ESPI_Standards.asp)) energy usage data from your [Toronto Hydro](https://torontohydro.com/) account.

Toronto Hydro offers a Green Button XML export through the customer portal, but does not offer programmatic API access.
This script logs into the dashboard with [Selenium](https://selenium.dev/), then downloads the report with [Requests](https://2.python-requests.org/en/master/).

## Requirements

* a [Toronto Hydro](https://torontohydro.com/) account
* Python 3.6+
* Firefox 57+ or Google Chrome and ChromeDriver

## Installation

Install with pip:

```
pip install toronto-hydro-green-button
```

## Usage

The script takes the following arguments:
- `username`
- `password`
- `account-id`
- `sp-id`

Username & password are self-explanatory. Account ID and Service Provider ID (SP ID) can be retrieved by using your browser tools to inspect the POST request body of `https://www.torontohydro.com/my-account/green-button-data` when manually downloading your usage data [here](https://www.torontohydro.com/my-account/green-button-data).

```
usage: toronto-hydro-green-button [-h] [--version] [--username USERNAME] [--password PASSWORD] [--account-id ACCOUNT_ID] [--sp-id SP_ID] [--start-date START_DATE] [--end-date END_DATE] [--browser {firefox,chrome}] [--output OUTPUT]

Export Green Button (ESPI) energy usage data from your Toronto Hydro account.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --username USERNAME, -u USERNAME
                        Toronto Hydro username. Will prompt if not set. [TORONTO_HYDRO_USERNAME]
  --password PASSWORD, -p PASSWORD
                        Toronto Hydro password. Will prompt if not set. [TORONTO_HYDRO_PASSWORD]
  --account-id ACCOUNT_ID, -a ACCOUNT_ID
                        Toronto Hydro account ID. Will prompt if not set. [TORONTO_HYDRO_ACCOUNT_ID]
  --sp-id SP_ID, -s SP_ID
                        Toronto Hydro service provider ID. Will prompt if not set. [TORONTO_HYDRO_SP_ID]
  --start-date START_DATE
                        Fetch usage data from this date (inclusive, YYYY-mm-dd). Defaults to one day ago (2025-11-13).
  --end-date END_DATE   Fetch usage data through this date (inclusive, YYYY-mm-dd). Defaults to one day ago (2025-11-13).
  --browser {firefox,chrome}
                        Headless browser to use to access Toronto Hydro dashboard (default: firefox).
  --output OUTPUT, -o OUTPUT
                        Write XML data to this file. Defaults to standard output.
```

If ChromeDriver is installed, the script attempts to use it by default.
Otherwise it falls back on headless Firefox.
ChromeDriver was slightly faster in my limited testing.

Run `toronto-hydro-green-button --help` for additional usage information.

## Tips

You can't get data for the current day, so this script defaults to getting data from yesterday.

## License

MIT
