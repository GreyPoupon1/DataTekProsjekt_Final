# -*- coding: utf-8 -*-
"""
Created on Mon May  3 18:13:48 2021

@author: krist
"""
# impoterer Python bibliotekene som brukes i koden
from yr.libyr import Yr
import pandas as pd
import requests
import json
import csv
import datetime as dt

# Definerer funksjonen for finner strømforbruket på oppvarming til soverommet for den gjellende timen. 
# Funksjonen skal kjøres en gang hver time.
def heating_bedroom():
    # Henter værdata for tiden akkurat nå fra yr.
    weather_df = Yr(location_name='Norge/Trøndelag/Trondheim/Trondheim')
    now_df = weather_df.now()
    
    # Trekker ut utetemperaturen som skal brukes til å regne strømforbruk.
    temp_val = int(pd.DataFrame(now_df)['temperature']['@value'])
    
    # Definerer oppvarmingskoeffisient i kWh/(C*h).
    # Brukes for å finne strømforbruket for den gjellende timen basert på utetemp.
    room_heating = 0.0146 #kWh/(C*h)
    
    # Definerer den gjellenge dagen
    date = dt.datetime.now().strftime("%d-%m-%y")
    # Definerer den gjellende timen
    hour = int(dt.datetime.now().strftime("%H"))
    
    # Definerer signal key for termostat temperaturen og hjemme status som hentes fra CoT.
    temp_key = '6074'
    room_key = '15089'
    # Definerer token for å hente info fra CoT
    token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzUxIn0.DeRcDo1IRe0fFV_IEw8WyUbEd02hwzWikjARXvc2oEE'
    
    # Henter ut termostat verdien celsius til soverommet fra CoT
    # og lagrer verdien i en variabel som skal brukes for å finne strømforbruket.
    t = requests.get('https://circusofthings.com/ReadValue', params=
                 {'Key': temp_key, 'Token':token})
    temp_room = round(json.loads(t.content)['Value'])
    
    # Henter ut hjemme status verdien til soverommet fra CoT
    # og lagrer verdien i en variabel som skal brukes for å finne strømforbruket. (1 = hjemme, 0 = borte)
    r = requests.get('https://circusofthings.com/ReadValue', params=
                 {'Key': room_key, 'Token':token})
    ishome = json.loads(r.content)['Value']
    
    # Finner strømforbruket på dagen (kl. 07:00 til 23:00) når beboeren er hjemme
    if ishome == 1 and hour != 23 and hour not in range(0,8):
        # Hvis termostaten har blitt satt til 0 betyr det at ovnen er skrudd av og bruker ikke strøm. 
        if (temp_room == 0):
            energy_bedroom = 0
        # Når utetemp er lavere enn verdien til termostaten blir 
        # differansen ganget med koeffisienten for å finne strømforbruket til panelovnen.
        elif (temp_val < temp_room):
            energy_bedroom = room_heating * (temp_room - temp_val)
        # Når utetemp er lik eller større enn verdien til termostaten bruker ikke panelovnen strøm. 
        else:
            energy_bedroom = 0
            
    # Når beboeren er borte, bruker ikke panelovnen strøm.
    elif ishome == 0:
        energy_bedroom = 0
    
    # Finner strømforbruket når beboeren er hjemme på natta (kl 23:00 til 06:00).
    elif (hour == 23 or hour in range(0,7)) and ishome == 1:
        # Hvis termostaten har blitt satt til 0 betyr det at ovnen er skrudd av og bruker ikke strøm. 
        if (temp_room == 0):
            energy_bedroom = 0
        # Når utetemp er mindre enn termostat verdien minus 4 blir differansen
        # (termostat verdi – 4 – utetemp) ganget med koeffisienten for å finne strømforbruket til panelovnen.
        # Dette blir gjort for å simulere mindre strømforbruk om natta.
        elif (temp_val < temp_room - 4):
            energy_bedroom = room_heating * ((temp_room - 4) - temp_val)
        # Når utetemp er lik eller større enn verdien til termostaten minus 4 bruker ikke panelovnen strøm.
        else:
            energy_bedroom = 0
        
    # Runder av verdien for å bli kvitt unødvendige desimaltell.
    energy_bedroom = round(energy_bedroom, 3)
    
    # Skriver srtømdorbruket, temperaturen og datoen til en csv_fil.
    # Strømforbruksverdien blir brukt i el_forbruk til å regen ut totalt strømforbruk for rommet den gjellende dagen.
    # Tenperatur verdien blir brukt i el_forbruk for å finne gjennomsnittstemperaturen for dagen
    # som igjenn blir brukt for å finne strømforbruket til fellesarealene.
    with open('temp_csv/Heating_Room.csv', 'a') as p:
        prod_df = csv.writer(p)
        prod_df.writerow([date, energy_bedroom, temp_val])

    hr = pd.read_csv('temp_csv/Heating_Room.csv')
    return hr