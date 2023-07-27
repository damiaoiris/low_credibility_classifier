# Low_credibility_classifier
A Low-Credibility Website Classifier Developed for the Statistical Learning Course at IST 

## A very modest attempt to build a low-credibility website classifier 

### Introduction
This repository houses our initial attempt at building a low-credibility website classifier. The goal of this project is to identify websites that tend to publish or host fake content, categorizing them as low-credibility.

### Project 
In this project we built a classifier of low-credbility websites using a Random Forest Model. The code for the classifier can be found in the "Project" folder. Although the results of our initial implementation were not as successful as we hoped, we believe it serves as a valuable starting point for future improvements.

#### Features and Data
The classifier employs 34 features, which are detailed in the "config_features.json" file within the "Project" folder. These features were collected, cleaned, and utilized to train the Random Forest Model.

#### Future Steps and Improvements may include:  
  - Better DB design (better division of the DB and more data);  - More elaborated features;


### The code layout (inside the Project folder) is the following: 
  - data folder: This folder contains the low-credibility and regular_websites DB. It also contains the code written to build openwpm scrapers and collect all the HTML data. We used OpenWPM (https://github.com/openwpm/OpenWPM) to collect HTML, as typically performs better rendering iframes (my own experience). Additionally, the idea was that by using OpenWPM we could easily extend our model to include features related with tracking and ads. 
  - The results of the OpenWPM used in this work were not included in this remote repository as they are too heavy. However, one can ask me to have them (to reproduce results), or can always run the file scrape_websites.py inside the data folder for any list of websites.
  - Inside the features folder one can find the code to generate a pipeline to get the features for each website. The pipeline is put into action when one runs the file make_features_DB. (In the notebook getting_features_DB.ipynb 2 csv files are built with all the features for low-credibility and not low_credibility DB)
  - After having the features DB, we curated them and built a Random Forest model -> Can be seen in the notebook present inside the classifier folder. There are other attempts to build the clasifer there (inspired by the work of Hounsel et al.), but at the end we did not use them.
  -  util: has important stuff for our code, but that are not main functions. resources: has stuff made for run openWPM.
