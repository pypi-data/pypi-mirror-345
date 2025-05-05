import time

from twilio_helper.main import TwilioHelper

import src.power_nudge.config as config
from src.power_nudge.utils.helper import get_battery_percentage, is_wifi_enabled, turn_wifi_on, has_internet
from src.power_nudge.utils.logger import log


class PowerNudge:
    def __init__(self):
        """
        Initializes PowerNudge by reading config values and creating Twilio helper.
        """
        try:
            log.debug("Initializing PowerNudge with config values.")
            self.twilio_whatsapp_number = f"whatsapp:{config.twilio_whatsapp_number}"
            self.twilio_account_sid = config.twilio_account_sid
            self.twilio_auth_token = config.twilio_auth_token
            self.stop_charging_at_percentage = config.stop_charging_at_percentage
            self.whatsapp_message_for_unplug = config.whatsapp_message_for_unplug
            self.receiver_whatsapp_number = f"whatsapp:{config.receiver_whatsapp_number}"
            self.sleep_time_after_turning_on_wifi = config.sleep_time_after_turning_on_wifi
            self.start_charging_at_percentage = config.start_charging_at_percentage
            self.whatsapp_message_for_charging = config.whatsapp_message_for_charging
            log.info("PowerNudge initialized successfully.")
            self.main()
        except Exception as e:
            log.error(f"Failed to initialize PowerNudge: {e}")
            raise

    def main(self):
        """
        Monitors battery level and sends WhatsApp messages via Twilio if:
        - Battery percentage exceeds the stop threshold (alert to unplug).
        - Battery percentage drops below the start threshold (alert to plug in).

        Steps:
        - Retrieve battery percentage.
        - Depending on threshold, send appropriate WhatsApp alert.
        - Ensure Wi-Fi is enabled and internet is accessible before sending.

        Raises:
            RuntimeError: If Wi-Fi is enabled but no internet access.
            Exception: For any unexpected failure during execution.
        """
        try:
            log.debug("Starting battery monitoring logic.")
            battery = get_battery_percentage()
            if battery is None:
                log.error("Battery percentage could not be retrieved.")
                raise RuntimeError("Could not retrieve battery percentage.")
            log.info(f"Current battery percentage: {battery}%")

            # Determine whether to send a charging or unplug alert
            if battery >= self.stop_charging_at_percentage:
                message = self.whatsapp_message_for_unplug
                log.info("Battery is above the stop threshold. Preparing to send unplug alert.")
            elif battery <= self.start_charging_at_percentage:
                message = self.whatsapp_message_for_charging
                log.info("Battery is below the start threshold. Preparing to send charging alert.")
            else:
                log.debug("Battery percentage within threshold. No action required.")
                return  # No action needed

            # Ensure Wi-Fi and internet access
            if not is_wifi_enabled():
                log.warning("Wi-Fi is disabled. Turning it on.")
                turn_wifi_on()
                time.sleep(self.sleep_time_after_turning_on_wifi)
                log.info("Wi-Fi turned on and waited for connection.")

            if has_internet():
                log.info("Internet connectivity confirmed. Proceeding to send WhatsApp message.")
                twilio_helper = TwilioHelper(self.twilio_account_sid, self.twilio_auth_token)
                twilio_helper.send_whatsapp_message(message,
                                                    self.twilio_whatsapp_number,
                                                    self.receiver_whatsapp_number)
                log.info("WhatsApp message sent successfully.")
            else:
                log.error("Wi-Fi is ON but no internet access.")
                raise RuntimeError("Wi-Fi is ON but no internet access.")
        except Exception as e:
            log.error(f"PowerNudge main execution failed: {e}")
            raise RuntimeError(f"PowerNudge main execution failed: {e}")


if __name__ == "__main__":
    log.debug("Starting PowerNudge script.")
    PowerNudge()
