# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import numpy as np
import scipy.spatial.distance as dist
from sklearn.metrics.pairwise import cosine_similarity


class Cosine:

    def __init__(self):
        self.func = self.cosine_vector_optimization
        pass

    def run(self, arr1: np.array, arr2: np.array):
        return self.func(arr1, arr2)

    @staticmethod
    def cosine_vector_base(arr1: np.array, arr2: np.array):
        """
        Efficiency is lowest: 122500 times needs 38.62 second.
        """
        return cosine_similarity(X=[arr1], Y=[arr2])[0][0]

    @staticmethod
    def cosine_vector_with_matrix(arr: np.array, filter_result=False, filter_threshold: float = 0):
        """
        Efficiency is high: 122500 times needs 1.3404 second.
        Input data:
            X = np.array([vector1, vector2, vector3])
            X : {array-like, sparse matrix} of shape (n_samples_X, n_features)
        filter_result:
        filter_threshold:
        Return a matrix:
            similarities[0, 1]: item1 & item2
            similarities[0, 2]: item1 & item3
        OR return a list:
            [[index1, index2, value], [index1, index3, value]]
        """
        similarity_matrix = cosine_similarity(arr)
        if filter_threshold > 0:
            similarity_matrix = np.where(similarity_matrix < filter_threshold, 0, similarity_matrix)
        if filter_result:
            res = []
            upper_triangular = np.triu(similarity_matrix, k=1)
            nonzero = np.nonzero(upper_triangular)
            for i in range(len(nonzero[0])):
                res.append((nonzero[0][i], nonzero[1][i], upper_triangular[nonzero[0][i]][nonzero[1][i]]))
            return res
        return similarity_matrix

    @staticmethod
    def cosine_vector_optimization(arr1: np.array, arr2: np.array):
        """
        Parallel optimization based on CPU
        Efficiency is highest: 122500 times needs 0.6753 second.
        """
        return 1 - dist.cosine(arr1, arr2)

