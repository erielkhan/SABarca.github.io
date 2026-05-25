import pandas as pd
import requests
import os
import time
from datetime import datetime

POBLACIO_FIXA = 'Sant Andreu de la Barca'

def descarregar_geojson(nom, consulta_csv):
    # Eliminamos las comillas simples de los extremos que pusimos en el CSV para proteger el texto
    consulta_neta = consulta_csv.strip().strip("'").strip('"')
    
    # Reemplazamos la palabra clave (area); por el objeto nativo mapeado de Sant Andreu de la Barca
    consulta_filtrada = consulta_neta.replace('(area)', '(area.municipi)')
    
    # Reconstruimos la estructura Overpass pura respetando tu sintaxis exacta
    consulta_completa = f"""[out:json][timeout:400][maxsize:2147483648];
area["name"="{POBLACIO_FIXA}"]["admin_level"="8"]->.municipi;
(
  {consulta_filtrada}
);
out body;
>;
out skel qt;"""
    
    print(f"\n>>> ENVIANDO CONSULTA A OVERPASS PARA: {nom}")
    print(consulta_completa)
    print("-" * 50)
    
    url = "https://overpass-api.de/api/interpreter"
    
    if not os.path.exists('dades'):
        os.makedirs('dades')
    ruta_fitxer = f"dades/{nom}.geojson"
    
    try:
        headers = {
            'User-Agent': 'GitHubActions-OSM-Downloader/1.2',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Enviamos usando POST pasándolo en el cuerpo del mensaje, la forma más robusta para consultas complejas
        resposta = requests.post(url, data={'data': consulta_completa}, headers=headers, timeout=430)
        
        if resposta.status_code == 200:
            dades_json = resposta.json()
            
            if "elements" in dades_json and len(dades_json["elements"]) > 0:
                if os.path.exists(ruta_fitxer):
                    os.remove(ruta_fitxer)
                
                with open(ruta_fitxer, "w", encoding='utf-8') as f:
                    f.write(resposta.text)
                msg = f"[OK] {nom}: Guardado con éxito ({len(dades_json['elements'])} elementos)."
                print(msg)
                return msg
            else:
                if "remark" in dades_json:
                    msg = f"[ERROR SINTAXIS] {nom}: {dades_json['remark']}"
                else:
                    msg = f"[ALERTA] {nom}: La consulta no ha devuelto ningún elemento en {POBLACIO_FIXA}."
                print(msg)
                return msg
        else:
            msg = f"[ERROR HTTP {resposta.status_code}] El servidor Overpass rechazó la petición. Detalles: {resposta.text[:200]}"
            print(msg)
            return msg
            
    except Exception as e:
        msg = f"[ERROR CONEXIÓN] {nom}: {str(e)}"
        print(msg)
        return msg

# Ejecución principal
try:
    df = pd.read_csv('consultes.csv')
    total_files = len(df)
    resultats = []
    
    for index, fila in df.iterrows():
        resultat = descarregar_geojson(fila['nom_fitxer'], fila['consulta'])
        resultats.append(resultat)
        
        if index < total_files - 1:
            print("Esperando 15 segundos de cortesía entre consultas...")
            time.sleep(15)
            
    with open("dades/log_execucio.txt", "w", encoding='utf-8') as log:
        log.write(f"Última ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("\n".join(resultats))

except Exception as e:
    print(f"Error general en el flujo principal: {e}")
