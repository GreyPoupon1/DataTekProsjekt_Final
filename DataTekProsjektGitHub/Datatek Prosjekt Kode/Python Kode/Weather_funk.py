# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 13:47:54 2021
@author: krist
"""

# impoterer nødvendige bibliotek
from yr.libyr import Yr
import pandas as pd
import requests
import json

# Definerer funksjonen som kalles i hovedprogrammet
def get_weather():
    # henter værdata fra yr og lagrer temperatur, vindhastighet og nedbørsmengde
    weather_df = Yr(location_name='Norge/Trøndelag/Trondheim/Trondheim')
    now_df = weather_df.now()
    temp_val = int(pd.DataFrame(now_df)['temperature']['@value']) # temp i Celsius
    wind_val = float(pd.DataFrame(now_df)['windSpeed']['@mps']) # vindhastighet i mps
    precipitation_val = float(pd.DataFrame(now_df)['precipitation']['@value']) # nedbørsmengde i mm

    # Definerer token for overførsel av data til CoT
    token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzUxIn0.DeRcDo1IRe0fFV_IEw8WyUbEd02hwzWikjARXvc2oEE'
    # sender temperatur til CoT
    temp_key = '12583'
    temp_data = {'Key': temp_key, 'Value': temp_val, 'Token': token}
    t_put = requests.put('https://circusofthings.com/WriteValue', 
             data = json.dumps(temp_data), 
             headers={'Content-Type': 'application/json'})
    
    # sender vindhastighet til CoT
    wind_key = '8760'
    wind_data = {'Key': wind_key, 'Value': wind_val, 'Token': token} 
    w_put = requests.put('https://circusofthings.com/WriteValue', 
             data = json.dumps(wind_data), 
             headers={'Content-Type': 'application/json'})
    
    # sender nedbørsmengde til CoT
    precipitation_key = '6464'
    precipitation_data = {'Key': precipitation_key, 'Value': precipitation_val, 'Token': token}
    p_put = requests.put('https://circusofthings.com/WriteValue', 
             data = json.dumps(precipitation_data), 
             headers={'Content-Type': 'application/json'})