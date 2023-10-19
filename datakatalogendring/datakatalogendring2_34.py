import json
import requests
import pandas as pd

if __name__ == '__main__': 
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
                elif 'vegobjekttypeid' in egenskap:
                    enRelasjon['datterObjektTypeId'] = egenskap['vegobjekttypeid']
                else: 
                    print( f"Fant ikke datter-objekttype i denne informasjonen:")
                    print( json.dumps( egenskap, indent=4, ensure_ascii=False ))

                resultater.append( enRelasjon )

    # Konverterer til dataframe
    # 1017 rader
    dagensRelasjoner = pd.DataFrame( resultater )

    # Liste fra Vilhelm med dem som er sletta, 443 rader
    sletta_regneark = pd.read_excel( 'vilhelm_2_34_relasjoner_som_er_sletta.xlsx', sheet_name='Ark2' )
    sletta_regneark.rename( columns={'VT_Id' : 'morObjTypeId', 'VT_Id.1' : 'datterObjektTypeId'}, inplace=True )
    sletta_regneark['mulig_typeid_1'] = sletta_regneark['TS_Id'] + 200000
    sletta_regneark['mulig_typeid_2'] = sletta_regneark['TS_Id'] + 220000
    sletta_regneark['dakat_versjon'].fillna( '', inplace=True )
    # sletta_regneark[ sletta_regneark['dakat_versjon'].str.contains('2.34') ]

    # Liste fra Datafangst databasen laget med backup fra torsdag for to uker siden
    # MariaDB [datafangst]> select distinct type_id from feature_association2; 
    # 574 rader 
    datafangst_relasjonstyper = pd.read_csv( 'relasjonstyper_frabackup_v2_34.csv' )

    # # Kobler mariadb-relasjonene med dagens relasjoner, finner differansen
    # joined = pd.merge( datafangst_relasjonstyper, dagensRelasjoner, on='type_id', how='inner'  )
    # UBRUKELIG, vi bruker kun et lite subsett av alle mulige relasjoner. Får 9 treff: 
        #     type_id  morObjTypeId          morObjTypeNavn                    relasjonNavn     datatype  datterObjektTypeId
        # 200805           241                Vegdekke           Assosiert Entreprenør  Assosiasjon                 608
        # 201637            67               Tunnelløp     Assosiert Tunnelovervåkning  Assosiasjon                 776
        # 201786            89            Signalanlegg          Assosiert Styreapparat  Assosiasjon                 456
        # 200806           226                 Bærelag           Assosiert Entreprenør  Assosiasjon                 608
        # 200833           627          Referansepunkt       Assosiert Referansestolpe  Assosiasjon                  98
        # 200821           609           Armeringsnett           Assosiert Entreprenør  Assosiasjon                 608
        # 201617           592       Nedbøyningsmåling  Assosiert Nedbøyningsmåleserie  Assosiasjon                 774
        # 200835           629  Vegdekke, flatelapping           Assosiert Entreprenør  Assosiasjon                 608
        # 202166           199                    Trær             Assosiert Plantekum  Assosiasjon                 931


    # sletta_joined = pd.merge( dagensRelasjoner, sletta_regneark, on=['morObjTypeId', 'datterObjektTypeId'])
    # TOMT RESULTAT (og det er jo fornuftig)

    # Finner overlapp mellom eksisterende datafangst-relasjoner og dem som Vilhelm har sletta 
    slettekandidat1 = pd.merge( sletta_regneark, datafangst_relasjonstyper, left_on='mulig_typeid_1', right_on='type_id', how='inner' )
    slettekandidat2 = pd.merge( sletta_regneark, datafangst_relasjonstyper, left_on='mulig_typeid_2', right_on='type_id', how='inner' )
    slettekandidat = pd.concat( [ slettekandidat1, slettekandidat2] )


    # Skriver ut oversikt over de objekttypene som skal slettes
    col = ['morObjTypeId', 'VT_navn', 'datterObjektTypeId', 'VT_navn.1', 'TS_Id', 'dakat_versjon', 'A og B gyldig', 'SHT_Navn',  'type_id']
    print( f"Relasjoner som skal slettes fra gamle Datafangst:")
    print( slettekandidat[col])

    sletteTypeId =  slettekandidat['type_id'].to_list()  
    
    


    # Konstruerer SQL-setning 
    print( f"SQL-setning for å slette de ugyldige relasjonene:")
    print(f"start trasaction; delete from feature_association2 where type_id in ('{','.join( [ str(x) for x in sletteTypeId ] )})")

