import numpy as np
import pandas as pd
import os
from pathlib import Path

#sets the max columns and rows that are displayed
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 2000)

#
def initialize():
    #get the relevant data from the config file
    config = pd.read_csv("nb2sf_config.csv")
    market = list(config['Market'])[0]
    lead_owner = list(config['Lead Owner'])[0]
    lead_source_details = list(config["Lead Source Details"])[0]
    #get the file and drop unneeded columns
    read_filename = 'neverbounce_input_NBout.csv'
    intial_path = Path(os.path.dirname(os.path.abspath(__file__)))
    input_file = intial_path / read_filename
    leads = pd.read_csv(input_file)
    leads = leads.iloc[: , 2:]
    return leads, market, lead_owner, lead_source_details

def business_name(leads):
    #add in the business name column into the table
    business_name = []
    for i in range(len(leads)):
        street = leads["street"][i]
        city = leads["city"][i]
        b_name = street + " | " + city + " | New Business"
        business_name.append(b_name)

    leads.insert(loc=0, column="Business Name",value=business_name)
    return leads

def sf_req_columns(leads,market,lead_owner,lead_source_details):
    #add the market, lead owner, and lead source detail columns in the table
    leads.insert(1,"Market",market)
    leads.insert(2, "Lead Owner", lead_owner)
    leads.insert(3, "Lead Source Details", lead_source_details)   
    return leads

def rename(leads):
    #renaming the columns to fit SF standards
    leads.rename(columns= { 'first':'First Name', 'last':'Last Name','street':'Street','city':'City','state':'State','postalCode':'Postal Code',
    'bedrooms':'Bedrooms','full bathrooms':'Full Bathrooms','owner_mailing':'Homeowner Address',
    'homesize':'Square Feet','lot_size':'Lot Size','value':'Market Total Value'}, inplace=True)

    if "Phone_1" in list(leads.columns.values):
        leads.rename(columns= {'Phone_1':'Phone 1'}, inplace=True)
    if "Email_1" in list(leads.columns.values):
        leads.rename(columns= {'Email_1':'Email 1'}, inplace=True)

    return leads

def execute():
    leads, market, lead_owner, lead_source_details = initialize()
    leads = business_name(leads)
    leads = sf_req_columns(leads,market,lead_owner,lead_source_details)
    leads = rename(leads)
    #export csv
    leads.to_csv('SF_Ready.csv',index = False)

execute()