import pandas as pd
import requests
import os
import time

# DEFINIM LA POBLACIÓ FIXA PER A TOTES LES CONSULTES
# Definim admin_level=8 per assegurar que busquem els límits del municipi
POBLACIO_FIXA = 'Sant Andreu de la Barca'

def descarregar_geojson(nom, consulta):
    # Generem la consulta nativa d'Overpass fixant el municipi
    consulta_completa = f"""
    [out:json][timeout:400][maxsize:2147483648];
    area["name"="{POBLACIO_FIXA}"]["admin_level"="8"]->.municipi;
    (
      {consulta.replace('(area)', '(area.municipi)')}
    );
    out body;
    >;
    out skel qt;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    
    if not os.path.exists('dades'):
        os.makedirs('dades')
    ruta_fitxer = f"dades/{nom}.geojson"
    
    print(f"Processant '{nom}' a {POBLACIO_FIXA}...")
    
    try:
        resposta = requests.get(url, params={'data': consulta_completa}, timeout=420)
        
        if resposta.status_code == 200:
            dades_json = resposta.json()
            
            if "elements" in dades_json and len(dades_json["elements"]) > 0:
                if os.path.exists(ruta_fitxer):
                    os.remove(ruta_fitxer)
                
                with open(ruta_fitxer, "w", encoding='utf-8') as f:
                    f.write(resposta.text)
                print(f" -> [OK] Desat correctament ({len(dades_json['elements'])} elements trobats).")
            else:
                if "remark" in dades_json:
                    print(f" -> [ALERTA] El servidor ha rebutjat la consulta. Missatge: {dades_json['remark']}")
                else:
                    print(f" -> [ALERTA] No s'ha trobat cap element d'aquesta consulta dins de {POBLACIO_FIXA}.")
                    
        elif resposta.status_code == 429:
            print(f" -> [ERROR 429] Bloqueig temporal per excés de peticions a la API.")
        elif resposta.status_code == 504:
            print(f" -> [ERROR 504] El servidor d'Overpass està saturat ara mateix.")
        else:
            print(f" -> [ERROR] Codi d'estat inesperat: {resposta.status_code}")
            
    except requests.exceptions.Timeout:
        print(f" -> [ERROR] Timeout de 420s. El servidor ha trigat massa a respondre.")
    except Exception as e:
        print(f" -> [ERROR] Error inesperat: {e}")

# Llegir el llistat de consultes del CSV
try:
    df = pd.read_csv('consultes.csv')
    total_files = len(df)
    
    for index, fila in df.iterrows():
        descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
        
        if index < total_files - 1:
            print(" -> Esperant 60 segons (1 minut) abans de la pròxima consulta...")
            time.sleep(60) 
            
except Exception as e:
    print(f"Error general en llegir el fitxer CSV: {e}")
