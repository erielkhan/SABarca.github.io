import pandas as pd
import requests
import os
import time
from datetime import datetime

POBLACIO_FIXA = 'Sant Andreu de la Barca'

def descarregar_geojson(nom, etiqueta_csv):
    # Netegem potencials espais o punts i comes sobrants que vinguin del CSV
    etiqueta = etiqueta_csv.strip().replace(';', '')
    
    # Reconstruïm la consulta d'Overpass perfectament formatada
    consulta_completa = f"""[out:json][timeout:400][maxsize:2147483648];
area["name"="{POBLACIO_FIXA}"]["admin_level"="8"]->.municipi;
(
  {etiqueta}(area.municipi);
);
out body;
>;
out skel qt;"""
    
    print(f"\n--- S'ESTÀ ENVIANT AQUESTA CONSULTA PER A: {nom} ---")
    print(consulta_completa)
    print("---------------------------------------------------\n")
    
    url = "https://overpass-api.de/api/interpreter"
    
    if not os.path.exists('dades'):
        os.makedirs('dades')
    ruta_fitxer = f"dades/{nom}.geojson"
    
    try:
        resposta = requests.get(url, params={'data': consulta_completa}, timeout=420)
        
        if resposta.status_code == 200:
            dades_json = resposta.json()
            
            # Comprovem si realment Overpass ha trobat coses
            if "elements" in dades_json and len(dades_json["elements"]) > 0:
                if os.path.exists(ruta_fitxer):
                    os.remove(ruta_fitxer)
                
                with open(ruta_fitxer, "w", encoding='utf-8') as f:
                    f.write(resposta.text)
                msg = f"[OK] {nom}: Creat correctament amb {len(dades_json['elements'])} elements."
                print(msg)
                return msg
            else:
                if "remark" in dades_json:
                    msg = f"[ALERTA] {nom}: Error de sintaxi del servidor: {dades_json['remark']}"
                else:
                    msg = f"[ALERTA] {nom}: La consulta no ha tornat cap element dins de {POBLACIO_FIXA}."
                print(msg)
                return msg
        else:
            msg = f"[ERROR HTTP {resposta.status_code}] No s'ha pogut descarregar {nom}."
            print(msg)
            return msg
            
    except Exception as e:
        msg = f"[ERROR CRÍTIC] {nom}: {str(e)}"
        print(msg)
        return msg

# Execució principal
try:
    df = pd.read_csv('consultes.csv')
    total_files = len(df)
    resultats = []
    
    for index, fila in df.iterrows():
        resultat = descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
        resultats.append(resultat)
        
        if index < total_files - 1:
            print("Esperant 60 segons de seguretat...")
            time.sleep(60)
            
    # FORÇAR CANVI AL REPOSITORI: Guardem un historial de l'execució
    # Així, encara que Overpass falli, GitHub Actions sempre tindrà un fitxer modificat per pujar (push)
    with open("dades/log_execucio.txt", "w", encoding='utf-8') as log:
        log.write(f"Última execució: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("\n".join(resultats))

except Exception as e:
    print(f"Error general: {e}")
