# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 13:27:54 2018

@author: kerrydriscoll
"""

"""
TO DO:
* Write mouse-over on ticket price scrub to reveal all years' prices
* See if I can use BeautifulSoup on Rotten Tomatoes (faster than Selenium)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import ExcelWriter
from openpyxl import load_workbook
import re
from time import time, sleep
import datetime
import random
from requests import get
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import mpld3
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
from sklearn.cluster import DBSCAN


"""
Measure Runtime to Evaluate Code Performance
"""
start_time = time()

"""
Open Web Browser
"""
option = webdriver.ChromeOptions()
option.add_argument(" — incognito")
browser = webdriver.Chrome(executable_path='/Users/kerrydriscoll/Downloads/chromedriver', chrome_options=option)

"""
Create DataFrame to Populate
"""
df_final = pd.DataFrame(columns=['Title', 'Year', 'Rotten Tomatoes Score', 'Unadjusted Domestic Box Office Gross', 'Adjusted Domestic Box Office Gross', 'Time Stamp'])

"""
Input MOVIE IDs to reach URL
"""

#All A24 Titles
IDs=pd.read_excel('/Users/kerrydriscoll/Desktop/resumes/A24/A24 IDs.xlsx')
#IDs=IDs[IDs['Rotten Tomatoes'].notnull()]


try_again = []

"""
Get Avg Ticket Price by Year
Purpose: tp Adjusting Box Office Performance
"""
browser.get('http://www.natoonline.org/data/ticket-price/')

# Wait 20 seconds for page to load
timeout = 20
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//table[@id='tablepress-6']")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()
        
        
table_element = browser.find_elements_by_xpath("//table[@id='tablepress-6']")
table_element = table_element[0].text
table = table_element.split('\n')
for i in range(len(table)):
    table[i]=table[i].split(' ')
Adjustment = pd.DataFrame(columns=table[0], data=table[1:])
Adjustment.set_index('Year', inplace=True)

#print(Adjustment)

"""
Extract Data for each MOVIE
"""
for i in IDs.index:
    
    """
    Extract Critic Score
    """
    browser.get("https://www.rottentomatoes.com/m/{}".format(IDs['Rotten Tomatoes'][i]))
    sleep(random.uniform(0.3, 0.8))

# Wait 20 seconds for page to load
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='meter-value superPageFontColor']")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        continue
        

    score_element = browser.find_elements_by_xpath("//span[@class='meter-value superPageFontColor']")
    score_element = [x for x in score_element if x.text != '']    
    score = [x.text for x in score_element][0]
    
    #print(score)
    
    url = "https://www.the-numbers.com/movie/{}".format(IDs['The Numbers'][i])
    #print(url)

    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    type(html_soup)
    
    """
    Extract Year
    """

    year_soup = html_soup.find_all(['meta content', 'title'])
    year = re.search('\(.+\s*\d+\s*\)', str(year_soup[0])).group(0)
    year = year.replace("(","")
    year = year.replace(")","")
    
    """
    Extract Unadjusted Box Office
    """
    box_office_soup = html_soup.find("b", text="Domestic Box Office").parent.parent
    box_office_soup = html_soup.find("td", class_="data")
    box_office = re.search('>(.*?)\<',str(box_office_soup)).group(0)
    box_office = box_office.replace(">","")
    box_office = box_office.replace("<","")
   
    """
    Adjust Box Office
    (to 2015 dollars)
    """
    release_ticket_value=Adjustment.loc[year].item()
    release_ticket_value=float(release_ticket_value.replace( '$',''))
    release_box_office=float(box_office.replace( '$','').replace(',', ''))
    num_tix = release_box_office / release_ticket_value
    ticket_value_2015=Adjustment.loc['2015'].item()
    ticket_value_2015=float(ticket_value_2015.replace( '$',''))
    
    adjusted_box_office=ticket_value_2015*num_tix
    adjusted_box_office='${:,.2f}'.format(adjusted_box_office)


    
    """
    Combine with other Titles
    """
    df = pd.DataFrame({'Title': IDs['Title'][i], 'Year': [year], 'Rotten Tomatoes Score': [score],'Unadjusted Domestic Box Office Gross': [box_office], 'Adjusted Domestic Box Office Gross': [adjusted_box_office], 'Time Stamp':datetime.datetime.now().strftime("%H:%M:%S")})
    df = df[['Title', 'Year', 'Rotten Tomatoes Score', 'Unadjusted Domestic Box Office Gross','Adjusted Domestic Box Office Gross', 'Time Stamp']]

    df_final = df_final.append(df, ignore_index=True)
    df_final = df_final[['Title', 'Year', 'Rotten Tomatoes Score', 'Unadjusted Domestic Box Office Gross','Adjusted Domestic Box Office Gross','Time Stamp']]

browser.quit() 

path = '/Users/kerrydriscoll/Desktop/resumes/A24/types_of_A24.xlsx'
writer = ExcelWriter(path, engine = 'openpyxl')
df_final.to_excel(writer)
writer.save()


run_time=time() - start_time
print("--- {} seconds ---".format(run_time))