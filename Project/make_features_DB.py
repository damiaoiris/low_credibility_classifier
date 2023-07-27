import pandas as pd
import os 
from pathlib import Path
from util.utils_DB import Database
from util.utils import clear_terminal, parse_ps_plus_1
from data.collector import Collector
import dns.resolver
import socket
import json 
import ssl
import whois
from features.html_features import HTMLFeatures
from features.domain_features import DomainFeatures
from features.certificate_features import CertificateFeatures
from features.whois_features import WhoisFeatures

current_dir = os.path.realpath(__file__)
par_dir = os.path.abspath(os.path.join(current_dir, os.pardir))


class FeaturesFetcher():

    def __init__(self):
        pass
    
    @staticmethod
    def fetch_html_features(html_path: Path): 
        
        raw_data = html_path

        return raw_data
        
    @staticmethod
    def fetch_domain_features(domain: str):
        try:
            raw_data = dns.resolver.query(domain, 'A').rrset[0]
            raw_data = str(raw_data)
        except Exception as e:
            raw_data = None
        return raw_data
    
    @staticmethod
    def fetch_certificate(domain):
        try:
            # Get the certificate
            context = ssl._create_unverified_context()
            sock = socket.socket(socket.AF_INET)
            sock.settimeout(5)
            conn = context.wrap_socket(sock,
                                       server_hostname=domain)
            conn.connect((domain, 443))
            der_cert = conn.getpeercert(True)

            # Convert the certificate from DER to PEM
            raw_data = str(ssl.DER_cert_to_PEM_cert(der_cert))
        except Exception as e:
            raw_data = None
        
        return raw_data
    
    @staticmethod
    def fetch_whois(domain):
        try:
            obj = whois.whois(domain)
            raw_data = obj.text
        except Exception as e:
            raw_data = None

        return raw_data

    @staticmethod
    def get_features(resp: pd.DataFrame, desired_features: list):

        final_df = pd.DataFrame()  # Initialize final_df outside the loop

        for idx, row in resp.iterrows():
            df = pd.DataFrame()  
            df_row = pd.DataFrame({"domain": [row.domain]})

            for name in desired_features:
                config_file = os.path.join(par_dir, "config_features.json")
                with open(config_file) as file:
                    all_features_name = json.load(file)
                feature_names = all_features_name[name]

                if name == 'domain_features':
                    features = DomainFeatures.get_features(feature_names=feature_names,
                                                        raw_data=FeaturesFetcher.fetch_domain_features(row.domain),
                                                        available=True,
                                                        domain=row.domain)
                elif name == 'html_features':
                    features = HTMLFeatures.get_features(feature_names=feature_names,
                                                        raw_data=row.html_path,
                                                        domain=row.site_url)
                elif name == 'cert_features': 
                    features = CertificateFeatures.get_features(feature_names=feature_names,
                                                            raw_data=FeaturesFetcher.fetch_certificate(row.domain),
                                                            available=True,
                                                            domain=row.domain)
                elif name == 'whois_features': 
                    features = WhoisFeatures.get_features(feature_names = feature_names,
                                                          raw_data = FeaturesFetcher.fetch_whois(row.domain),
                                                          available=True,
                                                          domain = row.domain)
                else:
                    features = pd.DataFrame()

                df_row = pd.concat([df_row, features], axis=1)
            df = pd.concat([df, df_row], axis=0)

            df = df.reset_index(drop=True)  # Reset the index of df
            final_df = pd.concat([final_df, df], axis=0, ignore_index=True)  # Append the row's features to final_df

        return final_df

