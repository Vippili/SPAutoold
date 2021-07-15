#imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import random
import smtplib, ssl
import os 
import numpy as np 
import pandas as pd
import datetime 
import a2b
from pathlib import Path
import bl2nb
import nb2sf

#reads the config file
config = pd.read_csv("app_config.csv")

#get the parameters
headless = False #set to true if you want program to run in the background
name = list(config['CSV Name'])[0]
name = name + ' ' + str(random.randint(0,99999)) #generates a unique name id 
apple_device = list(config['Apple Device'])[0]
start_file_path = r'/Users'
if not apple_device:
    start_file_path = r'C:\\Users'

for root, dirs, files in os.walk(start_file_path): #/Users is for mac only (WINDOWS is C:\)
    for x in files:
        if x == "chromedriver":
            PATH = os.path.abspath(os.path.join(root, x))
            print(PATH)

download_location = Path(os.path.dirname(os.path.abspath(__file__)))
print(download_location)

#new webdriver to allow for downloads
chromeOptions = Options()
if headless:
    chromeOptions.headless = True
chromeOptions.add_experimental_option("prefs", {"download.default_directory": str(download_location)})
driver = webdriver.Chrome(executable_path=PATH, options=chromeOptions)

#BL Username and Password + File Path of Input csv
username = "Dallas21"
password = "Tester2021!"
target_file = download_location / "app_input.csv"

#email prerequisites + email function
receive = list(config['Receiving Email'])[0] 
def email_sender(receive):
    port = 587
    sender_email = "avantstaybelle@gmail.com"
    sender_email_password = "bellebot"
    mesg = """Subject: BellesLink Step Complete 

        Hello! Your BellesLink Upload is ready. Procceding to next steps.

        Sent by:
        BellesLink Bot
        """
    context = ssl.create_default_context()
    print("Starting to send")
    smtpserver = smtplib.SMTP("smtp.gmail.com", port)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(sender_email, sender_email_password)
    smtpserver.sendmail(sender_email, receive, mesg)
    print("sent email!")
    
#logs in by entering the user and password, then pressing login. 
def bl_login(user, password):
    time.sleep(7) #change into 7
    search_login = driver.find_element_by_id("btnLogin")
    search_username = driver.find_element_by_id("txtUserName")
    search_password = driver.find_element_by_id("txtPassword")
    search_username.send_keys(user)
    time.sleep(2)
    search_password.send_keys(password)
    time.sleep(2)
    search_login.send_keys(Keys.RETURN)

#uploads the csv file via file path
def bl_fileUpload():
    time.sleep(2) #change to 7
    file_select = driver.find_element_by_xpath("//input[@id = 'ctl00_contentMain_uploadCtrl_TextBox0_Input']")
    file_select.send_keys(str(target_file))

#presses the process button (want to make more robust with the options)
def bl_process():
    time.sleep(5) #change to 7
    process = driver.find_elements_by_id("ctl00_contentMain_btnProcess")
    process[-1].send_keys(Keys.RETURN)
    
#fills in the name of the upload and presses submit
def bl_submit(name):
    time.sleep(4) #change to 7
    batch_name = driver.find_element_by_id("ctl00_contentMain_txtBatchName_I")
    batch_name.send_keys(name)
    submit = driver.find_element_by_id("ctl00_contentMain_btnSubmit")
    submit.click()
    time.sleep(2) #change to 7
    alert = driver.switch_to.alert
    alert.accept()

#BL Security about refreshing every 2 minutes
#searches for file, if not present wait ~2 minutes then run again, else download the file and notify the user
def bl_results(name):
    time.sleep(2)
    refresh_button = driver.find_element_by_id("ctl00_contentMain_Button1")
    refresh_button.click()
    time.sleep(4)
    search_name = driver.find_element_by_id("ctl00_contentMain_txtBatchName_I")
    search_name.send_keys(name)

    def bl_batch_search():
        try:
            refresh_button = driver.find_element_by_id("ctl00_contentMain_Button1")
            refresh_button.send_keys(Keys.RETURN)
            time.sleep(5)
            results = driver.find_element_by_id("ctl00_contentMain_grdSearchBatches_cell0_9_btnView")
            results.click()
            time.sleep(5)
            export_merged_results = driver.find_element_by_id("ctl00_contentMain_btnExportMerged")
            export_merged_results.click()
            print("csv downloaded")
            email_sender(receive)
        except:
            print("BL has not finished uploading results")
            wait_time = random.randint(240, 500)
            print("waiting for " + convert_time(wait_time) + " minutes before checking again.")
            time.sleep(wait_time)

            bl_batch_search()
    bl_batch_search()

#renaming processed file
def rename_file():
    path = download_location
    files = os.listdir(path)
    #exsisting_files = ["app_input.csv", "app.py", "app_config.csv", "a2b.py", "attom_input_processed.csv"]
    for f in files:
        if 'merged' in f.lower():
            filename = path / f
            filename.rename(path / "preNB.csv")
            #os.rename(path + "/" + f, path + "/preNB.csv")

#convert seconds to minutes for readability
def convert_time(wait_time):
    return str(datetime.timedelta(seconds = wait_time))

#main method
if __name__ == "__main__":
    a2b.execute()
    print(PATH)
    print(" \n")
    print("Your file name is " + name)
    print(download_location)
    driver.get("https://www.bellescamp.com/BellesLinkLogin.aspx?ReturnUrl=%2fSearchUploadBatch.aspx")
    bl_login(username, password)
    bl_fileUpload()
    bl_process()
    bl_submit(name)
    time.sleep(10) #add like 10 minute wait timer in the actual implementation
    #driver.close()
    driver.get("https://www.bellescamp.com/SearchUploads.aspx")
    bl_results(name)
    time.sleep(5)
    driver.close()
    rename_file()
    print("Success! Your BL File is complete!")
    bl2nb.execute()
    nb2sf.execute()
    print("finished uploading final SF ready to cloud")
    #remove_files = ['app_input.csv','attom_input_processed.csv','attom_input.csv','neverbounce_input_NBout.csv','neverbounce_input_result.csv','preNB.csv','SF_Ready.csv']


#driver.get("https://www.bellescamp.com/SearchUploads.aspx")
#bl_login(username, password)
#bl_results('BL Final Test 91098551')
