"""
Håndtere kommunikasjon (opp-og nedlasting DF20)
"""
import requests
import getpass
import json 
from copy import deepcopy 

def login( username=None,  pw=None, brukertype='ANSATT', miljo='TEST' ):
    """
    Logger inn i nye Datafangst (DF2.0). Returnerer http header til bruk i senere API-kall
    """

    if miljo.upper() in ['TEST', 'ATM' ]: 
        authapi = 'https://nvdbauth.test.atlas.vegvesen.no/api/v1/auth/autentiser'
    elif miljo.upper() in ['PROD', 'PRODUKSJON' ]: 
        authapi = 'https://nvdbauth.atlas.vegvesen.no/api/v1/auth/autentiser'
    else: 
        raise NotImplementedError(f"Har ikke implementert støtte for miljø {miljo} ennå")

    innlogging_headers =  { 'X-Client' : 'LtGlahn python' }

    if not username: 
        username = getpass.getpass( 'Ditt brukernavn')

    if not pw: 
        pw = getpass.getpass( f"Passord for bruker {username} i {authapi}:> ")
    
    innlogging_body    =  {'brukernavn' : username, 'brukertype' : brukertype, 'passord' : pw  }
    r_innlogging = requests.post( authapi, headers=innlogging_headers, json=innlogging_body  )
    if r_innlogging.ok: 
        print( "SUKSESS, vi er logget inn")
        id_token = r_innlogging.json()
        # MERK MELLOMROM mellom 'Bearer' og id_token  
        df_headers =  { 'X-Client': 'LtGlahn python',
                        'Authorization' : 'Bearer' + ' ' + id_token['id_token'] }
        return df_headers 
    else: 
        print( f"Innlogging feilet: http {r_innlogging.status_code} {r_innlogging.text}" )
        return None 

    
def hentKontrakter( header_med_token:dict, apiUrl ='https://datafangst-api-gateway.test.atlas.vegvesen.no/api/v2/'  ):
    """
    Henter liste med de kontraktene du har tilgang til 
    """
    pass


def lastOppGeojson( myGeoJson:dict, kontrakt:str, filnavn:str, header_med_token:dict, destination='NVDB', apiUrl = 'https://datafangst-api-gateway.test.atlas.vegvesen.no/api/v2/' ): 
    """
    Laster opp geojson på kontrakt. 

    ARGUMENTS
        myGeoJson : dict, featureCollection med geojson features 

        kontrakt : str, ID til kontrakten

        filnavn : str, filnavnet denne fila (featureCollection) skal ha

        header_med_token : dict med http header informasjon, fås fra login-funksjon
    """

    geojson_as_str = json.dumps( myGeoJson )

    myHeaders = deepcopy( header_med_token )
    myHeaders['Content-Type'] = 'application/geojson'
    myHeaders['X-FILNAVN'] = filnavn

    params={'destination' : destination }

    url = apiUrl + 'kontrakter/' + kontrakt + '/filer/kropp'

    r = requests.post( url, data=geojson_as_str, params=params, headers=myHeaders )
    if r.ok: 
        print( f"Fil {filnavn} lastet opp på kontrakt {kontrakt}")
    else: 
        print( f"Opplasting feiler: HTTP {r.status_code} {r.text}")


def godkjennFiler( kontrakt:str, filnavn:str, header_med_token:dict, apiUrl = 'https://datafangst-api-gateway.test.atlas.vegvesen.no/api/v2/' ): 
    """
    Godkjenner fil(er) på kontrakt

    ARGUMENTS: 
        kontrakt : str, ID til kontrakten 

        filnavn : str, filnavn på den eller de filen(e) som skal godkjennes (komma mellom filnavnene hvis det er flere)

        header_med_token : dict med http header informasjon, fås fra login-funksjonen

    KEYWORDS: 
        apiurl : str, lenke til riktig API miljo 
    """
    myHeaders = deepcopy( header_med_token )
    myHeaders['Content-Type'] = 'application/json'

    url = apiUrl + 'kontrakter/' + kontrakt + '/filer/godkjenn'
    payload = filnavn.split( ',')  # Blir til en liste med tekst. 
    payload = json.dumps( payload )

    r = requests.patch( url, payload,  headers=myHeaders )
    if r.ok: 
        print( f"Godkjente filer: {filnavn} på kontrakt {kontrakt}")
    else: 
        print( f"Godkjenning av filer feiler: HTTP {r.status_code} {r.text}")
