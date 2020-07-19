#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True
data = pd.read_excel('scraped_city_emails.xlsx')
x = 25
for index, row in data.iterrows():
    if(row['Checked'] == 'Done'):
        continue
    state = row['State']
    if (state == 'Oregon' and x > 0):
        city = row['City']
        driver = webdriver.Chrome('/Users/lumingwang/Documents/internship/chromedriver', options=options)
        driver.get('https://google.com/search?q=' + state + '+state+' + city + '+city+website')
        results = driver.find_elements_by_xpath('//div[@class="r"]/a/h3')
        results[0].click()
        time.sleep(10)
        data.loc[index, 'Checked'] = 'Done'
        url = driver.current_url
        data.loc[index, 'Website'] = url
        data.to_excel('scraped_city_emails.xlsx', encoding='utf-8', index=False)
        x -= 1
        print(url)
        driver.quit()