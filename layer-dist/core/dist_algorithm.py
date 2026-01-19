import time

class CalculateNearestFeatures:
    def __init__(self, layer_a, layer_b, method='loop'):
        self.layer_a = layer_a
        self.layer_b = layer_b
        self.method = method

    def get_distances_loop(self):        
        pass

    def get_distances_spatial_index(self):
        pass

    def create_distances_layer(self, distances):
        pass

    def create_dist_geometries_layer(self, geometries):
        pass

    def run(self):
        start_time = time.time()

        if self.method == 'loop':
            distances, geometries = self.get_distances_loop()
        elif self.method == 'spatial_index':
            distances, geometries = self.get_distances_spatial_index()
        else:
            raise ValueError(f"Unknown method: {self.method}")

        self.create_distances_layer(distances)
        self.create_dist_geometries_layer(geometries)

        end_time = time.time()
        self.log_time(start_time, end_time)

    def log(self, message):
        print(message)

    def log_time(self, start_time, end_time):
        elapsed = end_time - start_time
        self.log(f"Elapsed time: {elapsed:.2f} seconds")
    
