import argparse
import os
import json
import sys 
import pandas as pd
# from sklearn.base import accuracy_score
from sklearn.metrics import accuracy_score,confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

print(os.path.realpath(__file__))
from classifier import DisinformationClassifier

current_dir = os.path.realpath(__file__)
par_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(par_dir)
from features.whois_features import WhoisFeatures
from features.certificate_features import CertificateFeatures
from features.domain_features import DomainFeatures
from features.html_features import HTMLFeatures

full_params     = {'max_features': 196, 
                   'min_samples_split': 5, 
                   'bootstrap': False,
                   'criterion': 'entropy',
                   'n_estimators': 327,
                   'min_samples_leaf': 1,
                   'max_depth': 22,
                   'random_state': 0}

registrar_params = {'max_features': 12,
                    'min_samples_split': 5,
                    'bootstrap': True,
                    'criterion': 'gini',
                    'n_estimators': 245,
                    'min_samples_leaf': 1,
                    'max_depth': 29,
                    'random_state': 0}

ca_params        = {'max_features': 1,
                    'min_samples_split': 34,
                    'bootstrap': False,
                    'criterion': 'entropy',
                    'n_estimators': 604,
                    'min_samples_leaf': 2,
                    'max_depth': 19,
                    'random_state': 0}

ca_with_registrar = {'max_features': 23,
                     'min_samples_split': 2,
                     'bootstrap': False,
                     'criterion': 'entropy',
                     'n_estimators': 817,
                     'min_samples_leaf': 1,
                     'max_depth': 34,
                     'random_state': 0}

web_host_params = {'max_features': 270,
                   'min_samples_split': 10,
                   'bootstrap': False,
                   'criterion': 'entropy',
                   'n_estimators': 555,
                   'min_samples_leaf': 2,
                   'max_depth': 31,
                   'random_state': 0}

desired_features_names = ["html_features", "domain_features", "cert_features", "whois_features"]

def main(db_raw_training_data: pd.DataFrame, desired_features:list):

    # colect all columns names
    # config_dir = os.path.join(par_dir, "config.json")
    # with open(config_dir) as file:
    #     all_features_name = json.load(file)

    # desired_features = []
    # for name in desired_features_names:
    #     if name == "html_features":
    #         names = all_features_name[name]
    #         for n in names:
    #             desired_features.extend(names[n])
    #     else: 
    #         desired_features.extend(all_features_name[name])

    X_train, X_test, y_train, y_test = train_test_split(
        db_raw_training_data[desired_features],  # X
        db_raw_training_data["target"].to_list(),  # y
        test_size=0.2,  # Proportion of the dataset to include in the test split
        random_state=0  # Random seed for reproducibility
    )

    d = DisinformationClassifier(X_train, y_train, 
                                 desired_features,
                                 save_ft_names=True)
   
    # d.classifier.set_params(**full_params)
    d.train() 
    d.save("full_model.pickle")

    y_pred, _ = zip(*[d.predict(resp) for _, resp in X_test.iterrows()])
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    conf_matrix = confusion_matrix(y_test, y_pred)

    return accuracy, precision, recall, f1, conf_matrix

if __name__ == '__main__':
    main()
