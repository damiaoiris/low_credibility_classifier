import argparse
import sys
import os
import sqlite3
import pandas as pd
current_dir = os.path.realpath(__file__)
par_dir = os.path.dirname(current_dir)
sys.path.append(par_dir)
from scraper import Crawler
from constants import BROWSER_N, SEED_PROFILE, OUTPUT_DIR, sites_to_test


class Collector():

    def __init__(self, 
                audit_name: str = "test_audit",
                sites_to_visit: list = sites_to_test, 
                headless: bool = False) -> None:
        self.audit_name = audit_name
        self.sites_to_visit = sites_to_visit
        self.headless = headless
        self.save_content = True
        output_dir = OUTPUT_DIR
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)        

        # Create the folder and save it
        parent_output_dir = os.path.join(output_dir, self.audit_name)
        if not os.path.isdir(parent_output_dir):
            os.mkdir(parent_output_dir)
        self.parent_output_dir = parent_output_dir
    
    
    def run_scraper(self):
        
        audit = Crawler(
            browser_n = BROWSER_N,
            headless = self.headless,
            websites = self.sites_to_visit,
            save_content = self.save_content,
            save_screenshots=False,
            output_dir = self.parent_output_dir,
            audit_name = self.audit_name,
            seed_profile = SEED_PROFILE,
            )
        audit.scraping()
        failed = audit.get_failed_visits()

        return failed

