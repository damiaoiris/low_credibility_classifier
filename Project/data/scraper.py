from pathlib import Path
from typing import Optional
from datetime import datetime
import pandas as pd 
import sys
import os 
import sqlite3 

current_dir = os.path.realpath(__file__)
par_dir = os.path.dirname(os.path.dirname(current_dir))
util_dir = os.path.join(par_dir, "util")
data_dir = os.path.join(par_dir,"data")
sys.path.append(util_dir)
sys.path.append(data_dir)
from utils import parse_ps_plus_1

from constants import OPEN_WPM_PATH, OUTPUT_DIR, DEFAULT_AUDIT_NAME
sys.path.append(OPEN_WPM_PATH)
from openwpm.command_sequence import CommandSequence
from custom_command import LinkCountingCommand, ScroolDown
from openwpm.commands.browser_commands import (
    GetCommand,
    ScreenshotFullPageCommand,
    RecursiveDumpPageSourceCommand,
)
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.storage.leveldb import LevelDbProvider
from openwpm.task_manager import TaskManager


class Crawler (object): 

    """ 
        Run a crawler using openwpm 
            browser_n: int; number of crawlers to visit the websites in parallel, set to 1
            headless: bool; Set to true if you want the crawler to be runing on the background
            websites_type: str; from what database we want to collect 
            websites: str; path to the websites folder 
            save_content: bool = True
            save_screenshots: bool = False; 
            output_dir: str; output to save the results 
            audit_name: str; by default is "test_audit"
            seed_profile: str; path to run the browser with I don't care about cookies extension

        This crawler scrapes the websites and collects the html of each one
    """

    def __init__(
        self, 
        browser_n: int = 1,
        headless: bool = False,  
        websites: Optional[list] = ["https://web.lip.pt/"],
        save_content: bool = True,
        save_screenshots: bool = False, 
        output_dir: str = OUTPUT_DIR, 
        audit_name: str = DEFAULT_AUDIT_NAME , 
        seed_profile: Optional[str] = None,
        ) -> None:


        self.browser_n = browser_n 

        if headless: 
            self.headless_mode = "headless"
            print("[+] Running the browser instance in headless mode")
        else: 
            self.headless_mode = "native"
            print("[+] Running the browser instance in native (visible) mode")

        self.websites = websites
        self.save_content = save_content 
        self.save_screenshots = save_screenshots
        self.output_dir = output_dir
        self.seed_profile = seed_profile
        self.audit_name = audit_name

        ## Create some relevant directories

        # output sqlite database
        self.output_db = Path(
            os.path.join(self.output_dir, self.audit_name + ".sqlite")
        )
        # output content db
        self.content_db = Path(os.path.join(self.output_dir, "saved_content"))

        ## Define the manager parameters
        self.manager_config()
        ## Define the browser params
        self.browser_config()

    def get_failed_visits(self):
        """Fetch the visits which failed during the crawl"""
        """Count failed visits during the crawl"""
        query = """
        SELECT DISTINCT c.*, v.site_url
        FROM crawl_history as c JOIN site_visits as v ON
        c.visit_id = v.visit_id AND c.browser_id = v.browser_id
        WHERE c.command == "GetCommand" AND c.error IS NOT NULL;
        """
        with sqlite3.connect(self.output_db) as con:
            result = pd.read_sql_query(sql=query, con=con)
        return result[["browser_id", "visit_id", "site_url", "error", "retry_number"]]

    def browser_config(self) -> None:
        # create a browser params instance for all browsers
        browser_params = [
            BrowserParams(display_mode = self.headless_mode) for _ in range(self.browser_n)
        ]
        print(browser_params)
        # define the remaining browser parameters
        for browser_param in browser_params:
            # Record HTTP Requests and Responses
            browser_param.http_instrument = True
            # Record cookie changes
            browser_param.cookie_instrument = True
            # Record Navigations
            browser_param.navigation_instrument = True
            # Record JS Web API calls
            browser_param.js_instrument = True
            # Record the callstack of all WebRequests made
            browser_param.callstack_instrument = True
            # Record DNS resolution
            browser_param.dns_instrument = True
            # Bot mitigation
            browser_param.bot_mitigation = True
            # allow third party cookies
            browser_param.tp_cookies = "always"
            # do not track options
            browser_param.donottrack = False
            # tracking protection
            browser_param.tracking_protection = False

            if self.seed_profile:
                browser_param.seed_tar = Path(self.seed_profile)
                print(browser_param.seed_tar)
    
            # resources to save
            browser_param.save_content = self.save_content
            self.browser_params = browser_params

    def manager_config(self) -> None:
        # Loads the default ManagerParams and NUM_BROWSERS copies of the default BrowserParams
        manager_params = ManagerParams(num_browsers=self.browser_n)
        # Update TaskManager configuration (use this for crawl-wide settings)
        manager_params.data_directory = Path(self.output_dir)
        manager_params.log_path = Path(
            os.path.join(self.output_dir, f"{self.audit_name}.log")
        )
        self.manager_params = manager_params

    def scraping(
            self, 
    ) -> pd.DataFrame:
        if self.websites: 
            unstructed_content_provider = (
                None
                if not self.save_content
                else LevelDbProvider(Path(self.content_db))
            )
            with TaskManager(
                self.manager_params,
                self.browser_params,
                structured_storage_provider=SQLiteStorageProvider(Path(self.output_db)),
                unstructured_storage_provider=unstructed_content_provider,
            ) as manager:
                # Visits the sites
                for index, site in enumerate(self.websites):
                    def callback(success: bool, val: str = site) -> None:
                        print(
                             f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
                             )

                    # Parallelize sites over all number of browsers set above.
                    command_sequence = CommandSequence(
                        site,
                        site_rank=index,
                        callback=callback,
                    )

                    # Start by visiting the page
                    command_sequence.append_command(GetCommand(url=site, sleep=3), timeout=60)
                    command_sequence.append_command(ScroolDown())
                    command_sequence.append_command(
                            RecursiveDumpPageSourceCommand(domain = parse_ps_plus_1(site), suffix=self.audit_name)
                        )

                    # Run commands across all browsers (simple parallelization)
                    manager.execute_command_sequence(command_sequence)
                    
                         