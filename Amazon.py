# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 15:12:55 2016

@author: dkenefick
"""

#############
### Setup ###
#############
# libraries
from __future__ import division
from amazon.api import AmazonAPI
import pandas as pd
import numpy as np
import os
from time import sleep
import Creds

# path
data_path = os.path.normpath(Creds.root_path + r"\In\for_amazon.csv")
out_path = os.path.normpath(Creds.root_path + r"\Out\amazon_out.xlsx")


#######################
### AMAZON ANALYSIS ###
#######################

# import
data = pd.read_csv(data_path)
rows = len(data)

# blank series for title, author, isbn
data['am_title'] = ""
data['am_isbn']=""
data['am_author']=""
data['list_price']= np.nan
data['min_price']=np.nan
data['pages'] = np.nan
data['desc'] = ""

# establish connection
amazon = AmazonAPI(Creds.AMAZON_ACCESS_KEY, Creds.AMAZON_SECRET_KEY, Creds.AMAZON_ASSOC_TAG)

# for each product, get the product, then fill in the details.
for i in range(rows):
    #if the isbn is filled out, we can use that as the item id
    if pd.notnull(data['isbn-10'][i]):
        #find product
        product = amazon.lookup(ItemId=data['isbn-10'][i])
        
    else:
        try:
            #get the top search result by title
            product = amazon.search_n(1,Keywords=data.title[i]+" "+data.author[i], SearchIndex='All')[0]
        except:
            next
            
    #fill in details
    data.am_title[i]=product.title.encode("ascii","ignore")
    data.pages[i] = product.get_attribute("NumberOfPages")
    data.am_author[i] = product.get_attribute("Author").encode("ascii","ignore")
    data.list_price[i] = product.price_and_currency[0]
    if product._safe_get_element_text('OfferSummary.LowestUsedPrice.Amount') is not None:
        data.min_price[i] = min((int(product._safe_get_element_text('OfferSummary.LowestUsedPrice.Amount')) +399)/100 ,data.list_price[i])
    else:
        data.min_price[i] = data.list_price[i]
    if product.editorial_reviews:
        data.desc[i] = product.editorial_reviews[0].encode("ascii","ignore")
    data.am_isbn[i] = product.isbn
    data['amazon page'][i] = product.offer_url.replace("/?tag="+Creds.AMAZON_ASSOC_TAG,"")
    product = None
    sleep(.5)    

# export the data
data["Short Desc."]=data["Short Desc."].str.encode("ascii","ignore")
data.to_excel(out_path,index=False)
