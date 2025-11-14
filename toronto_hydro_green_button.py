"""
Export Green Button (ESPI) energy usage data from your Toronto Hydro account.
"""
import argparse
import enum
import getpass
import json
import logging
import os
import shutil
import sys
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import requests
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

__version__ = '0.1.0'

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Browser(str, enum.Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'


def get_web_driver(browser: Browser) -> WebDriver:
    if browser == Browser.FIREFOX:
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        return webdriver.Firefox(options=options)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        return webdriver.Chrome(options=options)


def login(driver: WebDriver, username: str, password: str) -> None:
    """Log into the Toronto Hydro dashboard."""
    driver.get('https://www.torontohydro.com/log-in')

    form = driver.find_element('id', '_th_module_authentication_ThModuleAuthenticationPortlet_authentication')
    username_field = form.find_element('id', 'email')
    password_field = form.find_element('id', 'password')
    login_button = form.find_element('css selector', '[type="submit"]')

    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()


def get_cookies(driver: WebDriver, timeout: int = 60) -> List[Dict[str, str]]:
    """Navigate to the usage dashboard and extract the browser cookies."""
    driver.get(
        'https://css.torontohydro.com/Pages/ICFRedirect.aspx?Controller=myenergy&Action=billhistory'
    )
    # Wait for redirect
    wait = WebDriverWait(driver, timeout)
    # fmt: off
    # Black splits the lamba at ==.
    wait.until(
        lambda driver: driver.current_url == 'https://www.torontohydro.com/my-account/account-summary'
    )
    # fmt: on
    cookies: List[Dict[str, str]] = driver.get_cookies()
    return cookies


def get_session(cookies: List[Dict[str, str]]) -> requests.Session:
    """Returns a requests Session with cookies required to download XML."""
    session = requests.session()
    for cookie in cookies:
        session.cookies.update({cookie['name']: cookie['value'] for cookie in cookies})  # type: ignore
    return session


def get_green_button_xml(
    session: requests.Session, 
    account_id: str,
    sp_id: str,
    start_date: date, 
    end_date: date
) -> str:
    """Download Green Button XML."""
    payload = {
        "accountId": account_id,
        "spID": sp_id,
        "downloadType": "usage",
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
    }
    response = session.get(
        "https://www.torontohydro.com/my-account/green-button-data?p_p_id=thmodulegbmanage&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=/dmd&p_p_cacheability=cacheLevelPage",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )

    response.raise_for_status()
    return response.text


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__,
    )

    parser.add_argument(
        '--username',
        '-u',
        default=os.getenv('TORONTO_HYDRO_USERNAME'),
        help='Toronto Hydro username. Will prompt if not set. [TORONTO_HYDRO_USERNAME]',
    )
    parser.add_argument(
        '--password',
        '-p',
        default=os.getenv('TORONTO_HYDRO_PASSWORD'),
        help='Toronto Hydro password. Will prompt if not set. [TORONTO_HYDRO_PASSWORD]',
    )

    parser.add_argument(
        '--account-id',
        '-a',
        default=os.getenv('TORONTO_HYDRO_ACCOUNT_ID'),
        help='Toronto Hydro account ID. Will prompt if not set. [TORONTO_HYDRO_ACCOUNT_ID]',
    )

    parser.add_argument(
        '--sp-id',
        '-s',
        default=os.getenv('TORONTO_HYDRO_SP_ID'),
        help='Toronto Hydro service provider ID. Will prompt if not set. [TORONTO_HYDRO_SP_ID]',
    )

    default_end_date = datetime.now().date() - timedelta(days=1)
    default_start_date = datetime.now().date() - timedelta(days=8)
    parser.add_argument(
        '--start-date',
        default=default_start_date,
        help=f'Fetch usage data from this date (inclusive, YYYY-mm-dd). Defaults to eight days ago ({default_start_date:%Y-%m-%d}).',
        type=clean_date,
    )
    parser.add_argument(
        '--end-date',
        default=default_end_date,
        help=f'Fetch usage data through this date (inclusive, YYYY-mm-dd). Defaults to one day ago ({default_end_date:%Y-%m-%d}).',
        type=clean_date,
    )

    parser.add_argument(
        '--browser',
        choices=[browser.value for browser in Browser],
        default=get_default_browser().value,
        help='Headless browser to use to access Toronto Hydro dashboard (default: %(default)s).',
        type=Browser,
    )
    parser.add_argument(
        '--output',
        '-o',
        metavar='OUTPUT',
        dest='out_file',
        help='Write XML data to this file. Defaults to standard output.',
        type=argparse.FileType('w'),
        default=sys.stdout,
    )

    args = parser.parse_args(argv)

    if args.start_date > args.end_date:
        raise argparse.ArgumentTypeError(
            f"end date '{args.end_date:%Y-%m-%d}' must be later than start date '{args.start_date:%Y-%m-%d}'"
        )

    return args


def get_default_browser() -> WebDriver:
    if shutil.which('chromedriver'):
        return Browser.CHROME
    else:
        return Browser.FIREFOX


def clean_date(value: str) -> date:
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f'{value!r} must be a date in ISO 8601 YYYY-mm-dd format'
        ) from exc


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    username = args.username or input('Username: ')
    password = args.password or getpass.getpass()
    account_id = args.account_id or input('Account ID: ')
    sp_id = args.sp_id or input('SP ID: ')
    start_date = args.start_date or input('Start date (YYYY-MM-DD): ')
    end_date = args.end_date or input('End date (YYYY-MM-DD): ')

    try:
        logger.info('Starting Selenium web driver')
        driver = get_web_driver(args.browser)
        logger.info('Logging into Toronto Hydro dashboard')
        login(driver, username, password)
        logger.info('Fetching Toronto Hydro dashboard cookies from browser')
        cookies = get_cookies(driver)
    finally:
        driver.quit()

    logger.info(
        'Downloading Green Button data between %s and %s',
        start_date,
        end_date,
    )
    session = get_session(cookies)
    data = get_green_button_xml(session, account_id, sp_id, start_date, end_date)
    args.out_file.write(data)


if __name__ == '__main__':
    main()
