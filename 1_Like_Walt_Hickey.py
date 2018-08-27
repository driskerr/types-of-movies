# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 13:27:54 2018

@author: kerrydriscoll
"""

"""
TO DO:
"""

import pandas as pd
from pandas import ExcelWriter
from openpyxl import load_workbook
import re
from time import time
import datetime
from requests import get
from bs4 import BeautifulSoup


"""
Measure Runtime to Evaluate Code Performance
"""
start_time = time()

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

url='http://www.natoonline.org/data/ticket-price/'
ticket_response = get(url)
ticket_soup = BeautifulSoup(ticket_response.text, 'html.parser')

table_element = ticket_soup.find_all('table', attrs={'id':'tablepress-6'})
table_element = table_element[0].text
table = table_element.split('\n\n')
table = [i.replace('\n','') for i in table[1:-1] if i != '']
table[0] = [table[0][:4]]+[table[0][4:]]
for i in range(1,len(table)):
    table[i]=table[i].split('$')
Adjustment = pd.DataFrame(columns=table[0], data=table[1:])
Adjustment['Year'] = [re.sub("[^0-9]", "", i) for i in Adjustment['Year']]
Adjustment.set_index('Year', inplace=True)

#print(Adjustment)

"""
Extract Data for each MOVIE
"""
for i in IDs.index:
    
    """
    Extract Critic Score
    """    
    rt_url = "https://www.rottentomatoes.com/m/{}".format(IDs['Rotten Tomatoes'][i])
    rt_response = get(rt_url)
    rt_soup = BeautifulSoup(rt_response.text, 'html.parser')

    score_soup = rt_soup.find_all('span', attrs={'class':'meter-value superPageFontColor'})
    score = score_soup[0].get_text() 
    
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
    
    if year not in Adjustment.index:
        year = max(Adjustment.index)
    
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
    release_ticket_value=float(Adjustment.loc[year].item())
    #release_ticket_value=float(release_ticket_value.replace( '$',''))
    release_box_office=float(box_office.replace( '$','').replace(',', ''))
    num_tix = release_box_office / release_ticket_value
    ticket_value_2015=float(Adjustment.loc['2015'].item())
    #ticket_value_2015=float(ticket_value_2015.replace( '$',''))
    
    adjusted_box_office=ticket_value_2015*num_tix
    adjusted_box_office='${:,.2f}'.format(adjusted_box_office)


    
    """
    Combine with other Titles
    """
    df = pd.DataFrame({'Title': IDs['Title'][i], 'Year': [year], 'Rotten Tomatoes Score': [score],'Unadjusted Domestic Box Office Gross': [box_office], 'Adjusted Domestic Box Office Gross': [adjusted_box_office], 'Time Stamp':datetime.datetime.now().strftime("%H:%M:%S")})
    df = df[['Title', 'Year', 'Rotten Tomatoes Score', 'Unadjusted Domestic Box Office Gross','Adjusted Domestic Box Office Gross', 'Time Stamp']]

    df_final = df_final.append(df, ignore_index=True)
    df_final = df_final[['Title', 'Year', 'Rotten Tomatoes Score', 'Unadjusted Domestic Box Office Gross','Adjusted Domestic Box Office Gross','Time Stamp']]


path = '/Users/kerrydriscoll/Desktop/resumes/A24/types_of_A24.xlsx'
book = load_workbook(path)
writer = ExcelWriter(path, engine = 'openpyxl')
writer.book = book
df_final.to_excel(writer, sheet_name=datetime.date.today().strftime("%Y-%m-%d"))
writer.save()


run_time=time() - start_time
print("--- {} seconds ---".format(run_time))