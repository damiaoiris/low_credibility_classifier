import pandas as pd
import json
import os
import gzip 
from pathlib import Path
from bs4 import BeautifulSoup
from data.constants import SOCIAL_MEDIA
import metadata_parser
from util.utils_DB import Database, make_soup_html
from util.utils import parse_ps_plus_1
import requests

class HTMLFeatures():

    @staticmethod
    def get_html(html_path: Path, domain: str) -> str:
        if html_path.exists():  # Check if the file exists
            try:
                with gzip.open(html_path, mode="rt") as f:
                    data = [json.loads(line) for line in f]
                html = data[0]["source"]
            except Exception as e:
                html = None
        else:
            html = None

        if not html:
            try:
                html = requests.get('http://' + domain, timeout=10).text
            except Exception as e:
                html = None
        return html
    
    @staticmethod
    def get_iframes(html_path: Path, domain:str) -> str:
        try:
            with gzip.open(html_path, mode="rt") as f:
                data = [json.loads(line) for line in f]
            iframes = data[0]["iframes"]
        except Exception as e:
            iframes = None
        if not iframes:
            try:
                html = requests.get('http://' + domain, timeout=10).text
            except Exception as e:
                html = None
            if html:
                main_soup = make_soup_html(html)
                iframes = main_soup.find_all('iframe')  
            else: 
                iframes = []
        return iframes
    
    @staticmethod
    def get_num_iframes(html_path: str, domain:str) -> int:
        _iframes = HTMLFeatures.get_iframes(html_path, domain)
        return len(_iframes)
    
    @staticmethod
    def has_active_socialmedia(html_path:Path, domain:str) -> bool: 
        _html = HTMLFeatures.get_html(html_path, domain)
        if _html:
            has_social_media = False
            #if it does not have href, it may have the social media logo but not the links
            html_souped = make_soup_html(_html)
            links = html_souped.find_all('a', href=True)
            for link in links:
                for s in SOCIAL_MEDIA: 
                    if s in link["href"]:
                        try:
                            req = requests.get(url=link["href"], timeout=10)
                            if req.status_code == 200:
                                has_social_media = True
                                break
                        except requests.exceptions.RequestException as e:
                            continue
            return has_social_media
        else: 
            return None
       
    @staticmethod
    def meta_tags(url): 
        # Collects all meta tags in url and analyzes it 
        try:
            response = requests.get(url, timeout=50)
            if response.status_code == 200:
                page_meta = metadata_parser.MetadataParser(url).metadata
                # og tags when specified determine how the share of the url in social media will look like
                meta_og = page_meta["og"]
                if not meta_og:
                    _has_og = False
                else: 
                    _has_og = True
                
                # Twitter meta tag -> specifies how it appears on twitter
                meta_twitter = page_meta["twitter"]
                if not meta_twitter: 
                    _has_twitter = False
                else: 
                    _has_twitter = True
                
                # It has a description -> to describe the site on Search Engines and/or Social Media
                strategy = ["meta", "og", "page", "dc"]
                save_description = None
                _has_description = None
                for s in strategy:
                    try:
                        meta_description = page_meta[s]["description"]
                    except: continue
                    if meta_description: 
                        _has_description = True
                        save_description = [meta_description]
                        break
                    else: 
                        _has_description = False 

                # Try to see if it uses keywords 
                save_keys = None
                try: 
                    keys_tags = page_meta["meta"]["keywords"]
                except: 
                    keys_tags = {}
                if not keys_tags:
                    _has_keywords = False
                else: 
                    _has_keywords = True 
                    save_keys = [keys_tags]

                return _has_og, _has_twitter, _has_description, _has_keywords, save_keys, save_description
            
            else:
                print(f"Error: Request failed with status code {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("Error: Request timed out.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def num_images(html_path:str, domain:str) -> int:
        _html = HTMLFeatures.get_html(html_path, domain)
        if _html:
            html_soup = make_soup_html(_html)
            n_images = len(html_soup.find_all("img"))
            return n_images
        else: return None

    def get_features(feature_names: dict, raw_data: Path, domain = str):

        features = feature_names
        _save, col = [], []

        if features["frames"]:
            n_iframes = HTMLFeatures.get_num_iframes(raw_data, domain)
            col.append(features["frames"][0])
            _save.append(n_iframes)

        if features["social_media"]:
            try:
                has_social = HTMLFeatures.has_active_socialmedia(raw_data, str(domain))
            except Exception as e:
                has_social = None
            col.append(features["social_media"][0])
            _save.append(has_social)

        if features["images"]:
            n_img = HTMLFeatures.num_images(raw_data, domain)
            col.append(features["images"][0])
            _save.append(n_img)

        if features["meta_tags"]:
            try:
                meta = HTMLFeatures.meta_tags(domain)
            except Exception as e:
                meta = None
            col.extend(features["meta_tags"])
            if meta:
                _save.extend(meta) 
            else: 
                _save.extend([None] * 6) 

        final_df = pd.DataFrame([_save], columns = col)
        return final_df


