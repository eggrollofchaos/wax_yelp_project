import requests
import json
import csv
import os
import matplotlib.pyplot as plt
import math

from keys import client_id, api_key

biz_url =  'https://api.yelp.com/v3/businesses/search'
rev_url = 'https://api.yelp.com/v3/businesses/{id}/reviews'

def fetch_biz_data(term, location, categories, csv_filepath, max_results = 50):
    url_params = {
        "term": term.replace(' ', '+'),
        "location": location.replace(' ', '+'),
        "categories" : categories,
        "limit": 50
    }

    # create a variable  to keep track of which result you are in. 
    cur = 0
    # max is 1000 businesses, total

    # delete data.csv if it exists
    if os.path.exists(csv_filepath):
        os.remove(csv_filepath)
        print('Deleted existing data.csv file.')

    #set up a while loop to go through and grab the result 
    while cur < max_results:
    # while cur < num and cur < 1000:
        #set the offset parameter to be where you currently are in the results 
        url_params['offset'] = cur
        #make your API call with the new offset number
        results = yelp_call(biz_url, url_params)
        #after you get your results you can now use your function to parse those results
        parsed_results_ld = parse_biz_results_ld(results['businesses'])
        if cur == 0:
            data_fields = csv_create(csv_filepath, parsed_results_ld)
            print('Created new biz_data.csv file and added headers:')
            print(list(data_fields))
            print('Downloading data -', end =" ")
        # use your function to insert your parsed results into the db
        csv_append(csv_filepath, parsed_results_ld)
        print('-', end =" ")
        #increment the counter by 50 to move on to the next results
        cur += 50
    
    print('Done.')
    print(f'Successfully gathered listings for maximum of {max_results} businesses of type \'{categories}\', search term \'{term}\', in \'{location}\'.')

def yelp_call(url, url_params = {}):
    # your code to make the yelp call
    # will be 50 businessesdef yelp_call ():
    headers = {
        'Authorization': 'Bearer {}'.format(api_key),
    }
    response = requests.get(url, headers=headers, params=url_params)
    data = response.json()
    return data

def parse_results(results):
    ''' Given a list of dictionaries, create a list of tuples'''
    # your code to parse the result to make them easier to insert into the DB
    # might not need phone, URL
    # create a container to hold our parsed data
    parsed_results = []
    # loop through our business and 
    for biz in results:
    # parse each individual business into a tuple
        biz_tuple = (biz['name'],biz['location']['zip_code'],biz['rating'])
    # add each individual business tuple to our data container
        parsed_results.append(biz_tuple)
    # return the container with all of the parsed results
    return parsed_results

def parse_biz_results_ld(results):
    ''' Given a list of dict from GET response, create a parsed list of dicts'''
    # your code to parse the result to make them easier to insert into the DB
    # might not need phone, URL
    # create a container to hold our parsed data
    parsed_results = []
    # loop through our business and 
    for biz in results:
    # parse each individual business into a dict
        if 'price' in biz.keys(): # some business don't have this data
            biz_dict = {'id' : biz['id'],
                        'name' : biz['name'],
                        'is_closed': biz['is_closed'],
                        'review_count': biz['review_count'],
                        'zip_code' : biz['location']['zip_code'],
                        'rating' : biz['rating'],
                        'price' : biz['price']
                       }
    # add each individual business dict to our data container
        parsed_results.append(biz_dict)
    # return the container with all of the parsed results
    return parsed_results

def csv_create(csv_filepath, parsed_results):
    with open(csv_filepath, 'w', newline = '') as csvfile:
        data_fields = parsed_results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames = data_fields)
        writer.writeheader()
    return data_fields

def csv_append(csv_filepath, parsed_results):
    ''' Given a target filepath and list of parsed results, write to CSV file'''
    # your code to open the csv file, concat the current data, and save the data.
    with open(csv_filepath, 'a', newline = '') as csvfile:
#         data_fields = ['Business Name', 'Location', 'Zip Code', 'Rating']
        data_fields = parsed_results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames = data_fields)
#         writer.writeheader()
        writer.writerows(parsed_results)
#         writer = csv.writer(csvfile, fieldnames = data_fields)
#         writer.writeheader()
#         writer.writerows(parsed_results)

def get_review(biz_id):
    rev_url_id = rev_url.format(id = biz_id)
    return yelp_call(rev_url_id)

def parse_rev_results_ld(results):
    parsed_results = []
    # loop through our business and 
    for rev in results:
    # parse each individual business into a dict
        rev_dict = {'id' : rev['id'],
                    'text' : rev['text'],
                    'rating' : rev['rating']
                   }
    # add each individual business dict to our data container
        parsed_results.append(rev_dict)
    # return the container with all of the parsed results
    return parsed_results