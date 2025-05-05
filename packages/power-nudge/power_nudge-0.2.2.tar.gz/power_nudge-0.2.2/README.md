# ⚡ PowerNudge

<p align="center">
<a href="https://pypi.org/project/power-nudge/" target="_blank">
    <img src="https://img.shields.io/pypi/v/power-nudge?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypistats.org/packages/power-nudge" target="_blank">
    <img src="https://img.shields.io/pypi/dm/power-nudge" alt="Downloads">
</a>
</p>

**PowerNudge** is a lightweight macOS utility that monitors your MacBook's battery percentage and sends you a **WhatsApp
alert via Twilio** when it reaches a predefined charging level — so you can unplug and prolong battery health.

Built with automation in mind, it’s perfect for users who want a hands-free way to monitor charging without keeping an
eye on the battery all the time.

## 🚀 Features

* 🔋 Monitors battery percentage using macOS's `pmset` command
* 📤 Sends WhatsApp messages via Twilio when battery thresholds are crossed
* 📶 Automatically enables Wi-Fi if disabled, and checks for internet connectivity
* 🧪 Integrated logging with [Loguru](https://github.com/Delgan/loguru) for easier debugging and monitoring
* ⚙️ Configurable thresholds and message templates via `src/config.py`

## 🛠 Requirements

* Python 3.12+
* macOS (uses `pmset` for battery info)
* Twilio Account with WhatsApp sandbox enabled
* Internet connection to send WhatsApp messages

## 📦 Installation

Install dependencies:

```bash
pip install power_nudge
````

Make sure you have the appropriate values set in `src/config.py` or through environment variables if abstracted.

## 🧠 How It Works

1. Reads your battery percentage using the `pmset` command.
2. Checks if battery is above or below thresholds:
    * Sends *"Please unplug!"* if battery is too high.
    * Sends *"Please plug in!"* if battery is too low.
3. Automatically enables Wi-Fi if off, and waits for connectivity.
4. Uses Twilio to send a WhatsApp alert.
5. All activity is logged using a central `log` object via Loguru.

## 🧪 Usage

```bash
python src/power_nudge/main.py
```

Or schedule it with a **cron job** or **launchd** to run periodically in the background.

## 📝 Logging

PowerNudge uses the [Loguru](https://loguru.readthedocs.io/en/stable/) library for structured, colorful, and level-based
logging (`debug`, `info`, `warning`, `error`).
You can configure your logging output in the `logger.py` file.

## 📬 Example WhatsApp Alerts

> 🔋 *Battery is 90%. Please unplug the charger!*
> 🔌 *Battery is 15%. Please plug in your charger!*

## 🧰 Developer Info

You’ll find helper functions in:

* `src/power_nudge/utils/helper.py` — for battery, Wi-Fi, and internet utilities
* `twilio_helper/main.py` — for sending WhatsApp messages via Twilio API
* `src/power_nudge/utils/logger.py` — for centralized logging setup

## 📄 License

MIT License