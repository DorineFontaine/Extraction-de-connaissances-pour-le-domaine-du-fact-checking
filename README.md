##Context
As part of the TER project, we had the opportunity to work on the following topic: "In search of fake news". Our group is made up of three students: Sara Belkasmy, Redouane Asma and Dorine Fontaine. Our research was supervised by teacher Konstantin Todorov.

Our subject was directly related to fact-checking sites. Our task was to compile information from these sites in the form of csv files to feed the "CLAIMSKG" knowledge base created by teachers from the Faculty of Science and researchers from several international teams.

To enrich the CLAIMSKG database as much as possible, each member of the group has set himself the task of finding new fact-checking sites to add to the database, if possible in a variety of languages.

We have therefore chosen to deal with the following sites: Mimikama, Correctiv German sites, Logically,Healthfeedback, Usatoday English sites, HoaxBuster a French site.

## ClaimsKG
This project constitutes the web scraping component of ClaimsKG that crawls fact checking sites (mostly taken from https://www.poynter.org/international-fact-checking-network-fact-checkers-code-principles, which holds a list of reliable fact-checking sites) and generates a CSV file with a dump of the extracted information. 

This project is a fork of https://github.com/vwoloszyn/fake_news_extractor that has been refactored and repurposed for the specific needs of ClaimsKG. Most of the original extractors for English-language fact-checking sites have been reimplemented under a new architecture and are the only ones that are functional (see list below). Althrough the original extractors for Portuguese language and German language sites are still present, they haven't yet been integrated, please refer to the orignal implementation if you need to use those. 

### English

- Fullfact - https://fullfact.org/
- Snopes - https://www.snopes.com/
- Politifact - http://www.politifact.com/
- TruthOrFiction - http://TruthOrFiction.com
- Checkyourfact - http://checkyourfact.com
- FactsCan - http://factscan.ca/
- AfricaCheck - https://africacheck.org/
- AAP FactCheck - https://factcheck.aap.com.au/
- EU vs Disinfo (Disinformation Cases) - https://euvsdisinfo.eu/disinformation-cases/
- AFP Fact Check - https://factcheck.afp.com/

See the ClaimsKG dataset website for statistics (https://data.gesis.org/claimskg/site)

See overview with example files at WIKI: https://github.com/claimskg/claimskg-extractor/wiki

### French

- AFP Factuel - https://factuel.afp.com/

## Features Extracted

- "Claim"			: Textual statement of the claim which is being verified
- "Credibility"			: Truth rating provided by the respective sites in its original form
- "URL"				: URL of the corresponding source page
- "body"			: Description provided by the source article about why the claim is true or false
- "Date"	: 		: Date when the claim was made. 
- "Referred Links"		: References used for verifying the claim.
- "Tags"			: Set of tags or topics provided by the fact checking site.
- "Normalized Credibility"	: FALSE, TRUE, MIXED, OTHER

This version of the extractor doesn't annotate the description and claim with entities on its own, there is a consecutive step to add annotations to the CSV files with TagMe (see tagme fork in the claimskg project group). 

## Normalizing truth values (ratings) across fact-checking websites

Given the varied rating schemes used by the fact-checking websites, where individual labels often are hard to objectively apply or interpret, we apply a simple normalized rating scheme consisting of four basic categories that can be mapped in a consensual way to all existing rating schemes: TRUE, FALSE, MIXTURE, OTHER. We provide full correspondence tables here: https://goo.gl/Ykus98

## Prerequisites
This reimplementation runs on Python3.5+. 
Redis is used for caching HTTP querries in order to allow faster resuming of extractions in case of failure and for a faster iterative development of new extractors. Please make sure to have a Redis instance (default parameters) running on the machine that runs the extractor. 
Expected package dependencies are listed in the "requirements.txt" file for PIP, you need to run the following command to get dependencies:
```
pip install -r requirements.txt
```


## Examples of usage

### Command-line usage
Export claims to a csv file named "output_got.csv".
- Get help use  [under implementation]
```
    python Exporter.py -h
```
- Get claims by website
```
    python Exporter.py --website fullfact,snopes
```
- limit of number of claims
```
    python Exporter.py --maxclaims 30
```

### Removing cached sites: 
If you wish to remove the cache entries relative to a particular site, you can use the following command, where SITENAME should be replaced with the site's name as listed above.

```shell 
redis-cli --raw keys "http://*SITENAME*" | xargs redis-cli --raw del - 
```



# Intégration

<https://github.com/eleutheromastrophimatique/ClaimsExtractor-/tree/master/claim_extractor/extractors> 

- eufactcheck.eu
- polygraph.info
- factograph.info

<https://gitlab.info-ufr.univ-montp2.fr/e20160008449/TER-M1_FullFact/tree/master> (fullfact)

<https://github.com/ImaneLamriou/TER/tree/master/extractors>

- afrikacheck FR
- newtral
- pagellapolitika

<https://github.com/massykezzoul/claims-checking/tree/master/src/websites>





