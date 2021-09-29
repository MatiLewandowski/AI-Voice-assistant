from __future__ import print_function
from re import search
from typing import _SpecialForm
import pyttsx3
import datetime
import speech_recognition as sr
import webbrowser
import wolframalpha
import wikipedia
from youtube_search import YoutubeSearch
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pytz
import requests,json



#engine init
engine=pyttsx3.init()
engine.setProperty('rate',150)

def log_to_Gcalendar():

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(service,query):

    # Call the Calendar API
    #timezone and time range preparation for proper request with google API
    tz=pytz.timezone('Europe/Warsaw')
    now = datetime.datetime.now()
    end_of_day=datetime.datetime.combine(now,datetime.datetime.max.time())
    now=now.astimezone(tz)
    end_of_day=end_of_day.astimezone(tz)

    print(f'Getting the upcoming events')

    #query for today events
    if 'today' in query:
        events_result = service.events().list(calendarId='primary', timeMin=now.isoformat(),timeMax=end_of_day.isoformat(),
                                        maxResults=5, singleEvents=True,
                                        orderBy='startTime').execute()

    #general query for 10 upcoming events
    else:
        events_result = service.events().list(calendarId='primary', timeMin=now.isoformat(),
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()  
    events = events_result.get('items', [])

    #inform the user if there's nothing upcoming
    if not events:
        print('No upcoming events found.')
        speak('No upcoming events')
    
    #display the events if there're any
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def weather_info(query):
    #Whats the weather in 'city' - request formula for getting weather info
    #get the city name
    city=query.split()[-1]
    #credentials for openweathermap API
    api_key='5601d4d8cb528b7c108b79aaee8b4806'
    
    #URL prepared for weather info search
    cpl_url=f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    try:
        response=requests.get(cpl_url)

    except:
        #if there's an error, request weather info of hometown
        cpl_url=f'http://api.openweathermap.org/data/2.5/weather?q=Gdansk&appid={api_key}&units=metric'
        response=requests.get(cpl_url)
    finally:
        info=response.json()
        #get the info about main weather & temperature in given location & then tell it to the user
        main=info['weather'][0]['main']
        temp=info['main']['temp']
        speak(f'Weather for today in {city} is: {main} and the temperature is {temp} degrees')


def speak(audio):
    #speaking function, converts the text to speech so the voice assistant can communicate with the user
    engine.say(audio)
    engine.runAndWait()

def current_time():
    #get the current time and return it
    Time=datetime.datetime.now().strftime("Today is %A %d of %B and the time is %I:%M %p")
    return Time

def welcome_message():
    #During startup welcome the user according to the current time
    if datetime.datetime.now().hour<12 and datetime.datetime.now().hour>0:
        speak('Good morning')
    elif datetime.datetime.now().hour>12 and datetime.datetime.now().hour<18:
        speak('Good afternoon')
    else:
        speak('Good evening')


welcome_message()




def speech_recognition():
    #speech recognition function, returning the string of what user said to process
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
        except Exception:
            pass
        return recognized

def searching(query):
    #Search function for user queries
    #first try wolfram engine
    try:
        app_id='YGHQAL-XY75Y64RRL'
        client=wolframalpha.Client(app_id)
        res=client.query(query)
        answer=next(res.results).text
        print(answer)
    except:
        #if answer not found, try Wikipedia
        found=wikipedia.search(query,3)
        if not found:
            print("I couldn't find anything")
        print(wikipedia.search(query,3))
        
        #list 3 most popular results and let the user decide what to read

        speak('3 most popular results are: ')
        for item in found:
            speak(item)
        speak('What would you like me to read?')
        choice=''
        possibilities=['first','second','third']
        while choice not in possibilities:
            choice=speech_recognition().lower()
        if 'first' in choice:
            print(wikipedia.summary(found[0]))
            speak(wikipedia.summary(found[0],2))
        elif 'second' in choice:
            print(wikipedia.summary(found[1]))
            speak(wikipedia.summary(found[1],2))  
        elif 'third' in choice:
            print(wikipedia.summary(found[2]))
            speak(wikipedia.summary(found[2],2))    

def yt_search():
    #youtube open/search function
    speak('would you like to see some specific video?')
    text=speech_recognition().lower()
    if 'no' in text:
        #opens main page of youtube
        webbrowser.open('youtube.pl')

    elif 'yes' in text:
        #opens specific video according to the user preferences
        speak('tell me what you want to see')
        text=speech_recognition().lower()
        result=YoutubeSearch(text,1).to_dict()
        url_suffix=result[0]['url_suffix']
        webbrowser.open('youtube.pl'+url_suffix)

def main():
    #main function/flow of voice assistant in variety of situations/queries from user
    wake='hello'
    decision='yes'
    
    while True:
        choice_flag=True
        text=speech_recognition().lower()
        while text.count(wake)>0:
            if choice_flag==True:
                speak("What's up?")
            query=''
            while query=='':
                query=speech_recognition().lower()

            if 'schedule' in query:
                service=log_to_Gcalendar()
                get_events(service,query)
                text=''

            elif 'weather' in query:
                weather_info(query)
                text=''

            elif 'open google' in query:
                webbrowser.open('google.pl')
                text=''

            elif 'open youtube' in query:
                yt_search()
                text=''


            elif 'time' in query:
                speak(current_time())
                text=''
                
            elif 'search' in query:
                query=query.replace('search for','')
                print(query)
                searching(query)
                text=''
            else:
                speak("Sorry, I don't understand. Would you like to try again?")
                choices=['yes','no']
                while choice_flag==True:
                    decision=speech_recognition().lower()
                    if decision in choices:
                        choice_flag=False
                        if decision=='yes':
                            continue
                        else:
                            text=''
                    else:
                        speak('Come again?')
                

main()









