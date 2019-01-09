# HEREqgis
HEREqgis is a python based plugin for QGIS that combines different traffic/routing/geocoding actions in one plugin. 
With HEREqgis you can geocode single and multiple addresses, find routes, places of interests around a or multiple locations and many more.
This plugin is designed to work in QGIS 3.4 and above.

## Contents and Usage
The HEREqgis plugin comes with different analytical tools as the here API povides different endpoints:
+ Geocode

   With the three tools you can geocode a single address, choose a point layer / delimited layer with an address field or a layer with dedicated address-content fields (like street, city, zip code, etc.). You will receive a single point memory layer with found addresses, quality indicators and the original searched address/address content.
   ![Geocoding Tab HEREqgis](https://i.imgur.com/IC0Z7B7.png)
+ Routing

   Currently the toolset supports one-to-one routing ("manual input") using different routing types (fast, short, balanced) and routing modes (pedestrian, bicycle, car, ...). The reuslt will be added as a memory layer to your QGIS project.
   ![Routing Tab HEREqgis](https://i.imgur.com/wzydRrk.png)
+ POI search

   Using the POI search you can query the HERE API for places of interest around an address/coordinate pair in a given vicinity (radius). The API will respond with a maximum of 100 search results in the categories you queried.
   ![POI Search Tab HEREqgis](https://i.imgur.com/2mzqDDw.png)

## Credentials
The plugin needs to have credentials from HERE. Therefore you need to register a freemium account (free of charge at [HERE.com](https://developer.here.com/). 
Fill in the generated app ID and app code in the xcredentials-tab of the plugin.

![Credential Tab HEREqgis](https://i.imgur.com/8kOkAHD.png)

The credentials will be stored for convenience in a file called credentials.json in the *cred* subfolder of your HEREqgis plugin folder (linux: */home/USER/.local/share/QGIS/QGIS3/profiles/default/python/plugins* / win: *C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins*). 

## TOS / Usage
Please take a look at the [*Terms and Contitions*](https://developer.here.com/terms-and-conditions) when using the Freemium plan (as most people might want to...).
Furthermore:
According to the [*Acceptable Use Policy*](https://legal.here.com/en-gb/terms/acceptable-use-policy) you're not allowed to store the results. Yet you can use them *cached* aka work with the memory layer for 30days max.
Forther QUestions and Answers can be found at the [*FAQ*](https://developer.here.com/faqs) page as well as the [main page of the freemium model](https://go.engage.here.com/freemium)
