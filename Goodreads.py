# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 17:05:19 2016

@author: dkenefick
"""
from __future__ import division

#for goodreads
from rauth.service import OAuth1Service, OAuth1Session
import xmltodict
import json
from time import sleep

import pandas as pd
import numpy as np
import os

import Creds

##########################
### GOODREADS ANALYSIS ###
##########################

class goodreads_session():
    
    sleep_time = .5    
    
    def __init__(self, client_key, client_secret, oauth_access_token, oauth_access_token_secret):

        #if we have all Creds, establish an authorized session
        if (oauth_access_token is not None) & (oauth_access_token_secret is not None):
            #establish the authenticated connection
            self.session = OAuth1Session(
                consumer_key = client_key,
                consumer_secret = client_secret,
                access_token = oauth_access_token,
                access_token_secret = oauth_access_token_secret,
                )
                
            # save access Creds
            self.access_token = oauth_access_token
            self.access_token_secret = oauth_access_token_secret
            
            #record that the session is authenticated
            self.auth = True
        
        #otherwise, establish a non-authorized session
        else:
            #establish non-authenticated connection
            self.session = OAuth1Service(
                consumer_key=client_key,
                consumer_secret=client_secret,
                name='goodreads',
                request_token_url='http://www.goodreads.com/oauth/request_token',
                authorize_url='http://www.goodreads.com/oauth/authorize',
                access_token_url='http://www.goodreads.com/oauth/access_token',
                base_url='http://www.goodreads.com/'
            )
            
            #Set the authentication Flag
            self.auth = False
        
        #save Goodreads Creds
        self.consumer_key = client_key
        self.consumer_secret = client_secret
    
    def __str__(self):
        if self.session:
                print(str(self.session))
        else:
            print("Null Session")
        
    def get_auth_id(self):
        #first, check if the current session is authorized
        if self.auth:
            #contact goodreads, get their response
            response = self.session.get('http://www.goodreads.com/api/auth_user.xml')
            sleep(self.sleep_time)
            #if the response is bad, raise an exception
            if response.status_code != 200:
                raise Exception("Bad response code: "+str(response.status_code))
            
            #if the response is good, parse the reponse, return the ID 
            else:
                data_dict = xmltodict.parse(response.content)
                return data_dict['GoodreadsResponse']['user']['@id']
        
        #if not authorized, raise exception
        else:
            raise Exception("Error: no Auth session")
        
    #possible extention - expand to handle multiple books
    def get_book_id_by_isbn(self,isbn):
        #contact goodreads, get their response
        response = self.session.get("https://www.goodreads.com/book/isbn_to_id/"+isbn+"?key="+self.consumer_key)
        sleep(self.sleep_time)
        #if the response is bad, raise an exception
        if response.status_code != 200:
            raise Exception("Bad response code: "+str(response.status_code))
        
        #if the response is good, parse the reponse, return the ID 
        else:
            return response.content
    
    def add_book_to_shelf(self, book_id, shelf, isbn=False):
        #if passed ISBN, get the id with above function
        if isbn:
            return self.add_book_to_shelf(self.get_book_id_by_isbn(book_id), shelf, False)
        else:
            data = {'name': shelf, 'book_id': book_id}
            response = self.session.post('http://www.goodreads.com/shelf/add_to_shelf.xml', data)
            sleep(self.sleep_time)
            if response.status_code != 201:
                raise Exception("Bad response code: "+str(response.status_code))
            else:
                return 0

    def get_book_stats(self, isbn):
        #contact goodreads, get their response
        response = self.session.get("https://www.goodreads.com/book/review_counts.json?isbns="+isbn+"&key="+self.consumer_key)
        sleep(self.sleep_time)
        #if the response is bad, raise an exception
        if response.status_code != 200:
            raise Exception("Bad response code: "+ str(response.status_code))
        
        #if the response is good, parse the reponse, return the dictionary
        else:
            return json.loads(response.content)

    def get_average_score(self,isbn):
        return self.get_book_stats(isbn)['books'][0]['average_rating']


##################
#### Analysis ####
##################

# path
data_path = os.path.normpath(Creds.root_path + r"\In\for_goodreads.csv")
out_path = os.path.normpath(Creds.root_path + r"\Out\goodreads_out.xlsx")


# import
data = pd.read_csv(data_path)
rows = len(data)

data['gr_avg_rating']= np.nan

#establish connection after all of that hullabaloo
gr = goodreads_session(
    client_key = Creds.GOODREADS_KEY,
    client_secret = Creds.GOODREADS_SECRET,
    oauth_access_token = Creds.GOODREADS_MY_ACCESS_TOKEN,
    oauth_access_token_secret = Creds.GOODREADS_MY_ACCESS_SECRET,
)

for i in range(rows):
    #gr.add_book_to_shelf(data.am_isbn[i] , 'read',isbn=True)
    data.gr_avg_rating[i] = gr.get_average_score(data.am_isbn[i])


data["short"]=data["short"].str.decode("ascii","ignore").str.encode("ascii","ignore")
data["desc"]=data["desc"].str.decode("ascii","ignore").str.encode("ascii","ignore")
data.to_excel(out_path,index=False)   

"""
# testing variables
isbn = "0809052172"
rating = 3
formatted_date = '2015-06-16'
user_id = '20201225'
#get my ID
id = gr.get_auth_id()

#add a book tothe shelf
#result = gr.add_book_to_shelf("0307278247","read",isbn=True)

#stats =gr.get_book_stats(isbn)
avg_score = gr.get_average_score(isbn)
"""



"""
# add review 
data = {'book_id':id, r'review[review]':r"it was good"}
response = session.post('https://www.goodreads.com/review.xml', data)
print(response.status_code)


# get a review id
# will have to add xml parsing, hard coded fopr now
response = session.get("https://www.goodreads.com/review/show_by_user_and_book.xml?book_id="+id+"&key="+GOODREADS_KEY+"&user_id="+user_id)

review_id = "1560626048"

#edit a review
data = {'id':review_id, 'review[review]':"it was good"}
response = session.put('https://www.goodreads.com/review/'+"1560626048"+'.xml', data)
print(response.status_code)
"""


