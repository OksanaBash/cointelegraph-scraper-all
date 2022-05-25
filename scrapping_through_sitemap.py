# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 17:13:58 2021

@author: Oksana Bashchenko
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv
import time
import json
from bs4.element import Tag
import numpy as np

#%%
file_to_store_news = 'news_database.csv' # should be in .csv format
with open(file_to_store_news, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['category', 'title', 'date', 'n_views', 'n_shares', 'summary', 'content', 'tags'])

#%%
def get_nice_text(soup): # recognize paragraphs and remove "related" part of the content
    txt = ''
    for par in soup.find_all(lambda tag:tag.name=="p" and not "Related:" in tag.text):
        txt += ' ' + re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',par.get_text())
    return txt.strip()

#%%
def prepare_pandas(df):
    df.index = df.date
    df.drop(columns = 'date', inplace = True)
    df.index = pd.to_datetime(df.index, utc = True)
    df.sort_index(inplace = True)
    return df

#%%
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 91.0.4472.124 Safari/537.36'}
url_base = "https://cointelegraph.com/post-sitemap-"
total_posts = 0

bad_response = []
bad_response_count =0
#%%
# the code requires number of content-aggregating pages from https://cointelegraph.com/sitemap.xml
# as for 20th May 2022, it is 46 non-empty pages.
print('This code requires the number of non-empty content aggregating pages from https://cointelegraph.com/sitemap.xml')
print('As of May 2022 it is 46')
print('Check the max number in url of the type "https://cointelegraph.com/post-sitemap-"')
n_agg_pages_str = input('Input this number:')
n_agg_pages = int(n_agg_pages_str)

#%%
for i in range(1,n_agg_pages+1): # number of content-aggregating pages from https://cointelegraph.com/sitemap.xml
    url = url_base+str(i)
    print('scrapping ', url)
    web_map = requests.get(url, headers = headers)
    soup = BeautifulSoup(web_map.text, features = 'lxml')
    all_links = soup.find_all('loc')

    posts_downloaded = 0

    for item in all_links:
        url_post = item.getText()
        is_news = url_post.split('/')[3]
        
        if is_news != "news":
            print('\n')
            print(is_news, 'not a news item \n')
            continue
        
        page = requests.get(url_post, headers = headers)
        page.encoding = 'utf-8'
        sauce = BeautifulSoup(page.text,"lxml")
        
        try:
            data = json.loads(sauce.find('script', type='application/ld+json').string)
        except:
            print('Something is wrong: status', page.status_code, 'will sleep and retry')
            time.sleep(4)
            try: 
                data = json.loads(sauce.find('script', type='application/ld+json').string)
            except:
                print('Sleeping didnt solve the problem, going to the next post')
                bad_response.append(url_post)
                bad_response_count +=1
                continue
                
            
        art_tag = data['articleSection']    
        date = data['datePublished']
        titleTag = sauce.find("h1",{"class":"post__title"})
        summaryTag = sauce.find("p", {"class":"post__lead"})
        contentTag = sauce.find("div",{"class":"post-content"})
        tagsTag = sauce.find('ul', {"class":"tags-list__list"}) # some articles have tags which could help with classification
        
        title = None
        content = None
        summary = None
        tags_list = None
        
        if isinstance(titleTag,Tag):
            title = titleTag.get_text().strip()
            
        if isinstance(contentTag,Tag):
            content = get_nice_text(contentTag)
    
        if isinstance(summaryTag, Tag):
            summary = summaryTag.get_text().strip() 
            
        if isinstance(tagsTag, Tag):
            tags_str = tagsTag.get_text().strip()
            tags_list_prep = tags_str.split('#')
            tags_list = [i.strip() for i in tags_list_prep if len(i)>0]
            
            
        stats = sauce.find_all('div', {"class" : "post-actions__item post-actions__item_stat"}) 
        views = stats[0]    
        views_list = views.get_text().strip().split(" ")
        count_views = int(views_list[0])
        
        count_shares = 0
        if len(stats)>1:
            shares = stats[1]
            shares_list = shares.get_text().strip().split(" ")
            count_shares = int(shares_list[0])
            
        #if posts_downloaded% 500 == 0:
         #   print('Date:', date, 'title:', title, 'summary:', summary )        
        
        with open(file_to_store_news, 'a', encoding = 'utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([art_tag, title, date, count_views, count_shares, summary, content, tags_list])
            
        posts_downloaded +=1
        
    total_posts += posts_downloaded
    print('loaded ', total_posts, 'posts')
    to_sleep = abs(np.random.normal(2, 3))
    time.sleep(to_sleep)
    
    
#%%
news_map = pd.read_csv(file_to_store_news)
news_map = prepare_pandas(news_map)


