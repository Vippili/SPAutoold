from googleapiclient.http import MediaFileUpload
from Google import Create_Service
import os
from datetime import date
import pandas as pd
from pathlib import Path

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

#reads the config file
config = pd.read_csv("app_config.csv")
name = list(config['CSV Name'])[0]
name = name.replace(" ", "_")
apple_device = list(config['Apple Device'])[0]
start_file_path = r'/Users'
#need to add windows support
if not apple_device:
    start_file_path = r'C:\\Users'
for root, dirs, files in os.walk(start_file_path): #/Users is for mac only (WINDOWS is C:\)
    for x in files:
        if x == "SF_Ready.csv":
            PATH = os.path.abspath(os.path.join(root, x))

directory = Path(os.path.dirname(PATH))

renamed_files = []
upload_files = ['app_input.csv','attom_input_processed.csv','attom_input.csv','neverbounce_input_NBout.csv','neverbounce_input_result.csv','preNB.csv','SF_Ready.csv','neverbounce_input.csv']
today = date.today()
timestamp = today.strftime("%m/%d/%y")
files = os.listdir(directory)

for f in upload_files:
    old_file_path = directory / f
    temp = os.path.splitext(f)[0]
    new_name = temp + '_' + name + '_' + timestamp + '.csv'
    new_name = new_name.replace('/', '_')
    old_file_path.rename(directory / new_name)
    #new_file_path = directory + '/' + new_name
    #os.rename(f, new_name)
    renamed_files.append(new_name)
    print(f + ' renamed')

print(renamed_files)
final_folder_id = '1K3PxxG0flg7do7z6rG5QzBxg-grYWM4X'
pre_attom_folder_id = '1OPHTSYQ9nIDDlDYAQDk_bauy5z_uvPjB'
pre_bl_folder_id = '1_TxVd3Tfj13G-MiGrWxIAP5OhR_C7RHC'
pre_nb_folder_id = '14zyF5-W4VFIPY3Fms75LKiAQGzYu60QZ'
pre_sf_folder_id = '1TRkgm7xgAPHfdhxgde1Aoq-NF-uT48Xq'
mime_types = 'text/csv'
 
file_metadata = {'name': renamed_files[0], 'parents' : [pre_bl_folder_id]}
media = MediaFileUpload(renamed_files[0], mimetype= mime_types)
service.files().create(
    body=file_metadata,
    media_body = media,
    fields = 'id'
).execute()

file_metadata = {'name': renamed_files[2], 'parents' : [pre_attom_folder_id]}
media = MediaFileUpload(renamed_files[2], mimetype= mime_types)
service.files().create(
    body=file_metadata,
    media_body = media,
    fields = 'id'
).execute()


file_metadata = {'name': renamed_files[3], 'parents' : [pre_sf_folder_id]}
media = MediaFileUpload(renamed_files[3], mimetype= mime_types)
service.files().create(
    body=file_metadata,
    media_body = media,
    fields = 'id'
).execute()

file_metadata = {'name': renamed_files[5], 'parents' : [pre_nb_folder_id]}
media = MediaFileUpload(renamed_files[5], mimetype= mime_types)
service.files().create(
    body=file_metadata,
    media_body = media,
    fields = 'id'
).execute()

file_metadata = {'name': renamed_files[6], 'parents' : [final_folder_id]}
media = MediaFileUpload(renamed_files[6], mimetype= mime_types)
service.files().create(
    body=file_metadata,
    media_body = media,
    fields = 'id'
).execute()

print('Uploaded to Google Drive')

for remove_file in renamed_files:
    if os.path.exists(remove_file):
        os.remove(remove_file)
    else:
        print(remove_file + ' does not exsist, if it does exsist please check code.')
print('augmentation process complete!')