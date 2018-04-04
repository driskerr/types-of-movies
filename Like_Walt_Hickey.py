# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 13:27:54 2018

@author: kerrydriscoll
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
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


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

# Wait 20 seconds for page to load
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='meter-value superPageFontColor']")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
        

    score_element = browser.find_elements_by_xpath("//span[@class='meter-value superPageFontColor']")
    score_element = [x for x in score_element if x.text != '']    
    score = [x.text for x in score_element][0]
    
    #print(score)
    
    browser.get("https://www.the-numbers.com/movie/{}".format(IDs['The Numbers'][i]))

# Wait 20 seconds for page to load
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//td[@class='data']")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
        
    """
    Extract Year
    """

    year_element = browser.find_elements_by_xpath("//h1[@itemprop='name']")
    year_element = [x for x in year_element if x.text != '']    
    year_text = [x.text for x in year_element][0]
    year = re.search('\(.+\s*\d+\s*\)', year_text).group(0)
    year = year.replace("(","")
    year = year.replace(")","")
    
    #print(year)
        
    """
    Extract Unadjusted Box Office
    """

    box_office_element = browser.find_elements_by_xpath("//td[@class='data']")
    box_office_element = [x for x in box_office_element if x.text != '']    
    box_office = [x.text for x in box_office_element][0] 
    
    #print(box_office)
    
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

    
x = df_final['Rotten Tomatoes Score'].apply(lambda x: float(x.replace('%', '')))
y = df_final['Adjusted Domestic Box Office Gross'].apply(lambda x: float(x.replace('$', '').replace(',', '')))

plt.scatter(x, y, s=50, color='#0C857F', alpha=0.3)
plt.xlabel("Rotten Tomatoes Score")
plt.ylabel("Domestic Box Office Gross")
plt.title("Types of A24 Films")

plt.ylim(0,)
ax = plt.subplot()
ax.set_xticks([i*25 for i in range(5)])
ylabels = ['${:,.0f}m'.format(label/1000000) for label in ax.get_yticks()]
ax.set_yticklabels(ylabels)

plt.show()    


run_time=time() - start_time
print("--- {} seconds ---".format(run_time))