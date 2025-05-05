import subprocess

import requests

from src.power_nudge.utils.logger import log


def get_battery_percentage():
    """
    Uses macOS's `pmset` to get the current battery percentage.

    Returns:
        int: Battery percentage if successful.
        None: If retrieval fails.
    """
    log.debug("Attempting to retrieve battery percentage using 'pmset'.")
    try:
        result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
        percentage = int(result.stdout.split('\t')[1].split(';')[0].strip().replace('%', ''))
        log.info(f"Battery percentage retrieved successfully: {percentage}%")
        return percentage
    except Exception as e:
        log.error(f"Failed to retrieve battery percentage: {e}")
        return None


def is_wifi_enabled() -> bool:
    """
    Check if Wi-Fi is currently enabled on the default interface (en0).

    Returns:
        bool: True if Wi-Fi is enabled, False otherwise.
    Raises:
        RuntimeError: If checking Wi-Fi status fails.
    """
    log.debug("Checking if Wi-Fi is enabled on interface 'en0'.")
    try:
        result = subprocess.run(['networksetup', '-getairportpower', 'en0'], capture_output=True, text=True)
        enabled = 'On' in result.stdout
        log.info(f"Wi-Fi enabled: {enabled}")
        return enabled
    except subprocess.CalledProcessError as e:
        log.error(f"subprocess error while checking Wi-Fi status: {e}")
        raise RuntimeError(f"Failed to check Wi-Fi status: {e}")
    except Exception as e:
        log.error(f"Unexpected error while checking Wi-Fi status: {e}")
        raise RuntimeError(f"Unexpected error checking Wi-Fi status: {e}")


def turn_wifi_on() -> None:
    """
    Turns on Wi-Fi on the default interface (en0).

    Raises:
        RuntimeError: If enabling Wi-Fi fails.
    """
    log.debug("Attempting to turn on Wi-Fi on interface 'en0'.")
    try:
        subprocess.run(['networksetup', '-setairportpower', 'en0', 'on'], check=True)
        log.info("Wi-Fi has been successfully turned on.")
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to turn on Wi-Fi: {e}")
        raise RuntimeError(f"Failed to turn on Wi-Fi: {e}")
    except Exception as e:
        log.error(f"Unexpected error while turning on Wi-Fi: {e}")
        raise RuntimeError(f"Unexpected error turning on Wi-Fi: {e}")


def has_internet() -> bool:
    """
    Check for internet connectivity by pinging Google.

    Returns:
        bool: True if the internet is reachable, False otherwise.
    """
    log.debug("Checking internet connectivity by pinging Google.")
    try:
        requests.get("https://www.google.com", timeout=3)
        log.info("Internet connectivity confirmed.")
        return True
    except requests.RequestException as e:
        log.warning(f"No internet connection detected: {e}")
        return False
