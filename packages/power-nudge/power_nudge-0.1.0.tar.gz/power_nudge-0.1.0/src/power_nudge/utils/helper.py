import subprocess


def get_battery_percentage():
    """
    Uses macOS's `pmset` to get the current battery percentage.

    Returns:
        int: Battery percentage if successful.
        None: If retrieval fails.
    """
    try:
        result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
        percentage = int(result.stdout.split('\t')[1].split(';')[0].strip().replace('%', ''))
        return percentage
    except Exception:
        return None
