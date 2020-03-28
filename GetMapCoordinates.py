from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.gui import QgsMapToolEmitPoint, QgsMapToolPan
import requests
import json


class GetMapCoordinates(QgsMapToolEmitPoint):
    '''Class to interact with the map canvas to capture the coordinate
    when the mouse button is pressed.'''

    def __init__(self, iface):
        QgsMapToolEmitPoint.__init__(self, iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.canvasClicked.connect(self.clicked)
        # self.pt4326=None

    def activate(self):
        '''When activated set the cursor to a crosshair.'''

    def getCredentials(self):
        self.appId = self.dlg.AppId.text()
        #self.appCode = self.dlg.AppCode.text()

    def clicked(self, pt, b):
        # if self.dlg.captureButton.isChecked():
        '''Capture the coordinate when the mouse button has been released,
        format it, and copy it to dashboard'''
        # transform the coordinate to 4326 but display it in the original crs
        canvasCRS = self.canvas.mapSettings().destinationCrs()
        epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = QgsCoordinateTransform(
            canvasCRS, epsg4326, QgsProject.instance())
        pt4326 = transform.transform(pt.x(), pt.y())
        lat = pt4326.y()
        lon = pt4326.x()
        self.getCredentials()
        # change dockwidget corrdinate with the original crs
        if self.dlg.captureButton.isChecked():
            url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox=" + \
                str(lat) + "%2C" + str(lon) + "%2C10&mode=retrieveAddresses&maxresults=1&gen=9&app_id=" + self.appId
            print(url)
            r = requests.get(url)
            try:
                self.dlg.fromAddress.setText(
                    json.loads(
                        r.text)["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"])
            except BaseException:
                self.dlg.fromAddress.setText("no address found")
                print("something went wrong")
            self.dlg.FromLabel.setText(
                str("%.5f" % lat) + ',' + str("%.5f" % lon))
            self.dlg.captureButton.setChecked(False)
        if self.dlg.captureButton_2.isChecked():
            url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox=" + \
                str(lat) + "%2C" + str(lon) + "%2C10&mode=retrieveAddresses&maxresults=1&gen=9&app_id=" + self.appId
            r = requests.get(url)
            try:
                self.dlg.toAddress.setText(
                    json.loads(
                        r.text)["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"])
            except BaseException:
                self.dlg.toAddress.setText("no address found")
                print("something went wrong")
            self.dlg.ToLabel.setText(
                str("%.5f" % lat) + ',' + str("%.5f" % lon))
            self.setWidget(self.dlg)
            self.iface.mapCanvas().setCursor(Qt.ArrowCursor)
            self.dlg.captureButton_2.setChecked(False)
        if self.dlg.captureButton_4.isChecked():
            url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox=" + \
                str(lat) + "%2C" + str(lon) + "%2C10&mode=retrieveAddresses&maxresults=1&gen=9&app_id=" + self.appId

            r = requests.get(url)
            try:
                self.dlg.placesAddress.setText(json.loads(
                    r.text)["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"])
            except BaseException:
                self.dlg.placesAddress.setText("no address found")
                print("something went wrong")
            self.dlg.placeLabel.setText(
                str("%.5f" % lat) + ',' + str("%.5f" % lon))
            self.dlg.findPOISButton.setEnabled(True)
            self.setWidget(self.dlg)
            self.iface.mapCanvas().setCursor(Qt.ArrowCursor)
            self.dlg.captureButton_4.setChecked(False)

        if self.dlg.captureButton_3.isChecked():
            url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?prox=" + \
                str(lat) + "%2C" + str(lon) + "%2C10&mode=retrieveAddresses&maxresults=1&gen=9&app_id=" + self.appId

            r = requests.get(url)
            # print(r.text)
            try:
                self.dlg.IsoAddress.setText(
                    json.loads(
                        r.text)["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"])
            except BaseException:
                self.dlg.IsoAddress.setText("no address found")
                print("something went wrong")
            self.dlg.IsoLabel.setText(
                str("%.5f" % lat) + ',' + str("%.5f" % lon))
            self.dlg.calcIsoButton.setEnabled(True)
            self.setWidget(self.dlg)
            self.iface.mapCanvas().setCursor(Qt.ArrowCursor)
            self.dlg.captureButton_3.setChecked(False)

    def setWidget(self, dockwidget):
        print(dockwidget)
        self.dlg = dockwidget
