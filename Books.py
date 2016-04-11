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
data_path = os.path.normpath(Creds.root_path + r"\SQ.xlsm")
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
for i in range(0,rows):
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
        
        #get average rating
        data.gr_avg_rating[i] = gr.get_average_score(data.am_isbn[i])
        
        # add to read shelf on GR
        result = gr.add_book_to_shelf(data.am_isbn[i],"read",isbn=True)
        
        #get the review number - make sure an int, then str to account for rating slike 4.5
        rating = str(int(data['goodreads rating'][i]))
        
        #format the date        
        dt = data['complete date'][i]
        yr = str(dt.year)
        day = str(dt.day)
        if len(day) == 1:
            day = '0'+day

        month = str(dt.month)
        if len(month) == 1:
            month = '0'+month    
            
        formatted_date = yr+'-'+month+'-'+day
        
        # get the book ids for the reviews
        book_id = gr.get_book_id_by_isbn(data.am_isbn[i])
        
        #try posting the review
        if gr.post_review(book_id,'',rating,formatted_date):
            #if it does not work, we need to edit the exsisting review
            user_id = gr.get_auth_id()
            rev_id = gr.get_review_id_by_book_and_user(book_id,user_id)
            gr.edit_review(rev_id,'',rating,formatted_date)
        
        #finish processing
        data['goodreads processed'][i] = 1    
            
            
### Save data            
            
data.to_excel(out_path,sheet_name="Books", index=False)            
            
            
            
            
            
            
            
            
            
            