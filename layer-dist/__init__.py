# -----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import Qt
from .gui.dock import LayerDistDockWidget
from qgis.core import QgsProject
from .core.dist_algorithm import CalculateNearestFeatures


def classFactory(iface):
    return DistancePlugin(iface)


class DistancePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()
        self.actions = []
        self.widget = None
        self.action = None

    def initGui(self) -> None:
        self.widget = LayerDistDockWidget(self.project, self.iface)

        self.action = QAction("LayerDist")
        self.action.setCheckable(True)
        self.actions.append(self.action)

        self.widget.setToggleVisibilityAction(self.action)

        self.iface.pluginToolBar().addAction(self.action)

        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.widget)

        self.widget.push_run.clicked.connect(self.run)

        self.widget.show()

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        method = (
            "loop"
            if self.widget.combo_execution_method.currentText() == "Simple"
            else "spatial_index"
        )
        dist_alg = CalculateNearestFeatures(
            project=self.project,
            layer_a=self.widget.combo_layer_a.currentLayer(),
            layer_b=self.widget.combo_layer_b.currentLayer(),
            method=method,
            create_geoms_layer=self.widget.check_link_layer.isChecked(),
        )

        dist_alg.log_message.connect(self.widget.append_log)
        dist_alg.new_stats.connect(self.widget.update_stats)

        dist_alg.run()
