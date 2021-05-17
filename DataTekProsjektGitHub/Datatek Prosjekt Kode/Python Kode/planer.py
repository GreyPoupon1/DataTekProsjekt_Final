# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 17:38:23 2021

@author: krist
"""
# Importerer alle python bibliotek og funksjoner som skal bli kjørt
import schedule
import time
import Weather_funk as wf #Værefunksjonen: oppdaterer CoT med værmelding
import El_price as ep #Strømprisfunksjnonen: henter dagens strømpriser fra entsoe og regnet u gjennomsnittet
import el_bedroom as eb #Soveromsfunksjonen: Simulerer energiforbruket på oppvarming på soverommet
import SolCelleProd_ny as scp #Solcellefunksjonen: Simulerer solselle produksjon basert på tid, vær og temperatur.
import el_forbruk as ef #Forbruksfunksjonen: regner ut det totale strømforbruket til boligen
import el_cost as ec #Kostendsfunksjonen: regner ut strømregning basert på forbrukm produksjon of pris.
import resett_csv as rec #Resettfunksjonen: resetter midlertidige csv-filer
import sol_week as sw #Solcelleproduksjonsfunksjonen: regner ut produksjonen så langt den gjellende uka


schedule.every().day.at("23:59").do(sw.prod_week) #Solcelleproduksjonsfunksjonen kjøres hver dag kl. 23:59
schedule.every().day.at("12:00").do(ep.get_el_price) # Strømprisfunksjnonen kjøres hver dag kl. 12:00
schedule.every().day.at("23:55").do(ef.energy_use) # Forbruksfunksjonen kjøres hver dag kl. 23:55.
                                                   # Må kjøres før Kostendsfunksjonen
schedule.every().day.at("23:58").do(ec.pay_consm) # Kostendsfunksjonen kjøres hver dag kl. 23:58
schedule.every().day.at("00:01").do(rec.resett) # Resettfunksjonen kjøres hver dag kl. 00:01. 
                                                # Må kjøres på starten av dagen for å slette forrige degens data
schedule.every().hour.at(":53").do(eb.heating_bedroom) #Soveromsfunksjonen kjøres en gang i timen kl. :53
schedule.every().hour.at(":50").do(scp.panel_output) #Solcellefunksjonen kjøres en gang i timen kl. :50
schedule.every(15).minutes.do(wf.get_weather) #Værefunksjonen kjøres hvert 15min.

#Løkka som kjører koden
while 1:
    schedule.run_pending()
    time.sleep(1)