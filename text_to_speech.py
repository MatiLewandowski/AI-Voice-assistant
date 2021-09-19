from typing import _SpecialForm
import pyttsx3
import datetime
import speech_recognition as sr
import webbrowser
import wolframalpha
import wikipedia
from youtube_search import YoutubeSearch

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


def speech_recognition(counter=1):
    r=sr.Recognizer()
    mic=sr.Microphone()
    with mic as source:
        recognized=''
        print('listening...')
        r.adjust_for_ambient_noise(source)
        audio=r.listen(source)
        try:   
            recognized=r.recognize_google(audio)
            print(recognized)
        except Exception as e:
            print('Exception: ' + str(e))
        return recognized

def searching(query):
    try:
        app_id='YGHQAL-XY75Y64RRL'
        client=wolframalpha.Client(app_id)
        res=client.query(query)
        answer=next(res.results).text
        print(answer)
    except:
        print(wikipedia.search(query,3))
        return wikipedia.search(query,3)

wake='hello'
while True:

    text=speech_recognition().lower()

    if text.count(wake)>0:

        speak("lana is here")
        query=speech_recognition().lower()
        if 'open google' in query:
            webbrowser.open('google.pl')
        elif 'open youtube' in query:
            webbrowser.open('youtube.pl')
            speak('would you like to see some specific video?')
            text=speech_recognition().lower()
            if 'no' in text:
                webbrowser.open('youtube.pl')

            elif 'yes' in text:
                speak('tell me what you want to see')
                text=speech_recognition().lower()
                result=YoutubeSearch(text,1).to_dict()
                url_suffix=result[0]['url_suffix']
                webbrowser.open('youtube.pl'+url_suffix)


        elif 'time' in query:
            speak(current_time())
        elif 'search' in query:
            query=query.replace('search for','')
            query.strip()
            print(query)
            found=searching(query)
            speak('3 most popular results are: ')
            for item in found:
                speak(item)
            speak('What would you like me to read?')
            choice=speech_recognition().lower()
            if 'first' in choice:
                print(wikipedia.summary(found[0]))
                speak(wikipedia.summary(found[0]),2)
            elif 'second' in choice:
                print(wikipedia.summary(found[1]))
                speak(wikipedia.summary(found[1]),2)  
            elif 'third' in choice:
                print(wikipedia.summary(found[2]))
                speak(wikipedia.summary(found[2]),2)








