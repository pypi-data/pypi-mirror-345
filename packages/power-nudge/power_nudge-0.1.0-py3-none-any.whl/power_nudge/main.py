from twilio_helper.main import TwilioHelper

import src.config as config
from src.power_nudge.utils.helper import get_battery_percentage


class PowerNudge:
    def __init__(self):
        """
        Initializes PowerNudge by reading config values and creating Twilio helper.
        """
        try:
            self.twilio_whatsapp_number = f"whatsapp:{config.twilio_whatsapp_number}"
            self.twilio_account_sid = config.twilio_account_sid
            self.twilio_auth_token = config.twilio_auth_token
            self.stop_charging_at_percentage = config.stop_charging_at_percentage
            self.whatsapp_message_for_unplug = config.whatsapp_message_for_unplug
            self.receiver_whatsapp_number = f"whatsapp:{config.receiver_whatsapp_number}"
            self.twilio_helper = TwilioHelper(self.twilio_account_sid,
                                              self.twilio_auth_token)
            self.main()
        except Exception:
            raise

    def main(self):
        """
        Main execution logic: check battery and send WhatsApp message if needed.
        """
        try:
            battery = get_battery_percentage()
            if battery and battery >= self.stop_charging_at_percentage:
                self.twilio_helper.send_whatsapp_message(self.whatsapp_message_for_unplug,
                                                         self.twilio_whatsapp_number,
                                                         self.receiver_whatsapp_number)
        except Exception:
            raise


if __name__ == "__main__":
    PowerNudge()
