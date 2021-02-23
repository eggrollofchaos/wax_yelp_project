import requests
import json
import csv
import os
import matplotlib.pyplot as plt
import math
import time

from keys import client_id, api_key

def get_biz_data(biz_url, url_params, biz_filepath, max_results = 50, new_file = 'n'):
    '''Given an API endpoint, set of parameters, CSV filepath, and a max # of results
    (optional, must be a multiple of 50), iteratively GET business data in chunks of 50,
    and write to CSV file.
    '''
    # create a variable  to keep track of which result you are in. 
    cur = 0
    # max is 1000 businesses, total
    print('Gathering business info:')
    # delete data.csv if it exists
    if new_file == 'y' and os.path.exists(biz_filepath):
        os.remove(biz_filepath)
        print('Deleted existing biz_data.csv file.')

    #set up a while loop to go through and grab the result 
    while cur < max_results:
    # while cur < num and cur < 1000:
        #set the offset parameter to be where you currently are in the results 
        url_params['offset'] = cur
        #make your API call with the new offset number
        biz_results = yelp_call(biz_url, url_params, offset = cur)
        #after you get your results you can now use your function to parse those results
        parsed_biz_results_ld = parse_biz_results_ld(biz_results['businesses'])
        if cur == 0: # first iteration
#             data_fields = csv_create(csv_filepath, parsed_bizresults_ld)
            data_fields = parsed_biz_results_ld[0].keys()
            if new_file == 'y':
                data_fields = csv_create(biz_filepath, data_fields)
                print('Created new biz_data.csv file and added headers:')
            else:
                print('Appending to biz_data.csv file with headers:')
            print(list(data_fields))
            print('Downloading data -', end =" ")
        # use your function to write your parsed results to CSV
        csv_append(biz_filepath, parsed_biz_results_ld)
        print('-', end =" ")
        #increment the counter by 50 to move on to the next results
        cur += 50
    
    print('Done.')
    print(f'Successfully gathered listings for maximum of {max_results} businesses of type \'{url_params["categories"]}\', search term \'{url_params["term"]}\', in \'{url_params["location"]}\'.')
    
def get_rev_data(biz_filepath, rev_url, rev_filepath):
    '''Given an API endpoint, Business Data filepath, and target CSV filepath,
    import Business data, extract Business IDs,
    iteratively GET review data for each Business (up to 3 reviews each),
    and write to CSV file.
    '''
    biz_imported_data = import_csv(biz_filepath)
    biz_ids = [biz['id'] for biz in biz_imported_data]
    
    print('Gathering reviews:')
    # check to see if file exists and delete if found
    if os.path.exists(rev_filepath):
        os.remove(rev_filepath)
        print('Deleted existing rev_data.csv file.')
        # set headers for CSV file, including business ID as a key for merging
        data_fields = csv_create(rev_filepath, ['id', 'business_id', 'text', 'rating'])
        print('Created new rev_data.csv file and added headers:')
    else:
        print('Appending to rev_data.csv file with headers:')
    print(list(data_fields))
    print('Downloading data -', end =" ")

    # create empty list, get reviews for each Business ID, and extend list
    count = 0
    for biz_id in biz_ids:
        has_error = False
        rev_results = get_review(rev_url, biz_id)
        # if we reach the end, will get an error
        if 'error' in rev_results.keys():
            has_error = True
            print('Encountered error:')
            print(rev_results['error']['code'])
            print(rev_results['error']['description'])
            break
        parsed_rev_results_ld = parse_rev_results_ld(rev_results['reviews'], biz_id)
        # use your function to write your parsed results to CSV
        csv_append(rev_filepath, parsed_rev_results_ld)
        count += 1
        print('-', end =" ")
        time.sleep(0.1)
    if has_error == True:
        print()
        print('Terminated early.')
    else:
        print('Done.')
    if count > 0:
        print(f'Successfully gathered up to 3 reviews each for {count} businesses.')
    
def yelp_call(url, url_params = {}, offset = 0):
    '''Given a Yelp endpoint URL, URL parameters (optional), and offset (optional),
    perform response.GET with url, headers (including API private key), and parameters.
    Returns a JSON data file.
    '''
    url_params['offset'] = offset
    headers = {
        'Authorization': 'Bearer {}'.format(api_key),
    }
    response = requests.get(url, headers=headers, params=url_params)
    # for debugging
    # print(response)
    data = response.json()
    return data

def parse_biz_results_ld(biz_results):
    ''' Given a list of dicts for business results from GET response,
    create a parsed list of dicts.
    '''
    # your code to parse the result to make them easier to insert into the DB
    # might not need phone, URL
    # create a container to hold our parsed data
    parsed_biz_results = []
    # loop through our business and 
    for biz in biz_results:
    # parse each individual business into a dict
        if 'price' not in biz.keys(): # some business don't have this data, set to blank
            biz['price'] = ''
        biz_dict = {'id' : biz['id'],
                    'name' : biz['name'],
                    'is_closed': biz['is_closed'],
                    # 'is_claimed' : biz['is_claimed'], # only available in Business Details Endpoint
                    'review_count': biz['review_count'],
                    'zip_code' : biz['location']['zip_code'],
                    'rating' : biz['rating'],
                    'price' : biz['price']
                   }
    # add each individual business dict to our data container
        parsed_biz_results.append(biz_dict)
    # return the container with all of the parsed results
    return parsed_biz_results

def parse_rev_results_ld(results, biz_id):
    ''' Given a list of dicts for business review results from GET response,
    create a parsed list of dicts.
    '''
    parsed_rev_results = []
    # loop through our business and 
    for rev in results:
    # parse each individual business into a dict
        rev_dict = {'id' : rev['id'],
                    'business_id' : biz_id,
                    'text' : rev['text'],
                    'rating' : rev['rating'],
                    'time_created' : rev['time_created']
                   }
    # add each individual business dict to our data container
        parsed_rev_results.append(rev_dict)
    # return the container with all of the parsed results
    return parsed_rev_results

def csv_create(csv_filepath, data_fields):
    '''Given a target filepath and a list of fields,
    create a new CSV file and set Headers
    '''
    with open(csv_filepath, 'w', newline = '') as csvfile:
#         data_fields = parsed_results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames = data_fields)
        writer.writeheader()
    return data_fields

def csv_append(csv_filepath, parsed_results):
    ''' Given a target filepath and list of parsed results as a list of dicts,
    append to CSV file (without Headers)
    '''
    # your code to open the csv file, concat the current data, and save the data.
    with open(csv_filepath, 'a', newline = '') as csvfile:
#         data_fields = ['id', 'name', 'is_closed', 'review_count', 'zip_code, 'rating', 'price]
        data_fields = parsed_results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames = data_fields)
        writer.writerows(parsed_results)

def get_review(rev_url, biz_id):
    ''' Given a Yelp Business ID, get reviews for that Business
    '''
    rev_url_id = rev_url.format(id = biz_id) # format the business endpoint per Yelp API spec
    return yelp_call(rev_url_id)

def import_csv(csv_filepath):
    '''Given a CSV filepath, import via DictReader
    '''
    imported_data = []
    with open(csv_filepath, 'r', newline = '') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            imported_data.append(row)
    return imported_data