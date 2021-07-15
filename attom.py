#imports 
import numpy as np
import pandas as pd
import requests
import json
import time

import zipfile
import io
from nameparser import HumanName



#sets the max columns and rows that are displayed
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 2000)



#reads the config file
config = pd.read_csv("app_config.csv")

#assigns var to string
read_filename = 'attom_input'


#Gets the TRUE/FALSE values for each of the parameters
has_postalCode = list(config['Has postalCodes'])[0]
has_names = list(config['Has Names'])[0]
names_onecolumn = list(config['Full Names'])[0]
minimum_bedrooms = list(config['Minimum Bedrooms'])[0]
has_bedrooms = list(config['Has Bedrooms'])[0]



#accept data in a json format -- HTTP Headers to send with request
headers = {'Accept': 'application/json', 'apikey': '6a0b9f5040cda24f00cebec3f0f0971d'}



#reads the attom_input file
houses = pd.read_csv(read_filename + '.csv')

def parse_postalCode(x):
    try:
        return str(x).strip().replace('\r','').replace('\n','')[0:5]
    except:
        return ''
    
    
houses['postalCode'] = houses['postalCode'].map(parse_postalCode)

def replace_rn(x):
    try:
        return x.replace('\r','').replace('\n','')
    except:
        try:
            return x
        except:
            return ''

#get first + middle name, if not then just return a blank
def get_first(x):
    try:
        return HumanName(x).first + ' ' + HumanName(x).middle
    except:
        return ''
#get last name, if not, return a blank    
def get_last(x):
    try:
        return HumanName(x).last
    except:
        return ''
#function that splits by &, otherwise returns the value
def get_AND_1(x):
    try:
        if '&' in x:
            return x.split('&')[0].strip()
        else:
            return x
    except:
        return x

#Takes in a value and formats it
def clean_string_title(x):
    try:
        return (' '.join(x.lower().split())).title()
    except:
        return ' '


#If the length is < 2, return false, else check if each index in the array is > 1, if at least one is, return true

def is_full(x):
    #split by space
    x = x.split(' ')
    if len(x) < 1.5:
        return False
    elif len(x) > 1.5:
        count_noninitials = 0
        
        for substr in x:
            if len(substr) > 1.5:
                count_noninitials += 1
                
            
        return (count_noninitials > 1)

# def reorder_name(name):
#     first = ''
#     first_taken = False
    
#     last = ''
#     last_taken = False
    
#     name = name.split(' ')
#     for word in name:
#         if not first_taken and len(word) > 1.5:
            
    
def get_first_name(x):
    #Splits by & and then strips each index and puts into a list (x)
    x = list(map(lambda y: y.strip(), x.split('&')))
    
    #If string is filled, get the First + Middle name 
    if is_full(x[0]):
        return get_first(x[0]).title()
    else:
        return x[0]

#same as previous function but with last name instead, if no last name return 'xxx'    
def get_last_name(x):
    x = list(map(lambda y: y.strip(),x.split('&')))
    
    if is_full(x[0]):
        return get_last(x[0]).title()
    else:
        try:
            return get_last(x[1]).title()
        except:
            return 'xxxx'



#if full name split into first and last
if has_names and names_onecolumn:
    houses['First'] = houses['Full'].map(get_first_name)
    houses['Last'] = houses['Full'].map(get_last_name)



#if an integer is greater than 3 return true
def br_bool(x):
    try:
        if int(x) > 3:
            return True
        else:
            return False
    except:
        return False


#if the lead has bedrooms then augment the column
if has_bedrooms:
    houses = houses[houses['bedrooms_original'] > (minimum_bedrooms - .5)]





def to_url_detail(row):
    site_request = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/attomavm/detail?"
    
    try:
        street1 = row['street'].replace(' ','+')
        site_request = site_request + 'address1=' + street1
    except:
        print("error in reading street1")
        street1 = "0"
        
    site_request = site_request + '&address2='
    
    next_char = ''
    try:
        city = str(row['city'].replace(' ','+'))
        site_request = site_request + city
        next_char = '+'
    except:
        print('error in reading city')
        city = ''
        
    try:
        state = str(row['state']).replace(' ','+')
        site_request = site_request + next_char + state
        next_char = '+'
    except:
        state = ''
        print('error in reading state') 
    
    try: 
        zipcode = row['postalCode']
        site_request = site_request + next_char + zipcode
    except:
#         print('failed zip')
        zipcode = ''
        
    print(street1 + ', ' + city + ', ' + state + ' ' + zipcode)
    
    return site_request
    



#returns built url about the owner
def to_url_owner(row):
    site_request = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detailowner?"
    
    try:
        street1 = row['street'].replace(' ','+')
        site_request = site_request + 'address1=' + street1
    except:
        print("error in reading street1")
        street1 = "0"
        
    site_request = site_request + '&address2='
    
    next_char = ''
    try:
        city = str(row['city'].replace(' ','+'))
        site_request = site_request + city
        next_char = '+'
    except:
        print('error in reading city')
        city = ''
        
    try:
        state = str(row['state']).replace(' ','+')
        site_request = site_request + next_char + state
        next_char = '+'
    except:
        state = ''
        print('error in reading state') 
    
    try: 
        zipcode = row['postalCode']
        site_request = site_request + next_char + zipcode
    except:
#         print('failed zip')
        zipcode = ''
        
    print(street1 + ', ' + city + ', ' + state + ' ' + zipcode)
    
    return site_request




#for the row, gets the response, if status code > 499, wait for 2 min and try again, get the json content
def get_output_detail(row):
    try:
        r_d = requests.get(to_url_detail(row), headers = headers)
        if r_d.status_code > 499:
            time.sleep(120)
            return get_output_detail(row)
    except:
        time.sleep(120)
        return get_output_detail(row)
    
    print(r_d)
    r_d = r_d.json()
    return r_d

#make a request and get the owner information, if error, wait 2 min, get json information outputted
def get_output_owner(row):
    try:
        r_o = requests.get(to_url_owner(row), headers = headers)
        if r_o.status_code > 499:
            time.sleep(120)
            return get_output_owner(row)
    except:
        time.sleep(120)
        return get_output_owner(row)
    
    print(r_o)
    r_o = r_o.json()
    return r_o





#set all the columns to empty arrays         
matchCode = []

absentee = []
proptype = []

value = []
value_range = []

pool = []
lot_size = []
homesize = []

beds = []
baths1qtr = []
bathshalf = []
baths3qtr = []
bathsfull = []
bathscalc = []
bathstotal = []
roomstotal = []

owner1_first = []
owner1_last = []
owner2_first = []
owner2_last = []
owner_mailing = []

lat = []
long = []
postal = []

i = 0
#iterate over the rows -- for every row in the csv, do these actions. 
for index,row in houses.iterrows():
    #get jsons of property and owner details for that row 
    r_d = get_output_detail(row)
    
    r_o = get_output_owner(row)
    
    #try printing the status + msg of the jsons, if it fails the status failed
    try:
        print(r_d['status']['msg'])
        print(r_o['status']['msg'])
    except:
        print('status printing failed')
    #print the property address's matchcode, and add it to the array
    try:
        print(r_d['property'][0]['address']['matchCode'])
        matchCode += [r_d['property'][0]['address']['matchCode']]
    except:
        print('matchCode not work')
        matchCode += ['failure']
    #add the value, else add "NONE"
    try:
        absentee += [r_d['property'][0]['summary']['absenteeInd']]
    except:
        absentee += [None]
        
    try:
        proptype += [r_d['property'][0]['summary']['proptype']]
    except:
        proptype += [None]
        
    try:
        value += [r_d['property'][0]['avm']['amount']['value']]
    except:
        value += [None]
    
    try:
        value_range += [r_d['property'][0]['avm']['amount']['valueRange']]
    except:
        value_range += [None]
    
    try:
        pool += [r_d['property'][0]['lot']['pooltype']]
    except:
        pool += [None]
        
    try:
        lot_size += [r_d['property'][0]['lot']['lotsize2']]
    except:
        lot_size += [None]
        
    try:
        homesize += [r_d['property'][0]['building']['size']['universalsize']]
    except:
        homesize += [None]
        
    try:
        beds += [r_d['property'][0]['building']['rooms']['beds']]
    except:
        beds += [None]
        
    try:
        baths1qtr += [r_d['property'][0]['building']['rooms']['baths1qtr']]
    except:
        baths1qtr += [None]
        
    try:
        bathshalf += [r_d['property'][0]['building']['rooms']['bathshalf']]
    except:
        bathshalf += [None]
        
    try:
        baths3qtr += [r_d['property'][0]['building']['rooms']['baths3qtr']]
    except:
        baths3qtr += [None]
        
    try:
        bathsfull += [r_d['property'][0]['building']['rooms']['bathsfull']]
    except:
        bathsfull += [None]
        
    try:
        bathscalc += [r_d['property'][0]['building']['rooms']['bathscalc']]
    except:
        bathscalc += [None]
        
    try:
        bathstotal += [r_d['property'][0]['building']['rooms']['bathstotal']]
    except:
        bathstotal += [None]
        
    try:
        roomstotal += [r_d['property'][0]['building']['rooms']['roomsTotal']]
    except:
        roomstotal += [None]
        
    try:
        owner1_first += [r_o['property'][0]['owner']['owner1']['firstnameandmi']]
    except:
        owner1_first += [None]
        
    try:
        owner1_last += [r_o['property'][0]['owner']['owner1']['lastname']]
    except:
        owner1_last += [None]
        
    try:
        owner2_first += [r_o['property'][0]['owner']['owner2']['firstnameandmi']]
    except:
        owner2_first += [None]
        
    try:
        owner2_last += [r_o['property'][0]['owner']['owner2']['lastname']]
    except:
        owner2_last += [None]
        
    try:
        owner_mailing += [r_o['property'][0]['owner']['mailingaddressoneline']]
    except:
        owner_mailing += [None]
           
    try:
        postal += [r_o['property'][0]['address']['postal1']]
    except:
        postal += [None]
        
    try:
        lat += [r_o['property'][0]['location']['latitude']]
    except:
        lat += [None]
        
    try:
        long += [r_o['property'][0]['location']['longitude']]
    except:
        long += [None]
        
    #wait for one second    
    time.sleep(1)

    #print the index and street + city
    try:
        print(str(i) + ": " + str(row['street'])+'|'+str(row['city']))
    except:
        print('idk')
    
#     try:
#         print(str(owner1_first[i]) + str(owner1_last[i]))
#     except:
#         print('idk2')
    
    i = i+1



#assign the columns
houses['matchCode'] = matchCode

houses['absentee'] = absentee
houses['proptype'] = proptype

houses['owner1_first'] = owner1_first
houses['owner1_last'] = owner1_last

houses['postal_attom'] = postal
houses['lat_attom'] = lat
houses['long_attom'] = long

#if it doesnt have names, set the First name and Last name to the owner1_first/last
if not has_names:
    houses['First'] = owner1_first
    houses['Last'] = owner1_last

#do the same for postal code 
if not has_postalCode:
    houses['postalCode'] = postal
    
houses['owner2_first'] = owner2_first
houses['owner2_last'] = owner2_last

houses['owner_mailing'] = owner_mailing
houses['beds_title'] = beds
houses['baths1qtr'] = baths1qtr
houses['bathshalf'] = bathshalf
houses['baths3qtr'] = baths3qtr
houses['bathsfull'] = bathsfull
houses['bathscalc'] = bathscalc
houses['bathstotal'] = bathstotal
houses['roomstotal'] = roomstotal
houses['homesize'] = homesize
houses['lot_size'] = lot_size
houses['pool'] = pool
houses['value'] = value
houses['value_range'] = value_range




#list of bad strings we want to avoid
badwords_substring = [
    'investments',
    'partner',
    'enterprise',
    'management',
    'properties',
    'property',
    'vacation',
    'holding',
    'apartment',
    'development',
    'l.p',
    'contracting',
    'law firm',
    'the killers',
    'rental',
    'partnership',
    'unknown',
    'travel',
    'homes',
    'ventures',
    'associates',
    'real estate',
    'realty',
    'limited',
    '(',
    ')',
    'xxxx'
]

#bad ends
badwords_ends = [
    ' inc',
    'inc '
    ' llc',
    'llc ',
    ' trust',
    'trust '
    'host ',
    ' host',
    'firm ',
    ' firm',
    'group ',
    ' group',
    'condo ',
    ' condo',
    ' xxxx',
    'xxxx '
]

badwords_wholestring = [
    'group',
    'trust',
    'inc',
    ' llc ',
    'trust',
    'host',
    'firm',
    'group',
    'homeowner',
    'owner',
    'various',
    'llc',
    'xxxx'
]

#boolean to see whether in that word is in the string
def is_trust(x):
    try:
        a = len(x)
    except:
        return True
    
    for bw in badwords_substring:
        if bw in x:
            return True
    
    for bw in badwords_ends:
        if bw == x[-len(bw):]:
            return True
        if bw == x[:len(bw)]:
            return True
        
    for bw in badwords_wholestring:
        if bw == x:
            return True
    
    return False



#clean the input, else return None
def clean_name(x):
    try:
        return x.lower().strip()
    except:
        return None



#clean data and reassign to the columns
houses['owner1_first'] = houses['owner1_first'].map(clean_name)
houses['owner1_last'] = houses['owner1_last'].map(clean_name)
houses['owner2_first'] = houses['owner2_first'].map(clean_name)
houses['owner2_last'] = houses['owner2_last'].map(clean_name)
if has_names:
    houses['First'] = houses['First'].map(clean_name)
    houses['Last'] = houses['Last'].map(clean_name)



#with names
if has_names:
    #create column for trust likely 
    is_trust_list = []
    for index, row in houses.iterrows():
        #initally set it to False for each row
        is_trust_row = False

        #if match code is not failure and the first and last names are trustworthy, return true
        if row['matchCode'] != 'failure':
            if is_trust(row['First']) or is_trust(row['Last']):
                is_trust_row = True

        is_trust_list += [is_trust_row]
else: #w/o names
    is_trust_list = []
    for index, row in houses.iterrows():
        is_trust_row = False

        #essentially same as above, checks diff columns though
        if row['matchCode'] != 'failure':
            if is_trust(row['owner1_first']) or is_trust(row['owner1_last']):
                is_trust_row = True
        #add each row to the array
        is_trust_list += [is_trust_row]



#capitalize properly 
def cap_name(x):
    try:
        return x.title()
    except:
        return None



#assign the trust list as the last column
houses['Trust_Likely'] = is_trust_list


#change a trust to a name
def trust_to_name(x):
    #for every word, add it to the substring if it isnt contained in the set of words
    try:
        x = x.split(' ')
        new_x = ''
        for substr in x:
            if substr in (badwords_substring + badwords_wholestring + ['trust','trus','trustee','tr','tru','ttee','company','share','family','of','the']):
                break
            else:
                new_x = new_x + ' ' + substr


        x = new_x.split(',')
        if len(x) == 1:
            temp = x[0].strip().split(' ')[0]
            return (temp,x[0].replace(temp,'').strip())
        else:
            try:
                return (x[1].strip(),x[0].strip())
            except:
                return (np.nan,np.nan)
    except:
        return (np.nan,np.nan)




#if no names -- create a trust first/last arrays and add them in by converting the owner last name (ONLY if 
# there is a trust_likely) through the trust to name program. 
if not has_names:
    trustname_first = []
    trustname_last = []
    for index,row in houses.iterrows():
        if row['Trust_Likely'] == True:
            temp = trust_to_name(row['owner1_last'])
            trustname_first += [temp[0]]
            trustname_last += [temp[1]]
        else:
            trustname_first += [np.nan]
            trustname_last += [np.nan]

    #assign to the table
    houses['trustname_first'] = trustname_first
    houses['trustname_last'] = trustname_last
else:
    trustname_first = []
    trustname_last = []
    for index,row in houses.iterrows():
        if row['Trust_Likely'] == True:
            if is_trust(row['owner1_first']) or is_trust(row['owner1_last']): #if no names, and the owner first/last name is a trust, add the value to the column
                temp = trust_to_name(row['owner1_last'])
                trustname_first += [temp[0]]
                trustname_last += [temp[1]]
            else:
                trustname_first += [row['owner1_first']]
                trustname_last += [row['owner1_last']]
        else:
            trustname_first += [np.nan]
            trustname_last += [np.nan]

    #assign to the table
    houses['trustname_first'] = trustname_first
    houses['trustname_last'] = trustname_last





#capitalize the names in each column
houses['owner1_first'] = houses['owner1_first'].map(cap_name)
houses['owner1_last'] = houses['owner1_last'].map(cap_name)
houses['owner2_first'] = houses['owner2_first'].map(cap_name)
houses['owner2_last'] = houses['owner2_last'].map(cap_name)
houses['trustname_first'] = houses['trustname_first'].map(cap_name)
houses['trustname_last'] = houses['trustname_last'].map(cap_name)

houses['First'] = houses['First'].map(cap_name)
houses['Last'] = houses['Last'].map(cap_name)






name1 = []
name2 = []
for index,row in houses.iterrows():
    if row['Trust_Likely']:
        name1 += [row['trustname_first']]
        name2 += [row['trustname_last']]
    else:
        name1 += [row['First']]
        name2 += [row['Last']]
#filter the trust names in the first/last names and assign to the First + Last name columns
houses['First'] = name1
houses['Last'] = name2




#export as a csv and name it as processed.
houses.to_csv(read_filename + '_processed.csv',index = False)
