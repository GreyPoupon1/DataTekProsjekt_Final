# -*- coding: utf-8 -*-
"""
Created on Thu May  6 16:13:49 2021

@author: krist
"""
# impoterer nødvendige bibliotek
# skal kjøres rett før midnatt hver dag
from csv import writer
import pandas as pd
import requests
import json
import datetime as dt

# definerer Funksjonen som blir kalt i hovedprogrammet(planer.py)
def prod_week():
    # finner gjellende uke
    week = dt.datetime.now().isocalendar()[1]
    
    # henter panel produksjon per dag og lagrer en kopi i som en midlertidig csv-fil for videre manipulasjon 
    prod_week_df = pd.read_csv('csvfiler/Panel_production_day.csv')
    prod_week_df.to_csv('temp_csv/Panel_prod_week.csv', index=False)

    # skriver en null verdi til den midlertidige csv-filen slik at man kan bruke sum() funksjonen i neste steg
    # sum funksjonen krever minst to verdier, på mandag ha csv-filen kun en verdi
    with open('temp_csv/Panel_prod_week.csv', 'a') as bt:
         prod_temp_df = writer(bt)
         prod_temp_df.writerow([week, '-', 0])
    
    # Plukker ut verdiene for den gjellende uka og regner ut panel produksjonen for den gjellende uka
    prod_this_week_df = pd.read_csv('temp_csv/Panel_prod_week.csv', index_col='Week')
    prod_week = sum(prod_this_week_df.at[week, 'kWh'])

    key ='2605'
    token= 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzUxIn0.DeRcDo1IRe0fFV_IEw8WyUbEd02hwzWikjARXvc2oEE'
    
    # Sender panel produksjonen for den gjellende uka til CoT
    data = {'Key': key, 'Value': prod_week, 'Token': token}

    p = requests.put('https://circusofthings.com/WriteValue', 
         data = json.dumps(data), 
         headers={'Content-Type': 'application/json'} )
    
    # lagrer panel produksjonen for den gjellende uka i permanent csv-fil
    with open('csvfiler/Panel_production_week.csv', 'a') as pw:
        prod_df = writer(pw)
        prod_df.writerow([week, prod_week])
        
    return prod_week
