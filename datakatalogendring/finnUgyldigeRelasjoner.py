"""
Sjekker om vi har relasjonstyper i datafangst-databasen som IKKE finnes i gjeldende datakatalogversjon 

Leser en tekstfil med resultatet fra databasespørringen `select distinct type_id from feature_association2;`
og sammenligner med relasjonstyper i gjeldende datakatalog
"""

import json
import requests
import pandas as pd

if __name__ == '__main__': 

    # Leser de relasjonstypene som finnes i datafangst databasen 
    harDisse = pd.read_csv( 'select_distinct_relasjonstyper_2024-07-04.txt', header=None, names=['df10relasjoner'] )

    dakaturl = 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper'
    alleTyper = requests.get( dakaturl, headers={'Accept' : 'application/json'},
                                params={'inkluder' : 'egenskapstyper'}).json()

    resultater = []
    for objType in alleTyper:
        for egenskap in objType['egenskapstyper']: 
            if 'Assosiert' in egenskap['navn']:
                enRelasjon = {  'morObjTypeId'      : objType['id'],
                                'morObjTypeNavn'    : objType['navn'], 
                                'type_id'           : egenskap['id'],
                                'relasjonNavn'      : egenskap['navn'],
                                'datatype'          : egenskap['datatype']
                }
                if 'innhold' in egenskap: 
                    enRelasjon['datterObjektTypeId'] = egenskap['innhold']['vegobjekttypeid']
                    enRelasjon['datatype']           = egenskap['innhold']['datatype']
                    enRelasjon['type_id']            = egenskap['innhold']['id']
                elif 'vegobjekttypeid' in egenskap:
                    enRelasjon['datterObjektTypeId'] = egenskap['vegobjekttypeid']
                else: 
                    print( f"Fant ikke datter-objekttype i denne informasjonen:")
                    print( json.dumps( egenskap, indent=4, ensure_ascii=False ))

                resultater.append( enRelasjon )

    # Konverterer til dataframe
    dagensRelasjoner = pd.DataFrame( resultater )


    # Finner relasjoner som ikke er gyldige lenger: 
    ugyldige = harDisse[ ~harDisse['df10relasjoner'].isin( dagensRelasjoner['type_id'] ) ]


    sletteTypeId =  ugyldige['df10relasjoner'].to_list()  
    
    
    # Konstruerer SQL-setning 
    print( f"SQL-setning for å slette de ugyldige relasjonene:")
    print(f"start transaction; delete from feature_association2 where type_id in ({','.join( [ str(x) for x in sletteTypeId ] )})")

