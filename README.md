# 🌦️ Weather + Advice + AI Chatbot App

This is a simple Python application I built in my free time.

The app uses the **requests** library to communicate with public web APIs and provides the following features:

- ✅ Check today’s weather by city
- ✅ View weather history for the last 7 days
- ✅ Get random advice and jokes
- ✅ Built-in AI chatbot (ask general questions)

---

## ⚙️ Requirements

- Python 3.9 or higher
- `requests`
- `python-dotenv`

Install dependencies:

```bash

pip install requests python-dotenv
```

## 🚀 How to Run
```bash

python main.py

```
## 🤖 AI Chatbot Setup (Required)
---
---

To use the AI chatbot, you need a Hugging Face access token.

1️⃣ Create a Hugging Face Token

Go to: https://huggingface.co/settings/tokens

Click New token

Enable:
```bash

Inference → Make calls to Inference Providers


```
Copy your token (it starts with hf_)

2️⃣ Set the Token (Recommended Method)

Create a file named .env in the project root directory and add:
```bash
HF_TOKEN=PUT_YOUR_HUGGINGFACE_TOKEN_HERE
```

## ⚠️ Important:

Do NOT commit this file

Make sure .env is listed in .gitignore

## 🔐 Security Notice

Never share your Hugging Face token

Never commit real tokens to GitHub

Each user must create and use their own token

## 📌 Notes

The AI chatbot uses a non-gated Hugging Face model

Free-tier rate limits may apply

If the model is loading, wait a few seconds and try again

## 📄 License

This project is for learning and testing purposes.


---
