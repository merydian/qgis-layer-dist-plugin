from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterEnum,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSource,
    QgsProject,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingFeedback,
    QgsFields,
    QgsField,
    QgsCoordinateReferenceSystem,
    QgsWkbTypes,
    QgsFeature,
)
from qgis.PyQt.QtCore import QVariant
from typing import Dict, Any, List
from ..core.dist_algorithm import CalculateNearestFeatures


class DistanceProcessingAlgorithm(QgsProcessingAlgorithm):
    def __init__(self) -> None:
        super().__init__()
        self.LAYER_A = "LAYER_A"
        self.LAYER_B = "LAYER_B"
        self.METHOD = "METHOD"
        self.CREATE_GEOMS_LAYER = "CREATE_GEOMS_LAYER"
        self.OUTPUT = "OUTPUT"

        self.PARAMETERS: List = [
                QgsProcessingParameterFeatureSource(
                    name=self.LAYER_A,
                    description="Input Point layer to be measured from",
                ),
                QgsProcessingParameterFeatureSource(
                    name=self.LAYER_B,
                    description="Input layer to compare to",
                ),
                QgsProcessingParameterBoolean(
                    name=self.CREATE_GEOMS_LAYER,
                    description="Create geometries layer",
                    defaultValue=False,
                ),
                QgsProcessingParameterEnum(
                    name=self.METHOD,
                    description="Execution method",
                    options=["Simple", "Optimized"],
                    defaultValue=1,
                ),
                QgsProcessingParameterFeatureSink(
                    name=self.OUTPUT,
                    description="Output layer with distances",
                ),
            ]
        
    def initAlgorithm(self, config: QgsProcessingContext) -> None:
        for param in self.PARAMETERS:
            self.addParameter(param)

    def processAlgorithm(
        self,
        parameters: Dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> Dict[str, Any]:
        layer_a = self.parameterAsVectorLayer(
            parameters, self.LAYER_A, context
        )
        layer_b = self.parameterAsVectorLayer(
            parameters, self.LAYER_B, context
        )
        method_index = self.parameterAsEnum(
            parameters, self.METHOD, context
        )
        method = "loop" if method_index == 0 else "spatial_index"
        create_geoms_layer = self.parameterAsBool(
            parameters, self.CREATE_GEOMS_LAYER, context
        )

        dist_alg = CalculateNearestFeatures(
            project=QgsProject.instance(),
            layer_a=layer_a,
            layer_b=layer_b,
            method=method,
            create_geoms_layer=create_geoms_layer,
        )

        if layer_a.wkbType() == QgsWkbTypes.Type.Point:
            layer_type = QgsWkbTypes.Type.Point
        else:
            layer_type = QgsWkbTypes.Type.Polygon

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            self.get_fields(),
            layer_type,
            QgsCoordinateReferenceSystem.fromEpsgId(4326),
        )

        if method == "Simple":
            attributes = dist_alg.get_distances_loop()
        else:
            attributes = dist_alg.get_distances_spatial_index()

        for attr in attributes:
            feat = QgsFeature()
            feat.setGeometry(attr.geom_a)
            feat.setAttributes([attr.nearest_id, attr.distance, method])
            sink.addFeature(feat)

        # if create_geoms_layer:
            # return {self.OUTPUT: (dest_id, geoms_layer.id())}
        # else:
        return {self.OUTPUT: dest_id}
    
    def displayName(self) -> str:
        return "Calculate Nearest Features Distance"

    def createInstance(self) -> Any:
        """
        Returns instance of any child class
        """
        return self.__class__()
    
    def name(self) -> str:
        return "calculate_nearest_features_distance"

    def get_fields(self) -> QgsFields:
        fields = QgsFields()
        fields.append(QgsField("nearest_id", QVariant.Int))
        fields.append(QgsField("distance", QVariant.Double))
        fields.append(QgsField("method", QVariant.String))
        return fields