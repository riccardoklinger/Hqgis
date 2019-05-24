# -*- coding: utf-8 -*-

"""
/***************************************************************************
 HqgisAlgorithm
                                 A QGIS plugin
 Processing plugin for Hqgis
                              -------------------
        begin                : 2019-02-06
        copyright            : (C) 2019 by Riccardo Klinger
        email                : riccardo.klinger@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from .HqgisAlgorithm_geocode import geocodeList
from .HqgisAlgorithm_POIs import getPois

__author__ = 'Tom Chadwin'
__date__ = '2019-02-06'
__copyright__ = '(C) 2019 by Tom Chadwin'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


class HqgisProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

        # Deactivate provider by default
        self.activate = False

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        QgsProcessingProvider.unload(self)
        # ProcessingConfig.removeSetting(
        #     qgis2webProvider.MY_DUMMY_SETTING)

    def id(self):
        """This is the name that will appear on the toolbox group.

        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return 'Hqgis'

    def name(self):
        """This is the provired full name.
        """
        return 'Hqgis'

    def icon(self):
        """We return the default icon.
        """
        return QgsProcessingProvider.icon(self)

    def load(self):
        self.refreshAlgorithms()
        return True

    def loadAlgorithms(self):
        """Here we fill the list of algorithms in self.algs.

        This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.

        In this case, since the list is always the same, we assign from
        the pre-made list. This assignment has to be done in this method
        even if the list does not change, since the self.algs list is
        cleared before calling this method.
        """

        self.alglist = [geocodeList(), getPois()]
        for alg in self.alglist:
            self.addAlgorithm(alg)
