# -*- coding: utf-8 -*-
"""
Created on Mon May  3 18:24:01 2021

@author: krist
"""
import pandas as pd

# definerer funksjonen som blir kalt av hovedprogrammet(planer.py)
# funksjonen resetter alle midlertidige csv-filer slik at de er klase for ny informasjon
def resett():
    # Definerer dataframes ved hjelp av pandas
    room_df = pd.DataFrame(data={'Date': [], 'kWh': [], 'Temp': []})
    price_df = pd.DataFrame(data={'Date': [], 'kr/kWh': []})
    prod_h_df = pd.DataFrame(data={'Date': [], 'Time': [], 'kWh': []})
    bill_temp_df = pd.DataFrame(data={'Week': [], 'Date': [], 'Kr': []})
    consum_temp_df = pd.DataFrame(data={'Date': [], 'kWh': []})
    
    # lager csv-fila
    prod_h_df.to_csv('temp_csv/Panel_production_hour.csv', index=False)
    room_df.to_csv('temp_csv/Heating_Room.csv', index=False)
    price_df.to_csv('temp_csv/avg_price_day.csv', index=False)
    bill_temp_df.to_csv('temp_csv/bill_temp.csv', index=False)
    consum_temp_df.to_csv('temp_csv/El_consumption_temp.csv', index=False)
