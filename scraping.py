#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Albert Wang's Code

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True
import pandas as pd
from googleapiclient.discovery import build
from bs4 import BeautifulSoup, SoupStrainer
from API_KEY import api_key, cse_id
from datetime import datetime

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey = api_key)
    res = service.cse().list(q = search_term, cx = cse_id, **kwargs).execute()
    return res

data = pd.read_excel('web_scraping.xlsx')
startTime = datetime.now()
i = 0
for index, row in data.iterrows():
    if (i >= 1):
        break
    state = row['State']
    city = row['City']
    checked = row['Checked']

    if(checked == "Done"):
        continue
    
    if(state == "Washington" and city == "Bainbridge Island"): #auburn
        print("FINDING SITE...")
        original = google_search(state + " state " + city + " city website", api_key, cse_id)
        original_url = (original['items'][0]['formattedUrl'])[:-1]      
        print("Original Site: " + original_url)
        result = google_search(state + " state " + city + " city website directory", api_key, cse_id)
        url = result['items'][0]['formattedUrl'] #go directly to directory part of website
        x = 1
        while (original_url not in url): #guarantees correct website b/c CSE is stupid
            url = result['items'][x]['formattedUrl']
            x += 1
        if("http://" not in url and "https://" not in url):
            url = "http://" + url
        print("Site: " + url)
        data.loc[index, "Website"] = url
        print("CRAWLING SITE...")
        
        driver = webdriver.Chrome("/Users/lumingwang/Documents/internship/chromedriver", options=options)
        try: #selenium to run JS on site
            driver.get(url)
        except:
            data.loc[index, "Checked"] = "Done"
            i += 1
            continue
        
        soup = BeautifulSoup(driver.page_source, 'lxml', parse_only=SoupStrainer('a', href=True))
        first_level_hrefs = set()
        second_level_hrefs = set()
        email_set = set()
        for link in soup.find_all('a'): #collect front page emails & hyperlinks
            link_str = str(link.get('href'))
            if (original_url not in link_str and ("http:" in link_str or "https:" in link_str) or "/" not in link_str):
                continue
            first_level_hrefs.add(link_str)
            if("@" in link_str and "google.com" not in link_str):
                if ("mailto:" in link_str):
                    link_str = link_str[7:]
                if ("?subject=" in link_str):
                    link_str = link_str[:link_str.find("?subject=")]
                email_set.add(link_str)
        print("Front Page Complete")
        
        for href in first_level_hrefs: #collect first level emails & hyperlinks
            try:
                driver.get(href)
            except:
                href = original_url + href
                try:
                    driver.get(href)
                except:
                    continue
            soup = BeautifulSoup(driver.page_source, 'lxml', parse_only=SoupStrainer('a', href=True))
            for link in soup.findAll('a'):
                link_str = str(link.get('href'))
                second_level_hrefs.add(link_str)
                if("@" in link_str and "google.com" not in link_str):
                    if ("mailto:" in link_str):
                        link_str = link_str[7:]
                    if ("?subject=" in link_str):
                        link_str = link_str[:link_str.find("?subject=")]
                    email_set.add(link_str)  
        print("First Level Complete")
        
#        for href in second_level_hrefs: #collect second level emails & hyperlinks
#            try:
#                driver.get(href)
#            except:
#                href = original_url + href
#                try:
#                    driver.get(href)
#                except:
#                    continue
#            soup = BeautifulSoup(driver.page_source, 'lxml', parse_only=SoupStrainer('a', href=True))
#            for link in soup.findAll('a'):
#                link_str = str(link.get('href'))
#                if("@" in link_str):
#                    if ("mailto:" in link_str):
#                        email_set.add(link_str[7:])
#                    else:
#                        email_set.add(link_str)                
#        print("Second Level Complete")
        
        print(len(first_level_hrefs))
        print(len(second_level_hrefs))
        print("Email List: " + str(email_set))
        print("# of Emails: " + str(len(email_set)))
        data.loc[index, "Mayor Email"] = str(list(email_set))
        data.loc[index, "Checked"] = "Done"
        driver.quit()
        i += 1
        print("Total Completed: " + str(i) + "\n")

print("Time Taken: " + str(datetime.now() - startTime))
data.to_excel("web_scraping.xlsx", encoding='utf-8', index=False)