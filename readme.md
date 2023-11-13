# Hqgis
Hqgis is a python based plugin for QGIS that offers access to the [HERE API](https://developer.here.com/) and combines different traffic/routing/geocoding actions in one plugin.
With Hqgis you can geocode single and multiple addresses, find routes, places of interests around a or multiple locations and many more.
This plugin is designed to work in QGIS 3.4 and above.

## Sponsors
Thank you: 
@zoefSmoelt 

## Contents and Usage
The Hqgis plugin comes with different analytical tools as the HERE API povides different endpoints:
+ Geocode

   With the three tools you can geocode a single address, choose a point layer / delimited layer with an address field or a layer with dedicated address-content fields (like street, city, zip code, etc.). You will receive a single point memory layer with found addresses, quality indicators and the original searched address/address content.
   ![Geocoding Tab Hqgis](https://i.imgur.com/f1KV0NL.png)
+ Routing

   Currently the toolset supports one-to-one routing ("manual input") using different routing types (fast, short, balanced) and routing modes (pedestrian, bicycle, car, ...). The reuslt will be added as a memory layer to your QGIS project.
   ![Routing Tab Hqgis](https://i.imgur.com/vJZQSFn.png)
+ POI search

   Using the POI search you can query the HERE API for places of interest around an address/coordinate pair in a given vicinity (radius). The API will respond with a maximum of 100 search results in the categories you queried.
   ![POI Search Tab Hqgis](https://i.imgur.com/7ALhD7e.png)

+ Isochrone Analysis

   Isochrones, or lines of equal (travel) times are possible to calculated using different modes and types as well as for different times of the day. This can be done on a single address/map point or using a point layer. The result will be color coded (categorized) in QGIS in red (long travel times/distances) to grenn (short travel times/distances). Find some nice examples at [Topi Tjukanovs Homepage](https://tjukanov.org/vintage-isochrones/).  
   ![Isochrones in HQGIS](https://i.imgur.com/pX9qEeJ.png)


## Installation
Currently the plugin is only hosted here on github as the version is premature.
If you want to use it in QGIS, please download the repository and place the content of the zip in your python plugins folder (linux: */home/USER/.local/share/QGIS/QGIS3/profiles/default/python/plugins* / win: *C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins*). You can also install it directly in QGIS using the [plugin from ZIP option](https://gis.stackexchange.com/questions/302196/downloading-and-saving-plugins-for-qgis-3-4)

## Credentials
The plugin needs to have credentials from HERE. Therefore you need to register at least a freemium account (free of charge at [HERE.com](https://developer.here.com/) by creating a project and generate a REST API Key if not already generated.
Fill in the generated API Key in the credentials-tab of the plugin and click on "save credentials".

![Credential Tab Hqgis](https://i.imgur.com/IPvR5LV.png)

The credentials will be stored for convenience in a file called credentials.json in the *creds* subfolder of your Hqgis plugin folder (linux: */home/USER/.local/share/QGIS/QGIS3/profiles/default/python/plugins* / win: *C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins*).

## TOS / Usage
Please take a look at the [*Terms and Contitions*](https://developer.here.com/terms-and-conditions) when using the Freemium plan (as most people might want to...).
Furthermore:
According to the [*Acceptable Use Policy*](https://legal.here.com/en-gb/terms/acceptable-use-policy) you're not allowed to store the results. Yet you can use them *cached* aka work with the memory layer for 30 days max.
Further Questions and Answers can be found at the [*FAQ*](https://developer.here.com/faqs) page as well as the [main page of the freemium model](https://go.engage.here.com/freemium).

## Known Limitations
The plugin is using the [requests module](http://docs.python-requests.org/en/master/) at the current stage and is not respecting any proxy settings from QGIS.
