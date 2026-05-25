import pandas as pd
import requests
import os
import time

def descarregar_geojson(nom, consulta):
    # Preparem la consulta per rebre JSON formatat des d'Overpass
    consulta_completa = f"[out:json][timeout:25];{consulta}out body;>;out skel qt;"
    url = "https://overpass-api.de/api/interpreter"
    
    # Definim la ruta del fitxer
    if not os.path.exists('dades'):
        os.makedirs('dades')
    ruta_fitxer = f"dades/{nom}.geojson"
    
    print(f"Processant {nom}...")
    
    # Forcem la sobreescriptura netejant/eliminant el fitxer vell si existeix
    if os.path.exists(ruta_fitxer):
        print(f" -> S'ha detectat un fitxer existent. Es procedirà a sobreescriure'l.")
        os.remove(ruta_fitxer)
        
    try:
        resposta = requests.get(url, params={'data': consulta_completa})
        
        if resposta.status_code == 200:
            # Guardem el nou fitxer (sobreescriptura realitzada)
            with open(ruta_fitxer, "w", encoding='utf-8') as f:
                f.write(resposta.text)
            print(f" -> [OK] Desat correctament i actualitzat: {ruta_fitxer}")
        else:
            print(f" -> [ERROR] Overpass ha tornat el codi d'error: {resposta.status_code}")
            
    except Exception as e:
        print(f" -> [ERROR] No s'ha pogut connectar o descarregar: {e}")

# Llegir el llistat de consultes del CSV
try:
    df = pd.read_csv('consultes.csv')
    for index, fila in df.iterrows():
        descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
        # Espera de seguretat de 2 segons per respectar els servidors d'Overpass
        time.sleep(2) 
except Exception as e:
    print(f"Error general en llegir el fitxer CSV: {e}")
