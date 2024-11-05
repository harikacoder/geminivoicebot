import os
import pyttsx3 as py
import speech_recognition as sr
import pywhatkit
import randfacts
import requests
from datetime import date, datetime
import time
import google.generativeai as genai
import pygame
import pyaudio

engine = py.init()
engine.setProperty('rate', 190)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

genai.configure(api_key="")
today = str(date.today())
openaitts = False

pygame.mixer.init()

def generate_response(prompt):
    try:
        model = genai.GenerativeModel(
            model_name="chatgpt-4",
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ],
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

def speak_text(text):
    global openaitts    

    if openaitts:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        
        fname = 'output.mp3'
        with open(fname, 'wb') as mp3file:
            response.write_to_file(mp3file)

        try:
            pygame.mixer.music.load(fname)
            pygame.mixer.music.play()
        
            while pygame.mixer.music.get_busy():
                time.sleep(0.25)
            
            pygame.mixer.music.stop()
        
        except KeyboardInterrupt:
            pygame.mixer.music.stop()
            
    else:
        engine.say(text)
        engine.runAndWait()
        
talk = []

def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a") as f:
        f.write(text + "\n")

def get_chat_log():
    global today
    fname = 'chatlog-' + today + '.txt'
    if os.path.exists(fname):
        with open(fname, "r") as f:
            return f.read()
    else:
        return "No chat log found for today."

def main():
    global talk, today, model
    
    rec = sr.Recognizer()
    mic = sr.Microphone()
    rec.dynamic_energy_threshold = False
    rec.energy_threshold = 400    
    
    sleeping = True 
    
    while True:     
        with mic as source1:            
            rec.adjust_for_ambient_noise(source1, duration=0.5)

            print("Listening ...")
            
            try: 
                audio = rec.listen(source1, timeout=10, phrase_time_limit=15)
                text = rec.recognize_google(audio)
                
                if sleeping:
                    if "nova" in text.lower():
                        request = text.lower().split("nova")[1].strip()
                        sleeping = False
                        append2log(f"_"*40)
                        talk = []                        
                        today = str(date.today()) 
                         
                        if len(request) < 5:
                            speak_text("Hello I am nova, " + wishme() + ", I am your voice assistant.")
                            today_date = datetime.now()
                            hour_minute = today_date.strftime("%I:%M %p")
                            speak_text(f"Today is {today_date.strftime('%d')} of {today_date.strftime('%b')}. And it's currently {hour_minute}. {today_date.strftime('%a')}.")
                            speak_text(" how can I help you ?")
                            append2log(" how can I help?\n")
                            continue                      
                else: 
                    request = text.lower().strip()
                    if "that's all"  in request or "that's it" in request:
                        append2log(f"You: {request}\n")
                        speak_text("Bye now")
                        append2log("AI: Bye now.\n")                        
                        print('Bye now')
                        sleeping = True
                        continue
                    if "nova" in request:
                        request = request.split("nova")[1].strip()

                append2log(f"You: {request}\n")
                print(f"You: {request}\nAI: ")

                talk.append({'role': 'user', 'parts': [request]})

                if "chat log" in request:
                    chat_log = get_chat_log()
                    speak_text("Here is the chat log for today.")
                    speak_text(chat_log)
                    append2log("AI: Provided chat log.\n")
                else:
                    response = model.generate_content(talk, stream=True)
                    response_text = ''.join(chunk.text for chunk in response)
                    print(response_text)
                    speak_text(response_text.replace("*", ""))
                    talk.append({'role': 'model', 'parts': [response_text]})
                    append2log(f"AI: {response_text}\n")

            except Exception as e:
                continue 

            if "temperature" in request or "weather" in request:
                temp, desc = weather()
                speak_text(f"The current temperature is {temp} degrees Celsius with {desc}.")
            elif "news" in request:
                headlines = get_news()
                speak_text("Here are the top news headlines:")
                for i, headline in enumerate(headlines, 1):
                    speak_text(f"Headline {i}: {headline}")
            elif "call" in request:
                speak_text("Who would you like to call?")
                person = rec.recognize_google(rec.listen(source1))
                append2log(f"Call: {person}")
                speak_text(f"Calling {person} is not supported currently.")
            elif "play song" in request or "play music" in request:
                speak_text("Which song or video would you like to play?")
                media = rec.recognize_google(rec.listen(source1))
                append2log(f"Play song or video: {media}")
                pywhatkit.playonyt(media)
                speak_text(f"Playing {media} on YouTube.")

            elif "play vedio " in request or "play a vedio" in request:
                speak_text("Which video would you like to play?")
                media = rec.recognize_google(rec.listen(source1))
                append2log(f"Play video: {media}")
                pywhatkit.playonyt(media)
                speak_text(f"Playing {media} on YouTube.")
            elif "information" in request or "who is" in request:
                speak_text("You want information related to which topic?")
                topic = rec.recognize_google(rec.listen(source1))
                append2log(f"Information: {topic}")
                response = generate_response(topic)
                speak_text(response)
            elif "search" in request:
                speak_text("What do you want me to search for?")
                query = rec.recognize_google(rec.listen(source1))
                append2log(f"Search: {query}")
                pywhatkit.search(query)
                speak_text(f"Searching {query} on Google.")
            elif "fact" in request:
                fact = randfacts.get_fact()
                append2log("Random fact request")
                speak_text(f"Did you know that {fact}")
            elif "joke" in request:
                setup, punchline = joke()
                speak_text("Okay get ready for some chuckles")
                append2log("Joke request")
                speak_text(setup)
                speak_text(punchline)
                
            else:
                response = generate_response(request)
                speak_text(response)

def wishme():
    hour = int(datetime.now().hour)
    if 1 < hour < 12:
        return "Good morning"
    elif 12 <= hour < 16:
        return "Good afternoon"
    else:
        return "Good evening"

def weather():
    try:
        api_address = 'https://api.openweathermap.org/data/2.5/weather?q=Vishakhapatnam&appid=33b2b85b934773c225dfde666c9ed0b7'
        json_data = requests.get(api_address).json()
        temperature = round(json_data["main"]["temp"] - 273.15, 1)
        description = json_data["weather"][0]["description"]
        return temperature, description
    except Exception as e:
        return "unknown", f"an error occurred: {e}"

def get_news():
    try:
        api_key = "c3de44ca3efa473f8ee154228a0f1c91"
        url = f'https://newsapi.org/v2/top-headlines?country=in&apiKey={c3de44ca3efa473f8ee154228a0f1c91}'
        response = requests.get(url)
        news_data = response.json()
        articles = news_data['articles']
        headlines = [article['title'] for article in articles[:5]]
        return headlines
    except Exception as e:
        return [f"Error retrieving news: {e}"]

if __name__ == "__main__":
    main()
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    # Process the message
    response = process_message(user_message)
    return jsonify({'response': response})

def process_message(message):
    # Logic to process the message
    return "This is a placeholder response."

if __name__ == '__main__':
    app.run(debug=True)
