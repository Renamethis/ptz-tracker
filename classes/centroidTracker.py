from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class CentroidTracker():
    def __init__(self, maxDisappeared=50):
        self.__next_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_dist = maxDisappeared

    def register(self, centroid):
        self.objects[self.__next_id] = centroid
        self.disappeared[self.__next_id] = 0
        self.__next_id += 1

    def deregister(self, id):
        del self.objects[id]
        del self.disappeared[id]

    def update(self, rects):
        if(len(rects) == 0):
            for id in list(self.disappeared.keys()):
                self.disappeared[id] += 1
                if self.disappeared[id] > self.max_dist:
                    self.deregister(id)
            return self.objects
        input = np.zeros((len(rects), 2), dtype="int")
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            input[i] = (cX, cY)
        if len(self.objects) == 0:
            for i in range(0, len(input)):
                self.register(input[i])
        else:
            ids = list(self.objects.keys())
            centroids = list(self.objects.values())
            #print(input)
            #print(np.array(centroids).reshape(1, -1))
            distance = dist.cdist(np.array(centroids),
                                  input, 'euclidean')
            #print(distance)
            rows = distance.min(axis=1).argsort()
            cols = distance.argmin(axis=1)[rows]
            uRows = set()
            uCols = set()
            for (row, col) in zip(rows, cols):
                if(row in uRows or col in uCols):
                    continue
                id = ids[row]
                self.objects[id] = input[col]
                self.disappeared[id] = 0
                uRows.add(row)
                uCols.add(col)
            unRows = set(range(0, distance.shape[0])).difference(uRows)
            unCols = set(range(0, distance.shape[1])).difference(uCols)
            if distance.shape[0] > distance.shape[1]:
                for row in unRows:
                    id = ids[row]
                    self.disappeared[id] += 1
                    if self.disappeared[id] > self.max_dist:
                        self.deregister(id)
            else:
                for col in unCols:
                    self.register(input[col])
        return self.objects
