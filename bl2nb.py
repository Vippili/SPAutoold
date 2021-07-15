import numpy as np
import pandas as pd
import os
from pathlib import Path


#sets the max columns and rows that are displayed
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 2000)


def initialize():
    #get the file and drop unneeded columns
    read_filename = 'preNB.csv'
    intial_path = Path(os.path.dirname(os.path.abspath(__file__)))
    input_file = intial_path / read_filename
    leads = pd.read_csv(input_file)
    #removes all unneeded columns
    leads = leads.drop(columns=['Updated_Full_Address','Updated_City','Updated_State','Updated_Zip','Updated_Zip_Four','Updated_Street','Status_1','Caller_ID_1','Phone_Type_1',
    'Status_2','Caller_ID_2','Phone_Type_2','Status_3','Caller_ID_3','Phone_Type_3','Status_4','Caller_ID_4','Phone_Type_4','Status_5','Caller_ID_5','Phone_Type_5',
    'Bad_Phone_1','Bad_Phone_2','Bad_Phone_3','Bad_Phone_4','Bad_Phone_5'])
    return leads

def phone_mutation(leads):
    #extract the phone numbers and shift the columns to the left (same as excels "go to special, delete, shift rows left")
    phones = leads[['Phone_1','Phone_2','Phone_3','Phone_4','Phone_5']]
    v = phones.values
    a = [[n]*v.shape[1] for n in range(v.shape[0])]
    b = pd.isnull(v).argsort(axis=1, kind = 'mergesort')
    new_phones = v[a,b]

    #make the phones into a table and rename the columns
    new_phones = pd.DataFrame(new_phones)
    new_phones.columns = ["Phone_1","Phone_2","Phone_3","Phone_4","Phone_5" ]

    leads = leads.drop(columns = ['Phone_1','Phone_2','Phone_3','Phone_4','Phone_5'])

    #replace the Phone columns in the original leads list with the new table that shifted the rows left
    for column in new_phones.columns:
        leads[column] = new_phones[column]

    #remove any rows in the leads that do not have any phone numbers
    leads['Phone_1'] = leads['Phone_1'].replace([np.nan],'N/A')   
    for i in range(len(leads["Phone_1"])):
        if leads['Phone_1'][i] == "N/A":
            leads = leads.drop(i)    
    return leads

def index_number(leads):
    #adds the NB Number column into the table
    leads.insert(0, 'NB Number', range(1, 1 + len(leads)))
    return leads    

def execute():
    leads = initialize()
    leads = phone_mutation(leads)
    leads = index_number(leads)
    #export csv
    leads.to_csv('neverbounce_input.csv',index = False)
    print('finished modifications')
    #starting Neverbounce program
    intial_path = Path(os.path.dirname(os.path.abspath(__file__)))
    nb_path = intial_path / 'neverbounce.py'
    os.system(f'python3 {nb_path}')
    print("finished nb, waiting for sf augmentation")


execute()