from pathlib import Path
from typing import Optional
import sqlite3
import gzip 
import json
import os
from util.utils import parse_ps_plus_1
from bs4 import BeautifulSoup

import pandas as pd

class Database:

    """Database class to perform all functions associated with the OpenWPM crawl DB. 
    """

    def __init__(self, database_filename: Path):
        self.database_filename = database_filename
        self.conn = sqlite3.connect(self.database_filename)


    def __enter__(self):
        self.conn = sqlite3.connect(str(self.database_filename.resolve()))
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn is not None:
            self.conn.close()
        self.conn = None

    def website_from_visit_id(self, visit_id):

        """
        Function to get relevant table data for a particular website. 
        This data is ued to build graphs.

        Args:
            visit_id: Visit ID of the website we want.
        Returns:
            df_requests: DataFrame representation of requests table in OpenWPM.
            df_responses: DataFrame representation of responses table in OpenWPM.
            df_redirects: DataFrame representation of redirects table in OpenWPM.
            call_stacks: DataFrame representation of call_stacks table in OpenWPM.
            javascript: DataFrame representation of javascript table in OpenWPM.
        """

        if self.conn is None:
            raise sqlite3.ProgrammingError("Database not open")

        df_http_requests = pd.read_sql_query(
            "SELECT visit_id, request_id, "
            "url, headers, top_level_url, resource_type, "
            f"time_stamp, post_body, post_body_raw from http_requests where {visit_id} = visit_id",
            self.conn
        )
        df_http_responses = pd.read_sql_query(
            "SELECT visit_id, request_id, "
            "url, headers, response_status, time_stamp, content_hash "
            f" from http_responses where {visit_id} = visit_id",
            self.conn
        )
        df_http_redirects = pd.read_sql_query(
            "SELECT visit_id, old_request_id, "
            "old_request_url, new_request_url, response_status, "
            f"headers, time_stamp from http_redirects where {visit_id} = visit_id",
            self.conn
        )
        call_stacks = pd.read_sql_query(
            f"SELECT visit_id, request_id, call_stack from callstacks where {visit_id} = visit_id",
            self.conn
        )
        javascript = pd.read_sql_query(
            "SELECT visit_id, script_url, script_line, script_loc_eval, top_level_url, document_url, symbol, call_stack, operation,"
            f" arguments, value, time_stamp from javascript where {visit_id} = visit_id",
            self.conn
        )
        return df_http_requests, df_http_responses, df_http_redirects, call_stacks, javascript


    def sites_visits(self):

        """
        Function to get site visit table data.

        Returns:
            DataFrame representation of the site_visits table for successfully crawled sites.
        """
        if self.conn is None:
            raise sqlite3.ProgrammingError("Database not open")
        
        df_successful_sites = pd.read_sql_query(
            "SELECT visit_id, site_url FROM site_visits",
            self.conn
        )

        return df_successful_sites
    

def make_soup_html(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def RawDB(audit_name: str) -> pd.DataFrame:
    # Get current directory
    current_dir = os.getcwd()
    # Go to path directory
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

    #Navigate to results folder
    path_to_folder = os.path.join(parent_dir, "results", audit_name)
    path_to_sqlite = os.path.join(path_to_folder, f"{audit_name}.sqlite")

    # Get the DB with visit_id
    my_DB = Database(database_filename = path_to_sqlite)
    df_site_visits = my_DB.sites_visits()

    # Get visit_id and the html and iframes and return in data_frame for analysis 
    df_html = pd.DataFrame(columns=["site_url", "visit_id", "domain", "html_path"])
    for _,row in df_site_visits.iterrows():
        _domain = parse_ps_plus_1(row["site_url"])
        _visit_id = row["visit_id"]
        tpl = (str(_visit_id), _domain, audit_name)
        _file_name = "-".join(tpl) 
        _html = Path(os.path.join(path_to_folder, "sources", _file_name + ".json.gz"))

        df_row = {"site_url": row["site_url"],
                  "visit_id": _visit_id,
                  "domain": _domain,
                  "html_path": _html}
        df_html = pd.concat([df_html, pd.DataFrame(df_row, index=[0])], ignore_index=True)
    return df_html 