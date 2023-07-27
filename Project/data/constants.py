from pathlib import Path
import os 

OPEN_WPM_PATH = "/Users/irisdamiao/model/OpenWPM"

OUTPUT_DIR = "/Users/irisdamiao/model/Project/results"

# Number of different browsers profiles: 
BROWSER_N = 1

# Number of websites, if none all will be used
WEBSITES_N = None

# Gets the seed to run browser with I don't Care About Cookies -> clicks automatically in accepting cookies for you 
SEED_PROFILE = "/Users/irisdamiao/model/Project/resources/profile.tar"

# default audit name
DEFAULT_AUDIT_NAME = "test_audit" 

# The current list of websites to visit
sites_to_test = [
    "https://www.publico.pt/",
    "https://www.nytimes.com/",
    # "https://expresso.pt/",
    # "https://pressgazette.co.uk", 
    # "https://www.msn.com",
    # "https://www.theguardian.com/international",
]

# social media 
SOCIAL_MEDIA = ["https://www.facebook.com/", 
                "https://www.linkedin.com",
                "https://twitter.com",
                "https://www.tiktok.com",
                "https://www.youtube.com",
                "https://github.com",
                "https://www.pinterest.com/",
                "https://www.instagram.com/",
                "https://www.snapchat.com/",
                "https://flipboard.com/",
                "https://www.flickr.com",
                "weibo",
                "https://soundcloud.com/",
                "https://vimeo.com",
                "https://www.slideshare.net/",
                "https://vk.com/",
                "https://www.xing.com"]
