# ⚡ PowerNudge

**PowerNudge** is a lightweight macOS utility that monitors your MacBook's battery percentage and sends you a **WhatsApp
alert via Twilio** when it reaches a predefined charging level — so you can unplug and prolong battery health.

Built with automation in mind, it’s perfect for users who want a hands-free way to monitor charging without keeping an
eye on the battery all the time.

---

## 🚀 Features

* 🔋 Monitors battery percentage using macOS's `pmset` command
* 📤 Sends a WhatsApp message via Twilio when a threshold is reached
* 🧪 Built-in Twilio credential validation

---

## 🛠 Requirements

* Python 3.12+
* macOS (uses `pmset` for battery info)
* Twilio Account with WhatsApp sandbox enabled
* Internet connection to send WhatsApp message

---

## 📦 Installation

Install dependencies:

```bash
pip install power_nudge
```

---

## 🧠 How It Works

* Reads your battery percentage via `pmset -g batt`
* Sends a WhatsApp alert if the threshold is reached

---

## 🧪 Usage

```bash
python src/power_nudge/main.py
```

Or, schedule it with a **cron job** or **launchd** to run periodically.

---

## 📬 Example Alert

> 🟢 *Battery is 90%. Please unplug the charger!*

---

## 📄 License

MIT License

---