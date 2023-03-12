from enum import Enum


class GraphLayoutAlgorithm(Enum):
    def __str__(self):
        return str(self.name)

    planar = "Planar"
    fruchterman_reingold = "Fruchterman-Reingold"
    shell = "Shell"
    kamada_kawai = "Kamada-Kawai"
    random = "Random"
    spectral = "Spectral"
    spiral = "Spiral"
    circular = "Circular"
