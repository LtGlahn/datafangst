"""
Eksempel - filopplasting til DF20 
"""

with open( 'fiktivtTrafikkspeil.geojson' ) as f:
    trafspeil = json.load( f )
import json
with open( 'fiktivtTrafikkspeil.geojson' ) as f:
    trafspeil = json.load( f )
import df20
header_token  = df20.login( user='jajens' )
header_token  = df20.login( username='jajens' )
kontrakt = '06842552-1295-403b-afeb-b0270d0f0872'
df20.lastOppGeojson( trafspeil, kontrakt, 'trafikkspeil.geojson', header_token )