#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer

from preprocess import ImportanceModelPreprocessor, make_complete_preprocessor

class DisinformationClassifier:

    def __init__(self, X_train, y_train, desired_features, save_ft_names=False):
        
        self.desired_features = desired_features
        # self.X, self.y = self.extract_training_data(raw_training_data, desired_features)

        self.X = X_train
        self.y = y_train

        if save_ft_names:
            self.preprocessor = ImportanceModelPreprocessor(self.X)
        else:
            self.preprocessor = make_complete_preprocessor(numeric=True, 
                                                           categorical=True,
                                                           boolean=True)

        self.classifier = RandomForestClassifier(n_estimators=100,
                                                 class_weight="balanced",
                                                 random_state=0)

    def extract_training_data(self, raw_training_data, desired_features):
        y = raw_training_data["target"].to_list()
        X = raw_training_data[desired_features]

        return X, y

    @staticmethod
    def load_model_from_file(filename):
        with open(filename, "rb") as f:
            m = pickle.load(f)
        return m

    def save(self, filename):
        # Save this model to disk
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def preprocess(self, X, isTrainingData):
        # Cast object columns to category
        
        if isTrainingData:
            self.preprocessor.fit(X)
        X = self.preprocessor.transform(X)
        return X

    def train(self):
        # Preprocess training data
        print(type(self.X.head(2)))
        self.X = self.preprocess(self.X, True)

        # Fit the classifier on the training data
        self.classifier.fit(self.X, self.y)

    def predict(self, resp):
        try:
            # Get features from raw data
            X_new = resp

            # Preprocess features
            X_new = self.preprocess(X_new, False)

            # Make a prediction
            targets = self.classifier.classes_
            probas = self.classifier.predict_proba(X_new)[0].tolist()
            probas_dict = {targets[0]: probas[0], targets[1]: probas[1]}
            y_new = max(probas_dict, key=probas_dict.get)
            return (y_new, probas_dict)
        except Exception as e:
            print(e)
            return "unclassified", None
