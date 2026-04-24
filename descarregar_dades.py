import pandas as pd
import requests
import os
import time

def descarregar_geojson(nom, consulta):
    # Preparem la consulta per rebre JSON formatat
    consulta_completa = f"[out:json][timeout:25];{consulta}out body;>;out skel qt;"
    url = "https://overpass-api.de/api/interpreter"
    
    print(f"Descarregant {nom}...")
    resposta = requests.get(url, params={'data': consulta_completa})
    
    if resposta.status_code == 200:
        # Creem la carpeta 'dades' si no existeix
        if not os.path.exists('dades'):
            os.makedirs('dades')
        
        ruta_fitxer = f"dades/{nom}.geojson"
        with open(ruta_fitxer, "w", encoding='utf-8') as f:
            f.write(resposta.text)
        print(f"Desat correctament: {ruta_fitxer}")
    else:
        print(f"Error en {nom}: {resposta.status_code}")

# Llegir el llistat de consultes
df = pd.read_csv('consultes.csv')

for index, fila in df.iterrows():
    descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
    # Espera de seguretat per no saturar el servidor
    time.sleep(2)
