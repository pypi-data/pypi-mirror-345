import speech_recognition as sr
import pyttsx3
import os
import pyautogui
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from platform import python_branch
import time
import subprocess
import re
from pathlib import Path
from unicodedata import name
def lekho(variable):
    print(f'{variable}')
def bolo(audio):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voices', voices[0].id)
    engine.say(audio)
    print(audio)
    engine.runAndWait()
def kholo(app):
    os.startfile(app)
def bondho_koro(app):
    os.system("taskkill /f /im " + app + ".exe")
def screenshot_nao(path):
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
def shuno():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio = r.listen(source, timeout=2, phrase_time_limit= 5)
    try:
        print("Recognising....")
        query = r.recognize_google(audio, language='en-in')
        print(f"Apni bolechen:\n {query}")
    except Exception as e:
        return 'none'
    return query
def input_nao(input_variable):
    input(f'{input_variable}')
def hishab_koro_rectangular_area(l,w):
    print("The area is", l*w)
def hishab_koro_square_area(a):
    print("The area is", a*a)
def hishab_koro_triangle_area(l,h):
    print("The are is", 0.5*l*h)
def hishab_koro_circular_area_diametre(d):
    r = 0.5*d
    print("The area is", 3.1416*r*r)
def hishab_koro_circular_area_radius(r):
    print("The area is", 3.1416*r*r)
def hishab_kore_bolo_rectangular_area(l,w):
    bolo("The area is")
    bolo(l*w)
def hishab_kore_bolo_square_area(a):
    bolo("The area is")
    bolo(a*a)
def hishab_kore_bolo_triangle_area(l,h):
    bolo("The area is")
    bolo(0.5*l*h)
def hishab_kore_bolo_circular_area_diametre(d):
    r = 0.5*d
    bolo("The area is")
    bolo(3.1416*r*r)
def hishab_kore_bolo_circular_area_radius(r):
    bolo("The area is")
    bolo(3.1416*r*r)
def sum(x,y):
    result = x+y
    lekho(result)


def email_pathao(From, To, Subject, Compose, Password, Host, port):
    msg = MIMEMultipart()
    msg['Subject'] = Subject
    msg['From'] = From 
    msg['To'] = To 
    body = MIMEText(Compose)
    msg.attach(body)
    UserName = From
    UserPassword = Password
    Server = Host
    Port = port
    s = smtplib.SMTP(Server, Port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(UserName, UserPassword)
    s.sendmail(From, To, msg.as_string())
    s.quit()
    
def is_equal(a, b):
    # Check if both parameters have the same data type
    if type(a) is type(b):
        # Perform comparison based on the data type
        if a == b:
            return "yes"
        else:
            return "no"
    else:
        # Return False if data types don't match
        return False
        