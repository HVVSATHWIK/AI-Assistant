import os
import asyncio
import aiohttp
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure your API key from environment variables
API_KEY = os.getenv('GENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
if not API_KEY or not WEATHER_API_KEY:
    raise ValueError("API keys for Generative AI and weather service must be set in environment variables")

genai.configure(api_key=API_KEY)

def generate_text(prompt):
    """Generate text using the Generative AI model."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating text: {e}")
        return "Sorry, I couldn't generate the text."

async def get_weather(city):
    """Fetch the current weather for a given city asynchronously."""
    try:
        base_url = 'http://api.openweathermap.org/data/2.5/weather'
        complete_url = f"{base_url}?q={city}&appid={WEATHER_API_KEY}&units=metric"
        async with aiohttp.ClientSession() as session:
            async with session.get(complete_url, timeout=10) as response:
                data = await response.json()
                if data['cod'] == 200:
                    weather = data['weather'][0]['description']
                    temp = data['main']['temp']
                    return f"The weather in {city} is currently {weather} with a temperature of {temp}°C."
                else:
                    return "Sorry, I couldn't fetch the weather information."
    except asyncio.TimeoutError:
        logging.error("Timeout error fetching weather")
        return "Fetching weather information timed out."
    except Exception as e:
        logging.error(f"Error fetching weather: {e}")
        return "Error fetching weather."

async def get_joke():
    """Fetch a random joke from the joke API asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://official-joke-api.appspot.com/jokes/random", timeout=10) as response:
                if response.status == 200:
                    joke = await response.json()
                    return f"{joke['setup']} - {joke['punchline']}"
                else:
                    return "Sorry, I couldn't fetch a joke right now."
    except asyncio.TimeoutError:
        logging.error("Timeout error fetching joke")
        return "Fetching joke timed out."
    except Exception as e:
        logging.error(f"Error fetching joke: {e}")
        return "Error fetching joke."

def speak(text):
    """Convert text to speech and print the text."""
    print(f"Assistant: {text}")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for audio input and return it as text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for ambient noise
        try:
            audio = recognizer.listen(source, timeout=10)  # Listen for 10 seconds
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return "Listening timed out."
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, my speech service is down."

async def process_command(user_input):
    """Process the user command and return the appropriate response."""
    if "weather" in user_input.lower():
        city = user_input.split("in")[-1].strip()
        return await get_weather(city)
    elif "joke" in user_input.lower():
        return await get_joke()
    else:
        if user_input == "Listening timed out.":
            return "I did not hear anything. Please try again."
        return generate_text(user_input)

async def main():
    """Main function to run the AI assistant."""
    speak("Hello! I'm your AI assistant. Would you like to interact with me using text or voice?")
    input_method = input("Type 'text' for text input or 'voice' for voice input: ").strip().lower()

    if input_method not in ["text", "voice"]:
        speak("Invalid input. Please restart and choose either 'text' or 'voice'.")
        return

    speak("How can I help you today?")
    while True:
        if input_method == "text":
            user_input = input("You: ")
        else:
            user_input = listen()
            print(f"User: {user_input}")

        if user_input.lower() in ["exit", "quit", "bye"]:
            speak("Goodbye!")
            break
        response = await process_command(user_input)
        speak(response)

if __name__ == "__main__":
    asyncio.run(main())
