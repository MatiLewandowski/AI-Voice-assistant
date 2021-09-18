from typing import _SpecialForm
import pyttsx3
import datetime
import speech_recognition as sr
import webbrowser
import wolframalpha
import wikipedia

#engine init
engine=pyttsx3.init()
engine.setProperty('rate',150)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def current_time():
    Time=datetime.datetime.now().strftime("Today is %A %d of %B and the time is %I:%M %p")
    return Time

def welcome_message():
    if datetime.datetime.now().hour<12 and datetime.datetime.now().hour>0:
        speak('Good morning')
    elif datetime.datetime.now().hour>12 and datetime.datetime.now().hour<18:
        speak('Good afternoon')
    else:
        speak('Good evening')


welcome_message()


def speech_recognition():
    r=sr.Recognizer()
    mic=sr.Microphone()
    with mic as source:
        print('listening...')
        r.adjust_for_ambient_noise(source)
        audio=r.listen(source)
        print('recognizing...')   
        recognized=r.recognize_google(audio)
        speak('you said '+ recognized)
        return recognized

def searching(query):
    try:
        app_id='YGHQAL-XY75Y64RRL'
        client=wolframalpha.Client(app_id)
        res=client.query(query)
        answer=next(res.results).text
        print(answer)
    except:
        print(wikipedia.summary(query,sentences=3))
        speak(wikipedia.summary(query,sentences=3))


while True:
    query=speech_recognition().lower()
    if 'open google' in query:
        webbrowser.open('google.pl')
    elif 'open youtube' in query:
        webbrowser.open('youtube.pl')
    elif 'time' in query:
        speak(current_time())
    elif 'search' in query:
        searching(query)





