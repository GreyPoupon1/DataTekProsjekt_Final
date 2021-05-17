# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 17:53:32 2021
@author: krist
"""
# impoterer nødvendige bibliotek
# Denne koden skal kjøres rett før midnatt hver dag
# OBS! må kjøres før el_cost.pay_consm()
from yr.libyr import Yr
import pandas as pd
import requests
import json
from csv import writer
import datetime as dt

# definerer fast verdier og koeffisienter for strømforbruk i boligen 
# kjøkken
oven = 1 #kWh per bruk
fridge = 0.82 #kWh per dag
micro_oven = 0.4 #kWh per dag. 800W i 30min hver dag
dishwasher = 0.64 #kWh per dag, ved normalt bruk
# bad
Water_heater = 8 #kWh per dag
washing_machine = 0.5 #kWh per gang brukt
# tvstue
tv = 1.5 #Wh per min i bruk
# selve huset
room_heating = 0.35 #kWh/(C*dag) Romoppvarmingskoeffisient 
other = 6 #kWh per day (lys, lading, pc osv.)

# definerer siganl key og token for innhenting og utsending av tv bruk fra CoT
tv_key = '22181'
token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1MTc3In0.G9gRducsNPjd8I01Pn6tmKB6hDr8MOXLr_t9cWYNwYY' # info til CoT

# Definerer funksjon for oppvarming av fellesareal som tv-stue og bad basert på utetemperatur.
# Antar to panel ovner og varmekabler på bader med samme bruk som en panelovn
def heating_house():
    # finner datoen
    date = dt.datetime.now().strftime('%d-%m-%y')
    # henter ut dagens temperaturer og regner ut gjennomsnittstemperaturen for dagen
    temp_df = pd.read_csv('temp_csv/Heating_Room.csv', index_col='Date').at[date, 'Temp']
    temp_val = sum(temp_df)/len(temp_df)
    
    # finner ut hvor mye energi som brukes til oppvarming av fellesareal basert på Romoppvarmingskoeffisient(room_heating)
    # og differansen mellom gjennomsnitstemperaturen og 22*C.
    if temp_val < 22:
        energy_house = (room_heating * (22 - temp_val))*2
    # hvis gjennomsnitstemperaturen er større en 22*C er forbruket 0
    else:
        energy_house = 0
    # finner ut hvor mye energi som brukes til oppvarming av bad basert på Romoppvarmingskoeffisient(room_heating)
    # og differansen mellom gjennomsnitstemperaturen og 28*C.
    if temp_val < 28:
       energy_bath = (room_heating * (28 - temp_val))
    # hvis gjennomsnitstemperaturen er større en 28*C er forbruket 0
    else:
        energy_bath = 0
    # retunerer forbruket til fellesareal og bad for senere bruk
    return [energy_house, energy_bath]

# Definerer funksjon for tv forbruk
def tv_use():
   # henter antall minutter tv-en har blitt brukt den siste dagen fra CoT
   r = requests.get('https://circusofthings.com/ReadValue', params=  
                 {'Key': tv_key, 'Token':token})
   tv_time = json.loads(r.content)['Value']
   
   # regner ut tv-en sitt strømforbruk i kWh
   tv_consumption = tv * tv_time / 1000
   
   # Resetter tv tid verdi slik at den er klar for neste dag
   data = {'Key': tv_key, 'Value': 0, 'Token': token}

   p = requests.put('https://circusofthings.com/WriteValue',
             data = json.dumps(data), 
             headers={'Content-Type': 'application/json'} )
   # returnerer tv tiden for videre bruk 
   return tv_consumption

# Definerer funksjonen som kalles av hovedprogrammet.
# funksjonen regner ut strømforbruket for den gjellende dagen
def energy_use():
    # henter dato og uke og dag
    day = dt.datetime.now().isoweekday()
    date = dt.datetime.now().strftime('%d-%m-%y') 
    week_num = dt.datetime.now().isocalendar()[1]
    
    # Henter strømforbruker til soverom og regner ut totalforbruket for dagen
    bedroom = pd.read_csv('temp_csv/Heating_Room.csv')['kWh']
    heating_bedroom=0
    for i in range(len(bedroom)):
        heating_bedroom += bedroom[i]
    
    # generelt forbruk for hver dag
    total = 0
    total += heating_bedroom*6 #ganger soveromsforbruket med 6 siden de er 6 soverom
    # kjøkken forbruk
    total += fridge
    #bad forbruk
    total += washing_machine * 3 # antar at vaskemaskinen bruker en fang om dagen
    total += Water_heater
    total += heating_house()[1] #oppvarming bad
    #tv forbruk
    total += tv_use()
    # hus forbruk
    total += heating_house()[0] #oppvarming fellesareal
    total += other 
    # antatt rutine for arbeidsdager
    if day in range(1,6):
        # kjøkken forbruk
        total += oven*6 # Antar at komfyren blir brukt 6 ganger om dagen til å lage middag
        total += micro_oven
        total += dishwasher
    #lørdag
    elif day == 6:
        # kjøkken forbruk
        total += oven*9 # Antar at komfyren blir brukt 9 ganger om dagen til å lage middag og halvparten av beboerene lager frokost
        total += micro_oven*4 # microoven brukes mer på lørdag
        total += dishwasher*2 # antar mer bruk av oppvaskmaskin 
    #sunday
    else:
        # kjøkken forbruk
        total += oven*12 # Antar at komfyren blir brukt 12 ganger om dagen til å lage middag og frokost av alle
        total += micro_oven
        total += dishwasher*2 # antar mer bruk av oppvaskmaskin 
      
    # Skriver strømforbruker for dagen til csv-fil for permanent lagring og utregning av strømregning i el_cost
    total = round(total, 2)
    with open('csvfiler/Electricety_consumption.csv', 'a') as el:
        consum_df = writer(el)
        consum_df.writerow([week_num, date, total]) #skriver ukenummer, totalt strømforbruk og dato til csv fil

    ec = pd.read_csv('csvfiler/Electricety_consumption.csv')
    print('forbruk')
    print(ec)
    return ec