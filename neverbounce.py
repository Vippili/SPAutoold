import pandas as pd
import scipy.stats as sp
import numpy as np
import neverbounce_sdk
import time

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 1000)


read_filename = 'neverbounce_input'
full_file = pd.read_csv(read_filename + '.csv')
config = pd.read_csv("neverbounce_config.csv")


index_var = list(config['Index Variable'])[0]
emails = full_file[list(map(lambda x: list(config[x])[0],list(config.columns)))]


emails_melt = emails.melt(id_vars = [index_var])
print(len(emails_melt))
emails_melt = emails_melt[~emails_melt['value'].map(pd.isna)]
print(len(emails_melt))



emails_melt['email'] = emails_melt['value']
emails_melt = emails_melt[[
    'email',
    'variable',
    index_var
]]



emails_melt_toNB = emails_melt.to_dict('records')



api_key = 'private_53f797745187b700f98064b8318df8bc'
client = neverbounce_sdk.client(api_key=api_key,timeout=30)



job = client.jobs_create(emails_melt_toNB)

# # all state-changing methods return a status object
resp = client.jobs_parse(job['job_id'], auto_start=False)
assert resp['status'] == 'success'



run_ready = False
while not run_ready:
	time.sleep(20)
	progress = client.jobs_status(job['job_id'])
	if progress['job_status'] == 'waiting':
		run_ready = True

	if progress['job_status'] == 'failed':
		print('JOB FAILED')
		break


client.jobs_start(job['job_id'])



download_ready = False
while not download_ready:
    time.sleep(120)
    progress = client.jobs_status(job['job_id'])
    if progress['job_status'] in ['complete','under_review']:
        download_ready = True

    if progress['job_status'] == 'failed':
    	print('JOB FAILED')
    	break



# Open file to write to
f = open(read_filename + '_result.csv', mode='wb')

# Jobs download
resp = client.jobs_download(job_id=job['job_id'], fd=f)
f.close()




results = pd.read_csv(read_filename + '_result.csv',names = ['email','variable',index_var,'email_status'])



emails_melt_filtered = emails_melt.merge(results[['email','email_status']],on = 'email',how = 'outer')
print(len(emails_melt_filtered))
emails_melt_filtered = emails_melt_filtered[emails_melt_filtered['email_status'] == 'valid'].drop_duplicates([index_var,'email'], keep = 'first')
print(len(emails_melt_filtered))
emails_melt_filtered = emails_melt_filtered.drop_duplicates([index_var,'variable'], keep = 'first')
print(len(emails_melt_filtered))



results_merge = emails_melt_filtered.pivot(values = 'email',columns = 'variable',index = index_var).reset_index()



full_file_ready = full_file.drop(list(map(lambda x: list(config[x])[0],list(config.columns)))[1:],axis = 1)
full_file_out = full_file_ready.merge(results_merge,on = index_var,how = 'left')
full_file_out.to_csv(read_filename + '_NBout.csv')