# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 09:00:34 2016

@author: dkenefick
"""
from __future__ import division
from amazon.api import AmazonAPI
import pandas as pd
import os
from time import sleep

# personal libraries
import Creds
from Goodreads import goodreads_session

# path
data_path = os.path.normpath(Creds.root_path + r"\SQ.xlsx")
out_path = os.path.normpath(Creds.root_path + r"\Python\Out\Books.xlsx")


################
### Analysis ###
################

# import - since used file should have all of the columns filled
data = pd.read_excel(data_path, sheetname = "Books", header = 0)
rows = len(data)

#placeholders for connections 
amazon_connection = None
gr = None

# loop through data.  if unprocessed, call the requisite 
for i in range(1,rows):
    # Amazon - get data if havent already
    if data['amazon processed'][i] != 1:
        
        # if we havent established the connection, do so.  
        if amazon_connection is None:
            amazon_connection = AmazonAPI(Creds.AMAZON_ACCESS_KEY, Creds.AMAZON_SECRET_KEY, Creds.AMAZON_ASSOC_TAG)
        
        #collect the data    
        # if we have the isbn, use it
        if pd.notnull(data['am_isbn'][i]):
            product = amazon_connection.lookup(ItemId=data['am_isbn'][i])
        
        else:       
            #otherwise, lookup title and author, and choose first choice
            try:
                #get the top search result by title
                product = amazon_connection.search_n(1,Keywords=data.am_title[i]+" "+data.am_author[i], SearchIndex='All')[0]
            except:
                print("No good matches found for:  "+int(data.title[i])+" \n Check spelling")
                next           
    
        # pull the data elements from the product object
        data.am_title[i]=product.title.encode("ascii","ignore")
        data.pages[i] = product.get_attribute("NumberOfPages")
        data.am_author[i] = product.get_attribute("Author").encode("ascii","ignore")
        data.list_price[i] = product.price_and_currency[0]
        data['amazon page'][i] = product.offer_url.replace("/?tag="+Creds.AMAZON_ASSOC_TAG,"")
        data.am_isbn[i] = product.isbn
        
        # some products do not have these - check
        if product._safe_get_element_text('OfferSummary.LowestUsedPrice.Amount') is not None:
            data.min_price[i] = min((int(product._safe_get_element_text('OfferSummary.LowestUsedPrice.Amount')) +399)/100 ,data.list_price[i])
        else:
            data.min_price[i] = data.list_price[i]            
        if product.editorial_reviews:
            data.desc[i] = product.editorial_reviews[0].encode("ascii","ignore")            

        if i != (rows-1):
            # clear the product for the next round
            product = None
            # rest, so as not to tire the amazon webpage out. 
            sleep(.5)                
            
        #update the data
        data['amazon processed'][i] = 1            
            
    # Goodreads, set data   
    if (data['goodreads processed'][i] != 1) & (data['amazon processed'][i] == 1):
        # if we havent established the connection, do so.  
        if gr is None:
            gr = goodreads_session(
                    client_key = Creds.GOODREADS_KEY,
                    client_secret = Creds.GOODREADS_SECRET,
                    oauth_access_token = Creds.GOODREADS_MY_ACCESS_TOKEN,
                    oauth_access_token_secret = Creds.GOODREADS_MY_ACCESS_SECRET,
                )
        # fill in data        
        data.gr_avg_rating[i] = gr.get_average_score(data.am_isbn[i])
        result = gr.add_book_to_shelf(data.am_isbn[i],"read",isbn=True)
        data['goodreads processed'][i] = 1    
            
            
### Save data            
            
data.to_excel(out_path,sheet_name="Books", index=False)            
            
            
            
            
            
            
            
            
            
            