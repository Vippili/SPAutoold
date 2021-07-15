import numpy as np
import pandas as pd
import os
from pathlib import Path

#sets the max columns and rows that are displayed
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 2000)


#reads the input file


#removes all failures
#leads = leads[leads['matchCode'] == 'ExaStr']
def initialize():
    read_filename = 'attom_input_processed.csv'
    intial_path = os.path.dirname(os.path.abspath(__file__))
    intial_path = Path(intial_path)
    input_file = intial_path / read_filename
    leads = pd.read_csv(input_file)
    #removes all unneeded columns
    leads = leads.drop(columns=['absentee','proptype','postal_attom','lat_attom','long_attom','owner2_first','owner2_last','baths1qtr','bathshalf','baths3qtr','bathsfull','bathscalc','roomstotal','pool','value_range','trustname_first','trustname_last'])
    print('done')
    return leads
#if first and last are empty, replaces rows, else, replaces to N/A
def first_last(leads):
    if leads['first'].isnull().all():
        leads['first'] = leads['First']
    if leads['last'].isnull().all():
        leads['last'] = leads['Last']

    leads['first'] = leads['first'].replace([np.nan],'N/A')   
    leads['last'] = leads['last'].replace([np.nan],'N/A')    

    for i in range(len(leads["first"])):
        if leads['first'][i] == 'N/A' and leads['last'][i] == 'N/A':
            leads = leads.drop(i)

    leads = leads.drop(columns =['owner1_first','owner1_last','First','Last'])
    return leads

#bedrooms column 
#if the raw data already has bedrooms, use that, else use the bedrooms from attom 
def bedrooms(leads):
    if 'bedrooms_original' in leads.columns.values:
        leads = leads.rename(columns={"bedrooms_original":"bedrooms"})
        leads = leads.drop(columns =['beds_title'])
    else:
        leads = leads.rename(columns={"beds_title":"bedrooms"})
    return leads

#if bathrooms exist or use a diff column, then split into full and half
def bathrooms(leads):
    if 'bathrooms' not in leads.columns.values:
        leads = leads.rename(columns={"bathstotal":"bathrooms"})
    else:
        leads = leads.drop(columns =['bathstotal'])
    leads['bathrooms'] = leads['bathrooms'].astype(float).map(str)
    leads[['full bathrooms', 'half bathrooms']] = leads.bathrooms.str.split(".", expand = True)
    leads['half bathrooms'] = leads['half bathrooms'].replace(['0.25','0.5','0.75','25','50','75'], '1')
    leads = leads.drop(columns = ['bathrooms'])

    return leads


def execute():
    intial_path = os.path.dirname(os.path.abspath(__file__))
    intial_path = Path(intial_path)
    attom_path = intial_path / 'attom.py'
    #run the attom program before running the cleaning script
    os.system(f'python3 {attom_path}')
    print('run attom')
    print(intial_path)
    leads = initialize()
    leads = first_last(leads)
    leads = bedrooms(leads)
    leads = bathrooms(leads)
    #export csv
    leads.to_csv('app_input.csv',index = False)
    print('finished modifications')


        