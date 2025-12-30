from dotenv import load_dotenv
load_dotenv()

import json
import time
import os
import requests
from datetime import datetime, timedelta


HISTORY_FILE = "history.json"
CHATBOT_HISTORY_FILE = "chatbot_history.json"



def ai_chat(message):
    url = "https://router.huggingface.co/v1/chat/completions"
    token = os.getenv("HF_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": message}
        ],
        "max_tokens": 100,
        "temperature": 0.8
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 503:
            return "AI is loading, wait 30 seconds and try again."
        if r.status_code == 429:
            return "Too many requests. Slow down."
        if r.status_code == 401:
            return "Invalid token."
        if r.status_code != 200:
            return f"HTTP {r.status_code}: {r.text}"

        data = r.json()

        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]

            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                if content:
                    return content.strip()

            if "text" in choice:
                return choice["text"].strip()

        return "No response from AI."

    except KeyError as e:
        return f"Response format error: missing {e}. Try again."
    except Exception as e:
        return f"Connection error: {e}"


def save_chatbot_history(user_message, ai_response, username):
    """Save chatbot conversation to history file"""
    if not os.path.exists(CHATBOT_HISTORY_FILE):
        with open(CHATBOT_HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("[]")

    with open(CHATBOT_HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = []

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": username,
        "user_message": user_message,
        "ai_response": ai_response
    }

    data.insert(0, entry)

    with open(CHATBOT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_chatbot_history():
    """Display chatbot conversation history"""
    if not os.path.exists(CHATBOT_HISTORY_FILE):
        print("No chatbot history yet.")
        return

    with open(CHATBOT_HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            print("Chatbot history file is broken.")
            return

    if not data:
        print("Chatbot history is empty.")
        return

    print("\n💬 AI Chatbot History")
    print("=" * 70)

    for i, item in enumerate(data, start=1):
        print(f"\n{i}) 📅 {item.get('timestamp', 'N/A')} - User: {item.get('user', 'Unknown')}")
        print(f"   👤 You: {item.get('user_message', 'N/A')}")
        print(f"   🤖 AI: {item.get('ai_response', 'N/A')}")
        print("-" * 70)


def save_history(entry):
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("[]")
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = []
    data.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_history():
    if not os.path.exists(HISTORY_FILE):
        print("No history yet.")
        return
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            print("History file is broken.")
            return
    if not data:
        print("History is empty.")
        return
    for i, item in enumerate(data, start=1):
        print(f"{i}) {item.get('timestamp', '')} - {item.get('city', '')}")
        print(f"   Temp: {item.get('temperature', '')}")
        print(f"   Weather: {item.get('weather', '')}")
        print(f"   Advice: {item.get('advice', '')}")
        if item.get("joke"):
            print(f"   Joke: {item.get('joke')}")
        print()


def fetch_weather_by_city(city):
    city_safe = city.replace(" ", "+")
    url = f"https://wttr.in/{city_safe}?format=j1"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def fetch_7day_weather(city):
    city_safe = city.replace(" ", "+")

    print(f"\n🌦️  Weather for the last 7 days in {city}:")
    print("=" * 60)

    for i in range(7, 0, -1):
        # Calculate the date for each day
        target_date = datetime.now() - timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")

        # wttr.in URL with specific date
        url = f"https://wttr.in/{city_safe}?date={date_str}&format=j1"

        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"❌ {date_str}: Could not fetch data")
                continue

            data = r.json()

            # Extract weather info
            if "weather" in data and len(data["weather"]) > 0:
                day_weather = data["weather"][0]

                # Get average temperature
                avg_temp = day_weather.get("avgtempC", "N/A")
                max_temp = day_weather.get("maxtempC", "N/A")
                min_temp = day_weather.get("mintempC", "N/A")

                # Get weather description
                hourly = day_weather.get("hourly", [])
                if hourly:
                    desc = hourly[0].get("weatherDesc", [{"value": "N/A"}])[0]["value"]
                else:
                    desc = "N/A"

                # Display the information
                day_name = target_date.strftime("%A")
                print(f"\n📅 {day_name}, {date_str}")
                print(f"   🌡️  Avg: {avg_temp}°C | Max: {max_temp}°C | Min: {min_temp}°C")
                print(f"   ☁️  {desc}")
            else:
                print(f"❌ {date_str}: No weather data available")

        except Exception as e:
            print(f"❌ {date_str}: Error - {e}")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    print("=" * 60)


def fetch_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=8)
        if r.status_code != 200:
            return None
        return r.json()["slip"]["advice"]
    except:
        return None


def fetch_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=8)
        if r.status_code != 200:
            return None
        j = r.json()
        return (j.get("setup", "") + " " + j.get("punchline", "")).strip()
    except:
        return None


def get_current_weather_fields(weather_json):
    try:
        current = weather_json["current_condition"][0]
        temp = current.get("temp_C", "N/A")
        desc = current.get("weatherDesc", [{"value": ""}])[0]["value"]
        feels = current.get("FeelsLikeC", temp)
        return temp, desc, feels
    except:
        return "N/A", "Unknown", "N/A"


def main():
    print("Welcome to the Weather + Advice + Joke app")
    print("Type 'q' at any prompt to quit.\n")
    name = input("What is your name? ").strip()
    if name.lower() == "q":
        return

    while True:
        print("\nMain menu:")
        print("1 - Weather + advice + joke")
        print("2 - View weather history")
        print("3 - AI chatbot")
        print("4 - 7-day weather history")
        print("5 - View chatbot history")
        print("q - Quit")
        choice = input("Choose an option: ").strip().lower()

        if choice == "q":
            break

        if choice == "1":
            city = input("Enter city name: ").strip()
            if not city:
                continue
            wjson = fetch_weather_by_city(city)
            if not wjson:
                print("Could not get weather.")
                continue
            temp, desc, feels = get_current_weather_fields(wjson)
            advice = fetch_advice() or "No advice available."
            joke = fetch_joke() or ""
            print("=" * 60)
            print(f"\nCity: {city}")
            print(f"Temperature: {temp}°C (feels like {feels}°C)")
            print(f"Weather: {desc}")
            if joke:
                print(f"Joke: {joke}")
            print(f"Advice: {advice}\n")

            save_history({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": name,
                "city": city,
                "temperature": f"{temp}°C",
                "weather": desc,
                "advice": advice,
                "joke": joke
            })

        elif choice == "2":
            print("=" * 60)
            show_history()

        elif choice == "3":
            print("=" * 60)
            print("hello ", name, "to :")
            print("\nAI Chatbot (type 'back' to return)")
            while True:
                msg = input("You: ").strip()
                if msg.lower() in ["back", "q"]:
                    break
                response = ai_chat(msg)
                print("AI:", response)

                save_chatbot_history(msg, response, name)

                time.sleep(1)

        elif choice == "4":
            city = input("Enter city name for 7-day history: ").strip()
            if not city:
                continue
            fetch_7day_weather(city)

        elif choice == "5":
            show_chatbot_history()


if __name__ == "__main__":
    main()