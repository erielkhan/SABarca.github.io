import pandas as pd
import requests
import os
import time

POBLACIO_FIXA = 'Sant Andreu de la Barca'

def descarregar_geojson(nom, consulta):
    # Generem la consulta combinada
    consulta_neta = consulta.replace('(area)', '(area.municipi)')
    
    consulta_completa = f"""[out:json][timeout:400][maxsize:2147483648];
area["name"="{POBLACIO_FIXA}"]["admin_level"="8"]->.municipi;
(
  {consulta_neta}
);
out body;
>;
out skel qt;"""
    
    # --- LÍNIA DE DIAGNÒSTIC ---
    print("\n--- CODI ENVIAT A OVERPASS (Copia'l si falla per provar-lo a la web) ---")
    print(consulta_completa)
    print("---------------------------------------------------------------------\n")
    
    url = "https://overpass-api.de/api/interpreter"
    
    if not os.path.exists('dades'):
        os.makedirs('dades')
    ruta_fitxer = f"dades/{nom}.geojson"
    
    try:
        resposta = requests.get(url, params={'data': consulta_completa}, timeout=420)
        
        if resposta.status_code == 200:
            dades_json = resposta.json()
            
            if "elements" in dades_json and len(dades_json["elements"]) > 0:
                if os.path.exists(ruta_fitxer):
                    os.remove(ruta_fitxer)
                
                with open(ruta_fitxer, "w", encoding='utf-8') as f:
                    f.write(resposta.text)
                print(f" -> [OK] Èxit! Fitxer desat a: {ruta_fitxer} ({len(dades_json['elements'])} elements).")
            else:
                if "remark" in dades_json:
                    print(f" -> [ALERTA] El servidor d'Overpass ha tornat un error de sintaxi: {dades_json['remark']}")
                else:
                    print(f" -> [ALERTA] La consulta ha anat bé però ha tornat 0 elements. Segur que hi ha dades d'això a Sant Andreu de la Barca?")
                    
        elif resposta.status_code == 429:
            print(f" -> [ERROR 429] Bloqueig temporal per excés de peticions.")
        else:
            print(f" -> [ERROR] El servidor ha respost amb codi: {resposta.status_code}")
            print(f" Contingut de la resposta d'error: {resposta.text[:200]}")
            
    except Exception as e:
        print(f" -> [ERROR INESPERAT]: {e}")

# Llegir el llistat de consultes del CSV
try:
    df = pd.read_csv('consultes.csv')
    total_files = len(df)
    
    for index, fila in df.iterrows():
        descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
        if index < total_files - 1:
            print(" -> Esperant 60 segons per cortesia...")
            time.sleep(60) 
            
except Exception as e:
    print(f"Error crític llegint el fitxer CSV: {e}")
