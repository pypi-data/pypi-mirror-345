# 📲 TwilioHelper

**TwilioHelper** is a lightweight and reliable Python wrapper around Twilio's WhatsApp API, designed for quick
integration and automated messaging. It provides built-in credential validation and error handling out of the box,
making it ideal for alerting systems, notification bots, and automation workflows.

---

## 🔧 Features

- ✅ **Credential Validation** – Automatically validates Account SID and Auth Token during initialization.
- 📤 **WhatsApp Messaging** – Send WhatsApp messages in just one function call.
- ❌ **Robust Error Handling** – Handles common Twilio exceptions gracefully with meaningful feedback.

---

## 🚀 Installation

Install the Twilio SDK (if not already installed):

```bash
pip install twilio
````

---

## 🧪 Getting Started

1. **Activate Twilio Sandbox for WhatsApp:**
   Visit [https://www.twilio.com/console/sms/whatsapp/learn](https://www.twilio.com/console/sms/whatsapp/learn) to
   enable your sandbox and verify your recipient phone number.

2. **Gather Credentials:**

    * `Account SID`
    * `Auth Token`
    * `From Number` (typically `whatsapp:+14400000000` for sandbox)
    * `To Number` (your verified number, e.g., `whatsapp:+919900000000`)

---

## 📦 Usage

```python
from twilio_helper.main import TwilioHelper

# Initialize the helper
helper = TwilioHelper(account_sid="your_account_sid", auth_token="your_auth_token")

# Send a WhatsApp message
response = helper.send_whatsapp_message(
    message="Battery is 90%, please unplug.",
    from_number="whatsapp:+14400000000",
    to_number="whatsapp:+919900000000"
)

print(response)  # Example output: {'message_sid': 'SMXXXXXXXXXXXXXXXXXXXX'}
```

---

## 🛡 Error Handling

TwilioHelper raises clear, descriptive exceptions for:

* ❗ **Invalid Twilio credentials** – Prevents initialization if credentials are incorrect.
* ❗ **Failed message send** – Errors from invalid numbers, message content, or connectivity are caught and reported.

---

## 🧾 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

Built with ❤️ by [Lav](https://github.com/lavvsharma)

---

## 📬 Contributions & Feedback

Feel free to open issues or PRs to improve functionality, add support for SMS or other Twilio services, or enhance
testing.
