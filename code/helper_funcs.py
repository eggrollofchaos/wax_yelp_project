import requests
import json
import csv
import matplotlib.pyplot as plt
import math

from  keys  import  client_id, api_key

def yelp_call(url_params, api_key):
    # your code to make the yelp call
    # will be 50 businessesdef yelp_call ():
    url =  'https://api.yelp.com/v3/businesses/search'
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

def parse_results_ld(results):
    ''' Given a list of dict from GET response, create a parsed list of dicts'''
    # your code to parse the result to make them easier to insert into the DB
    # might not need phone, URL
    # create a container to hold our parsed data
    parsed_results = []
    # loop through our business and 
    for biz in results:
    # parse each individual business into a dict
        biz_dict = {'id' : biz['id'],
                    'name' : biz['name'],
                    'is_closed': biz['is_closed'],
                    'review_count': biz['review_count'],
                    'zip_code' : biz['location']['zip_code'],
                    'rating' : biz['rating']}
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