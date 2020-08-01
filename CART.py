import numpy as np
import pandas as pd


"""
Implémentation de l'algorithme CART : Arbre de Décision pour de la classification.
La métrique de split utilisé est l'indice de Gini. 

---
Exemple : 

>>> from sklearn.datasets import load_iris
>>> import pandas as pd
>>> import numpy as np

>>> iris = load_iris()

>>> X = pd.DataFrame(iris.data, columns=iris.feature_names)
>>> y = pd.Series(iris.target, name="y")

>>> clf = DecisionTreeClassif()
>>> clf.fit(X, y, target_name=iris.target_names)

"""


class DecisionTreeClassif:

    def __init__(self, max_depth=float('inf')):
        self.max_depth = max_depth

    def fit(self, X, y, target_name=None):

        if target_name is None:
            target_name = np.unique(y)

        self.all_classes = np.unique(y)
        self.tree = self._tree_growth_(X, y, target_name=target_name)

    def predict(self, X):
        return [self._predict_(inputs, X) for inputs in X.index]


    def _predict_(self, inputs, X):
        node = self.tree
        
        while node.node.left:

            if X.loc[inputs, node.node.var] < node.node.threshold:
                node = node.node.left
            
            else:
                node = node.node.right

            if node.node is None:
                break
        
        return node.classe_predict

    def _gini_(self, y):
        m = y.size
        return 1.0 - sum((np.sum(y == c) / m) ** 2
                         for c in self.all_classes)

    def __make_threshold__(self, liste):

        liste_sorted = sorted(liste)
        return np.array([np.mean((liste_sorted[i], liste_sorted[i+1]))
                         for i in range(len(liste_sorted))[:-1]])

    def _tree_growth_(self, X, y, target_name, depth=0):

        if depth < self.max_depth:

            node = self._find_best_node_(X, y, target_name)

            if node.node is not None:

                X_left, y_left = X[node.node._sample_left], y[node.node._sample_left]
                X_right, y_right = X[node.node._sample_right], y[node.node._sample_right]

                node.node.left = self._tree_growth_(
                    X_left, y_left, target_name, depth + 1)
                node.node.right = self._tree_growth_(
                    X_right, y_right, target_name, depth + 1)

            return node

    def _find_best_node_(self, X, y, target_name):
        """
        Recherche le meilleur noeud possible (parmi toutes les variables et les seuils possibles) 
        selon la métrique suivante : indice de Gini.
        
        Paramètres
        -----
        X : features (pd.DataFrame)
        y : target (pd.Series)


        """
        best_gini = self._gini_(y)
        leaf = Leaf(X, y, target_name, self.all_classes)
        leaf.node = None

        for var in X.columns:

            all_value = np.unique(X[var])
            all_treshold = self.__make_threshold__(all_value)

            if len(all_treshold) > 1:

                for threshold in all_treshold:
                    node = Node(X, y, var, threshold, target_name, self.all_classes)

                    if node.gini_pondere < best_gini:
                        best_gini = node.gini_pondere
                        leaf.node = node

        return leaf


class Leaf:
    def __init__(self, X, y, target_name, all_classes):
        self.classe_predict = target_name[y[y.idxmax()]]
        self.repartition_parent = {target_name[i]: sum(y == i) for i in all_classes}


class Node:
    def __init__(self, X, y, var, threshold, target_name, all_classes):

        classe = X[var] < threshold
        m = len(y)
        number_left = sum(classe)
        number_right = sum(~classe)

        self._all_classes = all_classes
        self.threshold = threshold
        self.var = var

        left, right = self._sample_node_child_(
            X, y, var, threshold, target_name, classe)

        self._sample_left = left[1]
        self.repartition_left = left[0]

        self._sample_right = right[1]
        self.repartition_right = right[0]

        self.gini_pondere = self._gini_node_child_(X, y, var, threshold, classe,
                                                  m, number_left, number_right)

    def _sample_node_child_(self, X, y, var, threshold, target_name, classe):
        """
        Recherche de la répartition et des indices des noeuds fils

        Paramètre 
        --------
        X : DataFrame des features (X)
        y : Série de la valeur à prédire (y)
        threshold : seuil de découpage de l'échantillons
        classe : boolean indexing des données avec la variable threshold

        """

        sample_left_count = {target_name[i]: sum(
            classe[y == i]) for i in self._all_classes}

        sample_right_count = {target_name[i]: sum(
            ~classe[y == i]) for i in self._all_classes}

        sample_left = pd.concat(classe[y == i] for i in self._all_classes)
        sample_right = pd.concat(~classe[y == i] for i in self._all_classes)

        return (sample_left_count, sample_left), (sample_right_count, sample_right)

    def _gini_node_child_(self, X, y, var, threshold, classe, m, number_left, number_right):
        """
        Calcul du gini pondéré entre les deux noeuds fils

        Paramètre
        --------
        X : DataFrame des features (X)
        y : Série de la valeur à prédire (y)
        var : nom de la colonne
        threshold : seuil de découpage en deux échantillons
        m : nombre d'observations
        number_left : nombre d'observations pour le noeud fils gauche
        number_right : nombre d'observations pour le noeud fils droit

        """

        gini_left = 1.0 - sum((sum(classe[y == i]) / number_left) ** 2
                              for i in self._all_classes)
        gini_right = 1.0 - sum((sum(~classe[y == i]) / number_right) ** 2
                               for i in self._all_classes)

        gini_pondere = (number_left * gini_left +
                        number_right * gini_right) / m

        return gini_pondere

