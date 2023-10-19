"""
Lagrer en JSON-dump av gjeldende datakatalog-versjon fra NVDB api LES
 """
import json
import requests
from datetime import datetime

def lagreDakat( miljo='PROD' ):
    """
    Lagrer JSON-fil med gjeldende datakatalogversjon hentet fra NVDB api LES 
    """

    if miljo.upper() == 'PROD': 
        url = 'https://nvdbapiles-v3.atlas.vegvesen.no/'
    elif miljo.upper() == 'TEST' or miljo.upper() == 'ATM': 
        url = 'https://nvdbapiles-v3.test.atlas.vegvesen.no/'
    elif miljo.upper() == 'UTV' or miljo.upper() == 'STM': 
        url = 'https://nvdbapiles-v3.utv.atlas.vegvesen.no/'
    else: 
        raise ValueError( f"Ukjent driftsmiljø: {miljo}, paramterer miljo= må være PROD, TEST eller UTV (evt ATM, STM)")
    
    headers = {'Accept' : 'application/json', 
               "X-Client" : "nvdbapiv3.py fra Nvdb gjengen, vegdirektoratet", 
             "X-Kontaktperson" : "jan.kristian.jensen@vegvesen.no" }

    # Henter statusinformasjon
    r = requests.get( url + '/status', headers=headers)
    if r.ok: 
        status = r.json()
        versjon = status['datagrunnlag']['datakatalog']['versjon']
        versjon = versjon.replace( '.', '_' )
    else: 
        raise ValueError( f"Klarte ikke hente statusinformasjon fra LES: {r.url}\n http {r.status_code} {r.text[0:500]}")
    

    # Henter datakatalog
    r = requests.get( url + '/vegobjekttyper', headers=headers, params={ 'inkluder' : 'alle' })
    if r.ok: 
        dakat = r.json()
    else: 
        raise ValueError( f"Klarte ikke hente datakatalog fra LES: {r.url}\n http {r.status_code} {r.text[0:500]}")

    filnavn =  f"datakatalog-{miljo}-{versjon}-{str( datetime.now())[0:10]}.json"
    print( f"Lagrer datakatalog {filnavn}")
    with open( filnavn, 'w') as fp: 
        json.dump( dakat, fp, indent=4, ensure_ascii=False )

if __name__ == '__main__': 

    lagreDakat( )
    # lagreDakat( miljo='TEST')
    # lagreDakat( miljo='UTV')