import json
import time
import os
import requests
from datetime import datetime

HISTORY_FILE = "history.json"

def ai_chat(message):
    token = "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"
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-120b:fastest",
        "messages": [
            {"role": "user", "content": message}
        ],
        "max_tokens": 100,  # Increased for better responses
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
        
        # Handle different response formats
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            
            # Try to get content from message
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                if content:
                    return content.strip()
            
            # Try alternative format (some models use 'text')
            if "text" in choice:
                return choice["text"].strip()
        
        return "No response from AI."
        
    except KeyError as e:
        return f"Response format error: missing {e}. Try again."
    except Exception as e:
        return f"Connection error: {e}"


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
        print(f"{i}) {item.get('timestamp','')} - {item.get('city','')}")
        print(f"   Temp: {item.get('temperature','')}")
        print(f"   Weather: {item.get('weather','')}")
        print(f"   Advice: {item.get('advice','')}")
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
        return (j.get("setup","") + " " + j.get("punchline","")).strip()
    except:
        return None

def get_current_weather_fields(weather_json):
    try:
        current = weather_json["current_condition"][0]
        temp = current.get("temp_C","N/A")
        desc = current.get("weatherDesc",[{"value":""}])[0]["value"]
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
        print("2 - View history")
        print("3 - AI chatbot")
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
            show_history()

        elif choice == "3":
            print("\nAI Chatbot (type 'back' to return)")
            while True:
                msg = input("You: ").strip()
                if msg.lower() in ["back", "q"]:
                    break
                print("AI:", ai_chat(msg))
                time.sleep(1)

if __name__ == "__main__":
    main()
