from collector import Collector 
import os 
from pathlib import Path
import pandas as pd 
import argparse

cur_dir = os.path.dirname(os.path.abspath(__file__))
path_to_fake = os.path.join(cur_dir, "Fake_News.csv")
path_to_non_fake = os.path.join(cur_dir, "manual_list_not_FN.csv")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-w",
        "--website-type",
        dest="website_type",
        nargs="?",
        type = str,
        default= "FN",
        help="What DB you want to scrape, FN or NFN",
    )

    # headless flag
    parser.add_argument(
        "-headless", 
        dest="headless", 
        type=bool, 
        default=False,
        help="Run headless?"
    )

    # trial name
    parser.add_argument(
        "-n",
        "--trial-name",
        dest="audit_name",
        nargs="?",
        type=str,
        default="test_trial",
        help="Trail name to be used as a prefix to the name of the directory/db/profile of the crawl session",
    )

    args = parser.parse_args()

    if args.website_type == "FN":
        get_websites = pd.read_csv(path_to_fake, sep=";")
        websites = get_websites["Website"].tolist()
        print(websites)
        folder = "FN_" + args.audit_name 
        start = Collector(audit_name = folder,
                          sites_to_visit = websites, 
                          headless = args.headless)
        failed = start.run_scraper()
        failed.to_csv("failed_{folder}.csv")
    else:
        get_websites = pd.read_csv(path_to_non_fake, sep=";")
        websites = get_websites["website"].tolist()
        folder = "NFN_" + args.audit_name 
        start = Collector(audit_name = folder,
                          sites_to_visit = websites, 
                          headless = args.headless)
        failed = start.run_scraper()
        failed.to_csv("failed_{folder}.csv")

if __name__ == "__main__":
    ## parse CLI args
    main()