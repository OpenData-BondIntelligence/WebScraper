#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Albert Wang's Code

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True #see headless browser
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer

# USE SET FOR ALL HYPERLINKS TO AVOID DUPLICATES TO MAKE SCRAPING FASTER
data = pd.read_excel('scraped_city_emails.xlsx')
startTime = datetime.now()
lastTime = startTime
i = 0
driver = webdriver.Chrome('/Users/lumingwang/Documents/OpenData/chromedriver', options=options)
for index, row in data.iterrows():
    if (i >= 1):
        break
    if(row['Checked'] == 'Done'):
        continue
    
    state = row['State']
    
    if(state == 'Washington'):
        directory_found = True
        city = row['City']
        driver.get('https://google.com/search?q=' + state + '+state+' + city + '+city+website+directory')
        original = str(row['Website'])[:-1]
        print('Original: ' + original)
        results = driver.find_elements_by_xpath('//div[@class="r"]/a/h3')
        results[0].click() #selenium to find website
        time.sleep(3)
        url = driver.current_url
        if ('http' not in url):
            url = original[:original.find(':')] + '://' + url
        print('Website found: ' + url)
        # URL does not have HTTP/HTTPS so directory not in url does not work
        if ('directory' not in url and 'Directory' not in url or original not in url):
            print('No Directory Found')
            url = original
            driver.get(url)
            directory_found = False
        print('Searching Site: ' + url)
        data.loc[index, 'Directory Link'] = url
        print('CRAWLING SITE...')
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'lxml', parse_only=SoupStrainer('a', href=True))
        first_level_hrefs = set()
        email_set = set()
        
        if (directory_found): #city has directory
            for link in soup.find_all('a'): #collect front page emails & hyperlinks
                link_str = str(link.get('href'))
                if ('directory' not in link_str and 'Directory' not in link_str):
                    continue
                if('@' in link_str and 'google.com' not in link_str):
                    if ('mailto:' in link_str):
                        link_str = link_str[7:]
                    if ('?subject=' in link_str):
                        link_str = link_str[:link_str.find('?subject=')]
                    email_set.add(link_str)
                else:
                    first_level_hrefs.add(link_str)
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
                    if (link_str in first_level_hrefs):
                        continue
                    if('@' in link_str and 'google.com' not in link_str):
                        if ('mailto:' in link_str):
                            link_str = link_str[7:]
                        if ('?subject=' in link_str):
                            link_str = link_str[:link_str.find('?subject=')]
                        email_set.add(link_str)
            print('First Level Complete')
            
        else: #city does not have directory -- start from home page
            second_level_hrefs = set()
            for link in soup.find_all('a'): #collect front page emails & hyperlinks
                link_str = str(link.get('href'))
                if ('/' not in link_str):
                    continue
                if ('http' in link_str and original not in link_str):
                    continue
                if('@' in link_str and 'google.com' not in link_str):
                    if ('mailto:' in link_str):
                        link_str = link_str[7:]
                    if ('?subject=' in link_str):
                        link_str = link_str[:link_str.find('?subject=')]
                    email_set.add(link_str)
                else:
                    first_level_hrefs.add(link_str)
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
                    if (link_str in first_level_hrefs):
                        continue
                    if ('/' not in link_str):
                        continue
                    if ('http' in link_str and original not in link_str):
                        continue
                    if('@' in link_str and 'google.com' not in link_str):
                        if ('mailto:' in link_str):
                            link_str = link_str[7:]
                        if ('?subject=' in link_str):
                            link_str = link_str[:link_str.find('?subject=')]
                        email_set.add(link_str)
                    else:
                        second_level_hrefs.add(link_str)
            print('First Level Complete')
            
            for href in second_level_hrefs: #collect second level emails
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
                    if (link_str in second_level_hrefs):
                        continue
                    if ('/' not in link_str):
                        continue
                    if ('http' in link_str and original not in link_str):
                        continue
                    if('@' in link_str and 'google.com' not in link_str):
                        if ('mailto:' in link_str):
                            link_str = link_str[7:]
                        if ('?subject=' in link_str):
                            link_str = link_str[:link_str.find('?subject=')]
                        email_set.add(link_str)
            print('Second Level Complete')
            
        print('Links: ' + str(len(first_level_hrefs)))
        print('Email List: ' + str(email_set))
        print('# of Emails: ' + str(len(email_set)))
        data.loc[index, 'Mayor Email'] = str(list(email_set))
        data.loc[index, 'Checked'] = 'Done'
        data.to_excel('scraped_city_emails.xlsx', index=False)
        i += 1
        print('Time: ' + str(datetime.now() - lastTime))
        print('Total Completed: ' + str(i) + '\n')
        lastTime = datetime.now()

driver.quit()
print('Total Time: ' + str(datetime.now() - startTime))