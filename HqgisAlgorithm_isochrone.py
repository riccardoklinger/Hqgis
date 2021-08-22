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

from PyQt5.QtCore import QCoreApplication, QVariant
from PyQt5.QtGui import QColor
from qgis.core import (
    QgsProcessing,
    QgsFeatureSink,
    QgsRendererRange,
    QgsGraduatedSymbolRenderer,
    QgsProject,
    QgsProcessingParameterEnum,
    QgsCoordinateTransform,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsSymbol,
    QgsField,
    QgsFields,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsSettings,
)
from .decoding import decode
from functools import partial
from datetime import datetime
import Hqgis
import os
import requests
import json
import time
import urllib


class isochroneList(QgsProcessingAlgorithm):
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

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    KEYS = "KEYS"
    MODES = "MODES"
    METRIC = "METRIC"
    DISTANCES = "DISTANCE"
    DEPARTURETIME = "DEPARTURETIME"

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

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
        return "getIsochrones"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Get Isochrones around Points")

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr("Isochrones")

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "Isochrones"

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """This processing algorithm supports Isochrone search for a set of points.<br>Departure Time is treated as local time of the departure locations!
         Make sure your HERE credentials are stored in the QGIS global settings using the plugin itself. Please read the referenced <a href='https://github.com/riccardoklinger/Hqgis#tos--usage'>Terms of Usage</a> prior usage."""
        )

    def loadCredFunctionAlg(self):
        import json
        import os

        # fileLocation = QFileDialog.getOpenFileName(self.dlg, "JSON with credentials",os.path.dirname(os.path.realpath(__file__))+ os.sep + "creds", "JSON(*.JSON)")
        # print(fileLocation)
        scriptDirectory = os.path.dirname(os.path.realpath(__file__))
        # self.dlg.credentialInteraction.setText("")
        creds = {}
        try:
            s = QgsSettings()
            creds["id"] = s.value("HQGIS/api_key", None)
            # self.dlg.credentialInteraction.setText("credits used from " + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
        except BaseException:
            print("cred load failed, check QGIS global settings")
            # self.dlg.credentialInteraction.setText("no credits found in. Check for file" + scriptDirectory + os.sep + 'creds' + os.sep + 'credentials.json')
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
                self.tr("Input Point Layer"),
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.keys = [
            "pedestrian",
            "car",
            "truck",
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.KEYS,
                self.tr("routing mode"),
                options=self.keys,
                defaultValue="car",
                optional=False,
                allowMultiple=False,
            )
        )
        self.modes = ["fast", "short"]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.MODES,
                self.tr("Traffic Mode"),
                options=self.modes,
                defaultValue="fast",
                optional=False,
                allowMultiple=False,
            )
        )
        self.metric = ["time", "distance"]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.METRIC,
                self.tr("Metric"),
                options=self.metric,
                defaultValue="seconds",
                optional=False,
                allowMultiple=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.DISTANCES,
                self.tr("Distance(s)"),
                "300,600,900",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.DEPARTURETIME,
                self.tr("Local Departure Time"),  # 2019-06-24T01:23:45
                datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                optional=False,
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr("POI layer"))
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT, context)
        # allow only regular point layers. no Multipoints
        if (
            source.wkbType() == 4
            or source.wkbType() == 1004
            or source.wkbType() == 3004
        ):
            raise QgsProcessingException("MultiPoint layer is not supported!")
        transportMode = self.keys[self.parameterAsEnum(parameters, self.KEYS, context)]
        mode = self.modes[self.parameterAsEnum(parameters, self.MODES, context)]
        slots = self.parameterAsString(parameters, self.DISTANCES, context)
        metric = self.metric[self.parameterAsEnum(parameters, self.METRIC, context)]
        departureTime = self.parameterAsString(parameters, self.DEPARTURETIME, context)
        print(type(transportMode), type(metric), type(slots), type(mode), type(time))
        # feedback.pushInfo(addressField)

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated

        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        fields = QgsFields()
        # fields.append(QgsField("id", QVariant.String))
        fields.append(QgsField("origin_id", QVariant.Int))
        fields.append(QgsField("url", QVariant.String)),
        fields.append(QgsField("type", QVariant.String)),
        fields.append(QgsField("distance", QVariant.Double))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Polygon,
            QgsCoordinateReferenceSystem(4326),
        )
        # Send some information to the user
        feedback.pushInfo(
            "{} points for isochrone finding".format(source.featureCount())
        )
        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        # get the keys:
        creds = self.loadCredFunctionAlg()
        layerCRS = source.sourceCrs()
        if layerCRS != QgsCoordinateReferenceSystem(4326):
            sourceCrs = source.sourceCrs()
            destCrs = QgsCoordinateReferenceSystem(4326)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
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
            print(coordinates)
            # get the location from the API:
            header = {"referer": "HQGIS"}
            time.sleep(1)
            print(sink, type(sink))
            print(self.OUTPUT, type(self.OUTPUT))
            ApiUrl = (
                "https://isoline.router.hereapi.com/v8/isolines?origin="
                + coordinates
                + "&departureTime="
                + departureTime
                + "&range[type]="
                + metric
                + "&range[values]="
                + slots
                + "&routingMode="
                + mode
                + "&transportMode="
                + transportMode
                + "&apiKey="
                + creds["id"]
            )

            feedback.pushInfo("calling Url {}".format(ApiUrl))
            r = requests.get(ApiUrl, headers=header)
            print(json.loads(r.text))
            # layer = self.createRouteLayer()
            for line in reversed(json.loads(r.text)["isolines"]):
                # print(decode(line["polygons"][0]["outer"]))
                for polygon in line["polygons"]:
                    for key, value in polygon.items():
                        Points = decode(value)
                        vertices = []
                        for Point in Points:
                            lat = Point[0]
                            lng = Point[1]
                            vertices.append(QgsPointXY(lng, lat))
                        fet = QgsFeature()
                        fet.setGeometry(QgsGeometry.fromPolygonXY([vertices]))
                        fet.setAttributes(
                            [feature.id(), ApiUrl, key, line["range"]["value"]]
                        )
                        sink.addFeature(fet, QgsFeatureSink.FastInsert)
                        # QgsProject.instance().addMapLayer(layer)

            # Update the progress bar
            feedback.setProgress(int(current * total))
        return {self.OUTPUT: dest_id}
