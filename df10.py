"""
Leser data fra og sender data til applikasjonen datafangst https://datafangst.atlas.vegvesen.no/

Se dokumentasjon på datafangst API her https://apiskriv.vegdata.no/datafangst/datafangst-api
"""
import json
import requests
from requests.auth import HTTPBasicAuth
import getpass 
from copy import deepcopy 
import os 

def hentPassord( user:str, api:str): 
    servernavn = [ x for x in api.split( '/' ) if 'datafangst' in x ]
    if len( servernavn ) == 1: 
        servernavn = servernavn[0]
    else: 
        servernavn = api 
    pw = getpass.getpass( f"{user}'s password for {servernavn}:")
    return pw 


def get_data( url:str, user='jajens', pw=None, geojson=False ): 
    """
    Gjør GET - forespørsel mot Datafangst og returnerer data 
    """

    if not pw: 
        hentPassord( user, url )

    if geojson: 
        headers = headers = { 'Content-Type' : 'application/geo+json', 'Accept' : 'application/geo+json' }
    else: 
        headers = headers = { 'Content-Type' : 'application/geo+json', 'Accept' : 'application/json' }

    r = requests.get( url, headers=headers, auth=HTTPBasicAuth( user, pw) )
    if r.ok: 
        data = r.json( )
        return data  
    else: 
        print( f"GET-kall feilet: HTTP {r.status_code} {r.text[0:500]}")

    return None 


def alleKontrakter(  url='https://datafangst.vegvesen.no/api/v1/contract/', user='jajens', pw=None ): 
    """
    Henter liste med kontrakter fra contracts-endepunktet
    """
    contracts = get_data( url, user=user, pw=pw )
    return contracts

def searchContracts( contractList:dict, substring:str): 
    """
    Finner subsett av kontrakter der 'substring' er en del av kontraktnavnet

    ARGUMENTS
        contractList:  dictionary fra datafangst API. Selve listen er i contractList['contracts'] 

        substring: text

    KEYWORDS: 
        N/A

    RETURNS 
        contractList etter filtrering     
    """
    filtrert = deepcopy ( contractList )

    if 'tekstfilter' in filtrert: 
        filtrert['tekstfilter'] += f" +> '{substring}'"
    else: 
        filtrert['tekstfilter'] = f"'substring'" 

    filtrert['contracts'] = [ x for x in contractList['contracts'] if substring.lower() in x['name'].lower() ] 

    maks_antall_utskrift=10
    if len( filtrert['contracts'] ) == 0: 
        print( f"Ingen treff på søketerm {substring} blant {len(contractList['contracts'])} kontrakter")
    elif len( filtrert['contracts'] ) < maks_antall_utskrift:
        print( f"{len( filtrert['contracts'] )} treff på {substring} blant {len(contractList['contracts'])} kontrakter" )
        for contract in filtrert['contracts']: 
            print( f"\t{contract['name']} {contract['id']}")
    else:
        print( f"{len( filtrert['contracts'] )} treff på {substring} blant {len(contractList['contracts'])} kontrakter, viser de {maks_antall_utskrift} første:" )
        sample = filtrert['contracts'][0:maks_antall_utskrift]
        for contract in sample: 
            print( f"\t{contract['name']} {contract['id']}")

    return filtrert 

def alleFeaturecollections( contractId:str, destination='NVDB', api='https://datafangst.vegvesen.no/api/v1/contract/', user='jajens', pw=None ):
    """
    henter liste med featureCollection fra kontrakt
    """

    data = get_data( api + contractId + '/featurecollection', user=user, pw=pw )        
    return data 


def lagreFeatureCollections( contractId:str, mappenavn:str, api='https://datafangst.vegvesen.no/api/v1/contract/', user='jajens', pw=None, **kwargs): 
    """
    Lagrer alle featureCollections på en kontrakt i angitt mappenavn 

    ARGUMENTS: 
        contractId : ID på kontrakt  

        mappenavn : tekst, mappenavn dit du lagrer mappene 

    KEYWORDS
        Samme som alleFeatureCollections 

    RETURNS 
        None 
    """

    data = alleFeaturecollections( contractId, api=api, user=user, pw=pw, **kwargs )
    metadata = get_data( api+contractId, user=user, pw=pw )
    print( f"{len(data['featureCollections'] )} feature collections på kontrakt {metadata['name']} {metadata['id']}, lagres til mappe {mappenavn} ")
    if not os.path.exists( mappenavn): 
        os.makedirs( mappenavn)

    for col in data['featureCollections']: 
        src = [ x for x in col['resources'] if 'src' in x ]
        url= src[0]['src']
        myGeo = get_data( url, user=user, pw=pw, geojson=True )
        status = get_data( url + '/status', user=user, pw=pw )

        # Legger på valideringsstatus
        for idx,feat in enumerate( myGeo['features']): 
            myGeo['features'][idx]['properties']['validationStatus'] = status['validationStatus']

        with open( os.path.join( mappenavn, col['id']+'.geojson' ), 'w' ) as fp:
            json.dump( myGeo, fp, indent=4, ensure_ascii=False  )





if __name__ == '__main__': 
    api = 'https://datafangst.vegvesen.no/api/v1/contract/'
    # Kontrakt som har problem: 
    frankContractId = '7877472b-190f-4898-9939-82915952e15f'
    pw = hentPassord( 'jajens', api)


    featureCollectionList = ['2143c586-d067-4ef3-824a-1483a6c9db86', '51006529-b1cc-467f-9391-74da2bd2380e', '839c7c9e-31ad-4430-b56a-4074399b021e', '9750b500-fce0-4073-b20d-a3088a1aeaf4', 'b73d64c9-1e62-4c67-a14d-61110457fa25' ]
    for featCol in featureCollectionList: 
        myStatus = get_data( api + frankContractId + '/featurecollection/' + featCol + '/status' , pw=pw)
        print( myStatus)

# '2143c586-d067-4ef3-824a-1483a6c9db86', 
# 'validationStatus': 'PENDING', 
# 'validationIssues': [{'severity': 'NOTABENE', 'code': 'KOORDINATER_TRANSFORMERT', 'message': 'Koordinater ble transformert til UTM33N.',
#                        'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '2143c586-d067-4ef3-824a-1483a6c9db86'}}, 
#                     {'severity': 'WARNING', 'code': 'STØRRE_ENN_ANBEFALT_MAKSIMUM', 'message': 'Verdien 60 for egenskapstype Timesregel, varighet (10952) er større enn anbefalt maksimumsverdi: 20',
#                       'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '2143c586-d067-4ef3-824a-1483a6c9db86', 'lineNo': 0, 
#                     'featureId': 'ab3eede8-e189-4578-814a-a3320f73bb03', 'attributeTypeId': 10952, 'featureTypeId': 45, 'featureAlias': 'bomstasjon'}}, 
#                     {'severity': 'WARNING', 'code': 'MANGLER_ANBEFALTE_EGENSKAPER', 'message': "Objektet, av typen Bomstasjon (45), mangler egenskaper med viktighet 'påkrevd, ikke absolutt': [Bomstasjonstype (9390)]", 
#                      'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '2143c586-d067-4ef3-824a-1483a6c9db86', 'lineNo': 0, 
#                     'featureId': 'ab3eede8-e189-4578-814a-a3320f73bb03', 'featureTypeId': 45, 'featureAlias': 'bomstasjon'}}, 
#                     {'severity': 'NOTABENE', 'code': 'VEGOBJEKTTYPE_UTENFOR_OBJEKTLISTE', 'message': 'Vegobjekttypen Bomstasjon (45) er ikke påkrevd i henhold til objektlista', 
#                      'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '2143c586-d067-4ef3-824a-1483a6c9db86', 'lineNo': 0,
#                     'featureId': 'ab3eede8-e189-4578-814a-a3320f73bb03', 'featureTypeId': 45, 'featureAlias': 'bomstasjon'}}, 
#                     {'severity': 'WARNING', 'code': 'DATACATALOG_VERSION_NOT_LATEST', 'message': 'Ikke siste datakatalogversjon',
#                       'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '2143c586-d067-4ef3-824a-1483a6c9db86', 'lineNo': 0, 'featureAlias': 'bomstasjon'}}], 
# 'featureIdMappings': [{'tag': 'bomstasjon', 'featureId': 'ab3eede8-e189-4578-814a-a3320f73bb03'}]}

#  '51006529-b1cc-467f-9391-74da2bd2380e', 
# 'validationStatus': 'PENDING', 
# 'validationIssues': [
#     {'severity': 'WARNING', 'code': 'STØRRE_ENN_ANBEFALT_MAKSIMUM', 'message': 'Verdien 60 for egenskapstype Timesregel, varighet (10952) er større enn anbefalt maksimumsverdi: 20', 
#     'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '51006529-b1cc-467f-9391-74da2bd2380e', 'lineNo': 0, 
#     'featureId': 'd307f806-b25a-482f-a635-4bd015be2bb5', 'attributeTypeId': 10952, 'featureTypeId': 45, 'featureAlias': 'bomstasjon'}}, 
#     {'severity': 'WARNING', 'code': 'MANGLER_ANBEFALTE_EGENSKAPER', 'message': "Objektet, av typen Bomstasjon (45), mangler egenskaper med viktighet 'påkrevd, ikke absolutt': [Bomstasjonstype (9390)]", 
#      'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '51006529-b1cc-467f-9391-74da2bd2380e', 'lineNo': 0, 
#         'featureId': 'd307f806-b25a-482f-a635-4bd015be2bb5', 'featureTypeId': 45, 'featureAlias': 'bomstasjon'}}, 
#         {'severity': 'WARNING', 'code': 'DATACATALOG_VERSION_NOT_LATEST', 'message': 'Ikke siste datakatalogversjon', 
#          'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '51006529-b1cc-467f-9391-74da2bd2380e', 'lineNo': 0, 
#         'featureAlias': 'bomstasjon'}}, 
#         {'severity': 'NOTABENE', 'code': 'VEGOBJEKTTYPE_UTENFOR_OBJEKTLISTE', 'message': 'Vegobjekttypen Bomstasjon (45) er ikke påkrevd i henhold til objektlista', 
#          'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '51006529-b1cc-467f-9391-74da2bd2380e', 'lineNo': 0, 
#         'featureId': 'd307f806-b25a-482f-a635-4bd015be2bb5', 'featureTypeId': 45, 'featureAlias': 'bomstasjon'}},
#      {'severity': 'NOTABENE', 'code': 'KOORDINATER_TRANSFORMERT', 'message': 'Koordinater ble transformert til UTM33N.', 
#       'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '51006529-b1cc-467f-9391-74da2bd2380e'}}], 
# 'featureIdMappings': [{'tag': 'bomstasjon', 'featureId': 'd307f806-b25a-482f-a635-4bd015be2bb5'}]}

# '839c7c9e-31ad-4430-b56a-4074399b021e', 
# 'validationStatus': 'ACCEPTED', 
# 'validationIssues': [
#     {'severity': 'NOTABENE', 'code': 'ATTRIBUTTVERDI_AUTOKORRIGERT', 'message': "Verdien '16.80' er korrigert til '16.8'", 
#      'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '839c7c9e-31ad-4430-b56a-4074399b021e', 'lineNo': 0, 
#     'featureId': 'd47bc9c4-6937-461d-a76d-2630e2a89757', 'featureTypeId': 79, 'featureAlias': 'Stikkrenne/Kulvert (13-10-2023 12:12:16)'}},
#  {'severity': 'NOTABENE', 'code': 'MANGLER_BETINGET_PÅKREVDE_EGENSKAPER', 
#   'message': "Objektet, av typen Stikkrenne/Kulvert (79), mangler egenskaper med viktighet 'betinget': [Tilknyttet lukka dren (1941), Har innløpsrist (1923), Bredde, innvendig (4548), Høyde, innvendig (4549), Varmekabler (1832), Rehabilitering (10766), Gjennomløp for elv/bekk (10223), Diameter, innvendig (3113)]", 'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '839c7c9e-31ad-4430-b56a-4074399b021e', 'lineNo': 0, 'featureId': 'd47bc9c4-6937-461d-a76d-2630e2a89757', 'featureTypeId': 79, 'featureAlias': 'Stikkrenne/Kulvert (13-10-2023 12:12:16)'}}, {'severity': 'NOTABENE', 'code': 'KOORDINATER_TRANSFORMERT', 'message': 'Koordinater ble transformert til UTM33N.', 'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '839c7c9e-31ad-4430-b56a-4074399b021e'}}, {'severity': 'WARNING', 'code': 'MANGLER_ANBEFALTE_EGENSKAPER', 'message': "Objektet, av typen Stikkrenne/Kulvert (79), mangler egenskaper med viktighet 'påkrevd, ikke absolutt': [Type innløp (1939), Type utløp (1940), Bruksområde (6981), Tverrsnittsform (6984), Materialtype (6983), Etableringsår (4556), Overfylling innløp (10224)]", 'location': {'contractId': '7877472b-190f-4898-9939-82915952e15f', 'featureCollectionId': '839c7c9e-31ad-4430-b56a-4074399b021e', 'lineNo': 0, 
#  'featureId': 'd47bc9c4-6937-461d-a76d-2630e2a89757', 'featureTypeId': 79, 'featureAlias': 'Stikkrenne/Kulvert (13-10-2023 12:12:16)'}}], 
# 'featureIdMappings': [{'tag': 'Stikkrenne/Kulvert (13-10-2023 12:12:16)', 'featureId': 'd47bc9c4-6937-461d-a76d-2630e2a89757'}]}

#  '9750b500-fce0-4073-b20d-a3088a1aeaf4', 'validationStatus': 'ACCEPTED', 'validationIssues': [], 'featureIdMappings': []} => TOMT OBJEKT??? 
# 
# 
# 'b73d64c9-1e62-4c67-a14d-61110457fa25', 'validationStatus': 'PROCESSING', 'validationIssues': [], 'featureIdMappings': []} => Stikkrenne over kum
# Egenskapverdier: 10223: Nei, 10224: 0, 1832: Nei, 1923: Ja, 1939: Kum over stikkrenne, 1940: Kum, 1941: Nei, 6981: Vann, 6983: Betong, 6984: Sirkulær

