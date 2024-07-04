# Ugyldige relasjonstyper i gamle datafangst

Kode for å finne hvilke typer relasjonser som må vaskes vekk i gamle datafangst ved endringer i datakatalog. 

Ved datakatalog-oppdatering versjon 2_34 var det litt styr med regneark fra Vilhelm og sånn. 

Nå har vi en enklere oppskrift: Med SQL-spørringen `select distinct type_id from feature_association2` får vi svar på hvilke relasjonstyper som finnes. Resultatet lagres som en tekstfil, en linje per relasjonstype. Scriptet `finnUgyldigeRelasjoner.py` leser denne filen og sammenligner med gjeldende datakatalog. Hvis vi har ugyldige relasjonstyper i databasen så vil scriptet gi deg SQL-setningen for å fjerne dem, eksempel 

```sql  
delete from feature_association2 where type_id in (201833,201830,200589)
```


