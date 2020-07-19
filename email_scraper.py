#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Albert Wang's Code

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer

# IF DIRECTORY DOES NOT EXIST, SCRAPE HOME WEBSITE for example city of cashmere
data = pd.read_excel('scraped_city_emails.xlsx')
startTime = datetime.now()
lastTime = startTime
i = 0
for index, row in data.iterrows():
    if (i >= 10):
        break
    if(row['Checked'] == 'Done'):
        continue
    
    state = row['State']
    
    if(state == 'Washington'):
        city = row['City']
        original = str(row['Website'])[:-1]
        print('City Site: ' + original)
        driver = webdriver.Chrome('/Users/lumingwang/Documents/internship/chromedriver', options=options)
        driver.get('https://google.com/search?q=' + state + '+state+' + city + '+city+website+directory')
        results = driver.find_elements_by_xpath('//div[@class="r"]/a/h3')
        results[0].click() #selenium to find website
        time.sleep(3)
        url = driver.current_url
        print('Site: ' + url)
        data.loc[index, 'Directory Link'] = url
        print('CRAWLING SITE...')
        
        soup = BeautifulSoup(driver.page_source, 'lxml', parse_only=SoupStrainer('a', href=True))
        first_level_hrefs = set()
        email_set = set()
        for link in soup.find_all('a'): #collect front page emails & hyperlinks
            link_str = str(link.get('href'))
            if ('directory' not in link_str and 'Directory' not in link_str):
                continue
            first_level_hrefs.add(link_str)
            if('@' in link_str and 'google.com' not in link_str):
                if ('mailto:' in link_str):
                    link_str = link_str[7:]
                if ('?subject=' in link_str):
                    link_str = link_str[:link_str.find('?subject=')]
                email_set.add(link_str)
        print('Front Page Complete')
            
        for href in first_level_hrefs: #collect first level emails & hyperlinks
            try:
                driver.get(href)
            except:
                href = original + href
                try:
                    driver.get(href)
                except:
                    continue
            soup = BeautifulSoup(driver.page_source, 'lxml', parse_only=SoupStrainer('a', href=True))
            for link in soup.findAll('a'):
                link_str = str(link.get('href'))
                if('@' in link_str and 'google.com' not in link_str):
                    if ('mailto:' in link_str):
                        link_str = link_str[7:]
                    if ('?subject=' in link_str):
                        link_str = link_str[:link_str.find('?subject=')]
                    email_set.add(link_str)
        driver.quit()
        print('First Level Complete')
        
        print('Links: ' + str(len(first_level_hrefs)))
        print('Email List: ' + str(email_set))
        print('# of Emails: ' + str(len(email_set)))
        data.loc[index, 'Mayor Email'] = str(list(email_set))
        data.loc[index, 'Checked'] = 'Done'
        i += 1
        print('Time: ' + str(datetime.now() - lastTime))
        print('Total Completed: ' + str(i) + '\n')
        lastTime = datetime.now()
        data.to_excel('scraped_city_emails.xlsx', encoding='utf-8', index=False)

print('Total Time: ' + str(datetime.now() - startTime))