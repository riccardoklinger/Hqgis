# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import (QCoreApplication, QUrl, QVariant)
from PyQt5.QtNetwork import (QNetworkReply,
                             QNetworkAccessManager,
                             QNetworkRequest)
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFeatureSink,
                       QgsNetworkAccessManager,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFeature,
                       QgsGeometry,
                       QgsUnitTypes,
                       QgsPointXY,
                       QgsSettings)
from functools import partial
import processing
import Hqgis
import os
import requests
import json
import time
import urllib


class getPois(QgsProcessingAlgorithm):
    def __init__(self):
        super().__init__()

    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    KEYS = 'KEYS'
    MODES = 'MODES'
    RADIUS = 'RADIUS'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return type(self)()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'getPOIsForPoints'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Get POIs around Points')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('POIs')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'POIs'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """This processing algorithm supports POI search for different categories for a set of points.<br>
         The complete list of categories can be found on <a href='https://github.com/riccardoklinger/Hqgis/blob/master/categories.md'>github</a>.<br> Make sure your HERE credentials are stored in the QGIS global settings using the plugin itself. Please read the referenced <a href='https://github.com/riccardoklinger/Hqgis#tos--usage'>Terms of Usage</a> prior usage.""")

    def loadCredFunctionAlg(self):
        import json
        import os
        #fileLocation = QFileDialog.getOpenFileName(self.dlg, "JSON with credentials",os.path.dirname(os.path.realpath(__file__))+ os.sep + "creds", "JSON(*.JSON)")
        # print(fileLocation)
        scriptDirectory = os.path.dirname(os.path.realpath(__file__))
        # self.dlg.credentialInteraction.setText("")
        creds = {}
        try:
            s = QgsSettings()
            creds["id"] = s.value("HQGIS/api_key", None)
            #self.dlg.credentialInteraction.setText("credits used from " + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
        except BaseException:
            print("cred load failed, check QGIS global settings")
            #self.dlg.credentialInteraction.setText("no credits found in. Check for file" + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
            # self.dlg.geocodeButton.setEnabled(False)
        # if not id in creds:
        #    self.feedback.reportError("no id / appcode found! Check file " + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
        return creds

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # point.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Point Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.keys = ['accommodation',
                     'administrative-areas-buildings',
                     'administrative-region',
                     'airport',
                     'ambulance-services',
                     'amusement-holiday-park',
                     'atm-bank-exchange',
                     'bar-pub',
                     'body-of-water',
                     'bookshop',
                     'building',
                     'business-industry',
                     'business-services',
                     'camping',
                     'car-dealer-repair',
                     'car-rental',
                     'casino',
                     'cinema',
                     'city-town-village',
                     'clothing-accessories-shop',
                     'coffee',
                     'coffee-tea',
                     'communication-media',
                     'dance-night-club',
                     'department-store',
                     'eat-drink',
                     'education-facility',
                     'electronics-shop',
                     'ev-charging-station',
                     'facilities',
                     'facility',
                     'fair-convention-facility',
                     'ferry-terminal',
                     'fire-department',
                     'food-drink',
                     'forest-heath-vegetation',
                     'going-out',
                     'government-community-facility',
                     'hardware-house-garden-shop',
                     'hospital-health-care-facility',
                     'hospital-health-care-facility',
                     'hostel',
                     'hotel',
                     'intersection',
                     'kiosk-convenience-store',
                     'landmark-attraction',
                     'leisure-outdoor',
                     'library',
                     'mall',
                     'motel',
                     'mountain-hill',
                     'museum',
                     'natural-geographical',
                     'outdoor-area-complex',
                     'parking-facility',
                     'petrol-station',
                     'pharmacy',
                     'police-emergency',
                     'police-station',
                     'post-office',
                     'postal-area',
                     'public-transport',
                     'railway-station',
                     'recreation',
                     'religious-place',
                     'restaurant',
                     'service',
                     'shop',
                     'shopping',
                     'sights-museums',
                     'snacks-fast-food',
                     'sport-outdoor-shop',
                     'sports-facility-venue',
                     'street-square',
                     'taxi-stand',
                     'tea',
                     'theatre-music-culture',
                     'toilet-rest-area',
                     'tourist-information',
                     'transport',
                     'travel-agency',
                     'undersea-feature',
                     'wine-and-liquor',
                     'zoo']
        self.addParameter(
            QgsProcessingParameterEnum(
                self.KEYS,
                self.tr('POI Categories'),
                options=self.keys,
                # defaultValue=0,
                optional=False,
                allowMultiple=True
            )
        )
        # self.modes = [
        #    "walk", #indicates that the user is on foot.
        #    "drive", #indicates that the user is driving.
        #    "public_transport", #indicates that the user is on public transport.
        #    "bicycle", #indicates that the user is on bicycle.
        #    "none" #if the user is neither on foot nor driving.
        # ]
        # self.addParameter(
        #    QgsProcessingParameterEnum(
        #        self.MODES,
        #        self.tr('Traffic Mode'),
        #        options=self.modes,
        #        #defaultValue=0,
        #        optional=False,
        #        allowMultiple=False
        #    )
        # )
        # self.addParameter(
        #    QgsProcessingParameterNumber(
        #        self.RADIUS,
        #        self.tr('Radius around Points [m]'),
        # parentParameterName=self.INPUT,
        # options=self.keys,
        #        defaultValue=100,
        #        minValue=1,
        #        maxValue=100000,
        #    defaultUnit="DistanceMeters",
        #        optional=False,
        #    )#.setDefaultUnit(QgsUnitTypes.DistanceMeters)
        # )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('POI layer')
            )
        )

    def convertGeocodeResponse(self, responseAddress):
        geocodeResponse = {}
        try:
            geocodeResponse["Label"] = responseAddress["Location"]["Address"]["Label"]
        except BaseException:
            geocodeResponse["Label"] = ""
        try:
            geocodeResponse["Country"] = responseAddress["Location"]["Address"]["Country"]
        except BaseException:
            geocodeResponse["Country"] = ""
        try:
            geocodeResponse["State"] = responseAddress["Location"]["Address"]["State"]
        except BaseException:
            geocodeResponse["State"] = ""
        try:
            geocodeResponse["County"] = responseAddress["Location"]["Address"]["County"]
        except BaseException:
            geocodeResponse["County"] = ""
        try:
            geocodeResponse["City"] = responseAddress["Location"]["Address"]["City"]
        except BaseException:
            geocodeResponse["City"] = ""
        try:
            geocodeResponse["District"] = responseAddress["Location"]["Address"]["District"]
        except BaseException:
            geocodeResponse["District"] = ""
        try:
            geocodeResponse["Street"] = responseAddress["Location"]["Address"]["Street"]
        except BaseException:
            geocodeResponse["Street"] = ""
        try:
            geocodeResponse["HouseNumber"] = responseAddress["Location"]["Address"]["HouseNumber"]
        except BaseException:
            geocodeResponse["HouseNumber"] = ""
        try:
            geocodeResponse["PostalCode"] = responseAddress["Location"]["Address"]["PostalCode"]
        except BaseException:
            geocodeResponse["PostalCode"] = ""
        try:
            geocodeResponse["Relevance"] = responseAddress["Relevance"]
        except BaseException:
            geocodeResponse["Relevance"] = None
        try:
            geocodeResponse["CountryQuality"] = responseAddress["MatchQuality"]["Country"]
        except BaseException:
            geocodeResponse["CountryQuality"] = None
        try:
            geocodeResponse["CityQuality"] = responseAddress["MatchQuality"]["City"]
        except BaseException:
            geocodeResponse["CityQuality"] = None
        try:
            geocodeResponse["StreetQuality"] = responseAddress["MatchQuality"]["Street"][0]
        except BaseException:
            geocodeResponse["StreetQuality"] = None
        try:
            geocodeResponse["NumberQuality"] = responseAddress["MatchQuality"]["HouseNumber"]
        except BaseException:
            geocodeResponse["NumberQuality"] = None
        try:
            geocodeResponse["MatchType"] = responseAddress["MatchType"]
        except BaseException:
            geocodeResponse["MatchType"] = ""
        return(geocodeResponse)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        # allow only regular point layers. no Multipoints
        if (source.wkbType() == 4
            or source.wkbType() == 1004
                or source.wkbType() == 3004):
            raise QgsProcessingException(
                "MultiPoint layer is not supported!")
        # radius = self.parameterAsString(
        #    parameters,
        #    self.RADIUS,
        #    context
        # )
        # mode = self.parameterAsEnum(
        #    parameters,
        #    self.MODES,
        #    context
        # )
        categories = self.parameterAsEnums(
            parameters,
            self.KEYS,
            context
        )
        # feedback.pushInfo(addressField)

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(
                    parameters, self.INPUT))

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        fields.append(QgsField("origin_id", QVariant.Int))
        fields.append(QgsField("title", QVariant.String))
        fields.append(QgsField("label", QVariant.String))
        fields.append(QgsField("distance", QVariant.Double))
        fields.append(QgsField("categories", QVariant.String))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point,
            QgsCoordinateReferenceSystem(4326)
        )
        # Send some information to the user
        feedback.pushInfo(
            '{} points for POI finding'.format(
                source.featureCount()))
        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(
                    parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        # get the keys:
        creds = self.loadCredFunctionAlg()
        # convert categories to list for API call:
        categoriesList = []
        #self.keys[keyField].split(" | ")[1]
        for category in categories:
            categoriesList.append(self.keys[category])
        categories = ",".join(categoriesList)
        layerCRS = source.sourceCrs()
        if layerCRS != QgsCoordinateReferenceSystem(4326):
            sourceCrs = source.sourceCrs()
            destCrs = QgsCoordinateReferenceSystem(4326)
            tr = QgsCoordinateTransform(
                sourceCrs, destCrs, QgsProject.instance())
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            # convert coordinates:
            if layerCRS != QgsCoordinateReferenceSystem(4326):
                # we reproject:
                geom = feature.geometry()
                newGeom = tr.transform(geom.asPoint())
                x = newGeom.x()
                y = newGeom.y()
            else:
                x = feature.geometry().asPoint().x()
                y = feature.geometry().asPoint().y()
            coordinates = str(y) + "," + str(x)
            # get the location from the API:
            header = {"referer": "HQGIS"}
            ApiUrl = 'https://browse.search.hereapi.com/v1/browse?at=' + coordinates + \
                "&categories=" + categories + "&limit=100&apiKey=" + creds["id"]
            feedback.pushInfo('calling Url {}'.format(ApiUrl))
            r = requests.get(ApiUrl, headers=header)
            responsePlaces = json.loads(r.text)["items"]
            for place in responsePlaces:
                lat = place["position"]["lat"]
                lng = place["position"]["lng"]
                # iterate over categories:
                categoriesResp = []
                for cat in place["categories"]:
                    categoriesResp.append(cat["id"])
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lng, lat)))
                fet.setAttributes([
                    place["id"],
                    feature.id(),
                    place["title"],
                    place["address"]["label"],
                    place["distance"],
                    ";".join(categoriesResp)
                ])
                sink.addFeature(fet, QgsFeatureSink.FastInsert)
            #lat = responseAddress["Location"]["DisplayPosition"]["Latitude"]
            #lng = responseAddress["Location"]["DisplayPosition"]["Longitude"]
            # Add a feature in the sink
            # feedback.pushInfo(str(lat))

            # fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lng,lat)))
            # fet.setAttributes([

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancelation and progress
        # reports!)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
