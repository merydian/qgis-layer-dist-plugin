import time
from qgis.core import QgsFeature, QgsVectorLayer, QgsWkbTypes, QgsSpatialIndex

class DistanceAttribute:
    def __init__(self, geom_a, geom_b, nearest_id, distance):
        self.geom_a = geom_a
        self.geom_b = geom_b
        self.nearest_id = nearest_id
        self.distance = distance

class CalculateNearestFeatures:
    def __init__(self, project, layer_a, layer_b, method, create_geoms_layer):
        self.project = project
        self.layer_a = layer_a
        self.layer_b = layer_b
        self.method = method
        self.create_geoms_layer=create_geoms_layer

    def get_distances_loop(self) -> list[DistanceAttribute]:   

        attributes = []
        
        for feat_a in self.layer_a.getFeatures():
            geom_a = feat_a.geometry()
            if self.layer_a.geometryType() == QgsWkbTypes.PolygonGeometry:
                point_geom_a = geom_a.centroid()
            else:
                point_geom_a = geom_a
            
            dists = {}

            for feat_b in self.layer_b.getFeatures():
                geom_b = feat_b.geometry()

                dist = point_geom_a.distance(geom_b)
                dists[dist] = feat_b.id()
            
            nearest_id = dists[min(dists.keys())]
            dist = min(dists.keys())
            geom_b_nearest = self.layer_b.getFeature(nearest_id).geometry()
            
            attr = DistanceAttribute(geom_a, geom_b_nearest, nearest_id, dist)
            attributes.append(attr)
        
        return attributes

    def get_distances_spatial_index(self) -> list[DistanceAttribute]:
        layer_b_idx = QgsSpatialIndex(self.layer_b.getFeatures(), flags=QgsSpatialIndex.FlagStoreFeatureGeometries)

        attributes = []

        
        
        for feat_a in self.layer_a.getFeatures():
            geom_a = feat_a.geometry()
            
            if self.layer_a.geometryType() == QgsWkbTypes.PolygonGeometry:
                point_geom_a = geom_a.centroid()
            else:
                point_geom_a = geom_a

            candidate_ids = layer_b_idx.nearestNeighbor(point_geom_a, 5)
            
            dists = {}

            for fid in candidate_ids:
                feat_b = self.layer_b.getFeature(fid)
                geom_b = feat_b.geometry()

                dist = point_geom_a.distance(geom_b)
                dists[dist] = feat_b.id()
            
            nearest_id = dists[min(dists.keys())]
            dist = min(dists.keys())
            geom_b_nearest = self.layer_b.getFeature(nearest_id).geometry()
            
            attr = DistanceAttribute(geom_a, geom_b_nearest, nearest_id, dist)
            attributes.append(attr)
        
        return attributes

    def create_distances_layer(self, attributes):
        layer_out_name = "nearest_features"

        geom_type = "polygon" if self.layer_a.geometryType() == QgsWkbTypes.PolygonGeometry else "point"
        uri = f"{geom_type}?crs=epsg:{self.layer_a.crs().postgisSrid()}&field=nearest_id:integer&field=distance:double&field=method:string(20)"
        layer_out = QgsVectorLayer(uri, layer_out_name, "memory")

        for attr in attributes:
            feat = QgsFeature()
            feat.setGeometry(attr.geom_a)
            feat.setAttributes([attr.nearest_id, attr.distance, self.method])
            layer_out.dataProvider().addFeatures([feat])
        
        layer_out.updateFields()

        return layer_out        

    def create_dist_geometries_layer(self, geometries):
        pass

    def run(self):
        start_time = time.time()

        if self.method == 'loop':
            attributes = self.get_distances_loop()
        elif self.method == 'spatial_index':
            attributes = self.get_distances_spatial_index()
        else:
            raise ValueError(f"Unknown method: {self.method}")

        dist_layer = self.create_distances_layer(attributes)
        
        if self.create_geoms_layer:
            geoms_layer = self.create_dist_geometries_layer(attributes)
            self.project.addMapLayer(geoms_layer)
        
        self.project.addMapLayer(dist_layer)

        end_time = time.time()
        self.log_time(start_time, end_time)
        self.log(f"Number of features processed: {len(attributes)}\n")

    def log(self, message):
        print(message)

    def log_time(self, start_time, end_time):
        elapsed = end_time - start_time
        self.log(f"Elapsed time: {elapsed:.2f} seconds")
    
