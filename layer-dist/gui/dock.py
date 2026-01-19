import os
from qgis.PyQt import uic
from qgis.gui import QgsDockWidget

ui_file_path = f"{os.path.dirname(__file__)}/../ui/dockwidget.ui"
DOCK_WIDGET, _ = uic.loadUiType(ui_file_path)

class LayerDistDockWidget(DOCK_WIDGET, QgsDockWidget):
    """
    Main dock widget.
    """

    def __init__(self, project, iface) -> None:
        super(LayerDistDockWidget, self).__init__()
        self.setupUi(self)
        self.setObjectName("LayerDistDockWidget")