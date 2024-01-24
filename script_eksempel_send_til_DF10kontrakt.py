# Arbeidseksempel, opplasting av geojson-data til DF-kontrakt

import json
import getpass
import requests
from requests.auth import HTTPBasicAuth


if __name__ == '__main__': 


    with open( 'bomst_nyeNedreGlomma.geojson' ) as f:
        bomst = json.load( f )
    kontrakt = 'e93b459b-a2c4-4e6b-bb21-0d7fe3ae0736'

    dfApi = 'https://datafangst.vegvesen.no/api/v1/contract/'

    url = dfApi + kontrakt +  '/featurecollection'
    username = 'jajens'
    pw = getpass.getpass()

    r = requests.post( url, headers=headers, auth=HTTPBasicAuth(username, pw), data=json.dumps( bomst ) )