import pandas as pd
import requests
import os
import time

def descarregar_geojson(nom, consulta):
    # CONFIGURACIÓ DE TIMEOUT A 400 SEGONS:
    # [timeout:400] -> Donem 400 segons al servidor d'Overpass per processar la teva consulta.
    # [maxsize:2147483648] -> Mantenim la memòria del servidor a 2GB per a consultes massives.
    consulta_completa = f"[out:json][timeout:400][maxsize:2147483648];{consulta}out body;>;out skel qt;"
    url = "https://overpass-api.de/api/interpreter"
    
    if not os.path.exists('dades'):
        os.makedirs('dades')
    ruta_fitxer = f"dades/{nom}.geojson"
    
    print(f"Processant {nom}...")
    
    try:
        # timeout=420 -> El script de Python esperarà fins a 420 segons a que el servidor respongui
        # abans de donar la connexió per perduda.
        resposta = requests.get(url, params={'data': consulta_completa}, timeout=420)
        
        if resposta.status_code == 200:
            dades_json = resposta.json()
            
            # Validació del contingut del JSON
            if "elements" in dades_json and len(dades_json["elements"]) > 0:
                if os.path.exists(ruta_fitxer):
                    os.remove(ruta_fitxer)
                
                with open(ruta_fitxer, "w", encoding='utf-8') as f:
                    f.write(resposta.text)
                print(f" -> [OK] Actualitzat correctament ({len(dades_json['elements'])} elements trobats).")
            else:
                if "remark" in dades_json:
                    print(f" -> [ALERTA] El servidor ha rebutjat la consulta. Missatge: {dades_json['remark']}")
                else:
                    print(f" -> [ALERTA] La consulta no ha tornat cap element. Revisa les coordenades o etiquetes.")
                    
        elif resposta.status_code == 429:
            print(f" -> [ERROR 429] Estàs enviant masses peticions seguides. El servidor t'ha bloquejat temporalment.")
        elif resposta.status_code == 504:
            print(f" -> [ERROR 504] El servidor d'Overpass està completament saturat. Torna-ho a provar més tard.")
        else:
            print(f" -> [ERROR] Codi d'estat inesperat: {resposta.status_code}")
            
    except requests.exceptions.Timeout:
        print(f" -> [ERROR] S'ha esgotat el temps d'espera crític de Python (Timeout de 420s). La consulta és excessivament pesada.")
    except Exception as e:
        print(f" -> [ERROR] Error inesperat: {e}")

# Llegir el llistat de consultes del CSV
try:
    df = pd.read_csv('consultes.csv')
    total_files = len(df)
    
    for index, fila in df.iterrows():
        descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
        
        # Si NO és l'última línia del CSV, fem la pausa d'1 minut
        if index < total_files - 1:
            print(" -> Esperant 60 segons (1 minut) abans de la pròxima consulta per cortesia amb el servidor...")
            time.sleep(60) 
            
except Exception as e:
    print(f"Error general en llegir el fitxer CSV: {e}")
