# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 21:25:18 2018

@author: kerrydriscoll
"""

"""
TO DO:

* filter by year?

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


path = '/Users/kerrydriscoll/Desktop/resumes/A24/types_of_A24.xlsx'
df_final = pd.read_excel(path)


"""
Visualization
"""

css = """
text.mpld3-text, div.mpld3-tooltip {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 9px;
  color: black;
  opacity: 1.0;
  padding: 2px;
  border: 0px;
}
"""

fig, ax = plt.subplots(subplot_kw=dict(axisbg='#F0F0F0'))

x = df_final['Rotten Tomatoes Score'].apply(lambda x: float(x.replace('%', '')))
y = df_final['Adjusted Domestic Box Office Gross'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
y = y/1000000

scatter = ax.scatter(x, y, c='#0C857F', edgecolor='#085652',s=55,alpha=0.3)


ax.grid(color='#E3E3E3', linestyle='solid')
ax.set_title("Types of A24 Films", size=12)
ax.set_xlabel("Rotten Tomatoes Score")
ax.set_ylabel("Domestic Box Office Gross (millions, 2015 $)")
plt.gca().set_ylim(0,)
plt.gca().set_xlim(0,105)
#ax.set_xticks([i*25 for i in range(5)])
#ylabels = ['${:,.0f}m'.format(label/1000000) for label in ax.get_yticks()]
#ax.set_yticklabels(ylabels)

titles = df_final['Title'].tolist()
tooltip = mpld3.plugins.PointHTMLTooltip(scatter, labels=titles, css=css, voffset=10, hoffset=10)
mpld3.plugins.connect(fig, tooltip)

mpld3.enable_notebook()
mpld3.save_html(fig, "./mpld3_htmltooltip.html")
#mpld3.show()

sleep(random.uniform(0.3, 0.8))


"""
Perform DB Scan
"""

X = list(map(list, zip(x, y)))
X = StandardScaler().fit_transform(X)
db = DBSCAN(eps=.45, min_samples=3).fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, labels))
      
sleep(random.uniform(0.3, 0.8))

"""
Apply Types
"""

fig2, ax2 = plt.subplots(subplot_kw=dict(axisbg='#F0F0F0'))
X = np.asarray(list(map(list, zip(x, y))))
unique_labels = set(labels)
unique_labels = sorted(list(unique_labels))
#colors = ['#0C857F', '#FB0101', '#F6FE07', '#211B92']
#edges= ['#085652', '#950101', '#cad101', '#171367']
colors = [[0, 0, 0, 1], '#FE8C06', '#FB0101', '#211B92']
edges= ['k', '#B76301', '#950101', '#171367']
for k, col, ed in zip(unique_labels, colors, edges):
    #if k == -1:
        # Black used for noise.
     #   col = [0, 0, 0, 1]
     #   ed = 'k'
    
    class_member_mask = (labels == k)
    
    xy = X[class_member_mask & core_samples_mask]
    scatter1 = ax2.scatter(xy[:, 0], xy[:, 1], c=col, edgecolor=ed, s=55, alpha=0.4)
    
    labels1=[i[0] for i in zip(titles, class_member_mask & core_samples_mask) if i[1]==True]
    if xy.size != 0:         
        tooltip1 = mpld3.plugins.PointHTMLTooltip(scatter1, labels=labels1, css=css, voffset=10, hoffset=10)
        mpld3.plugins.connect(fig2, tooltip1)
    
    xy = X[class_member_mask & ~core_samples_mask]
    scatter2 = ax2.scatter(xy[:, 0], xy[:, 1], c=col, edgecolor=ed, s=30, alpha=0.2)
    
    labels2=[i[0] for i in zip(titles, class_member_mask & ~core_samples_mask) if i[1]==True]         
    if xy.size != 0:         
        tooltip2 = mpld3.plugins.PointHTMLTooltip(scatter2, labels=labels2, css=css, voffset=10, hoffset=10)
        mpld3.plugins.connect(fig2, tooltip2)
             
    class_titles = [i[0] for i in zip(titles, class_member_mask) if i[1]==True]
    
    print(k, class_titles)


ax2.set_title('Types of A24 Films')
ax2.set_xlabel("Rotten Tomatoes Score")
ax2.set_ylabel("Domestic Box Office Gross (millions, 2015 $)")
plt.gca().set_ylim(0,)
plt.gca().set_xlim(0,105)

ax2.grid(color='#E3E3E3', linestyle='solid')
#ax2.set_xticks([i*25 for i in range(5)])
#ylabels = ['${:,.0f}m'.format(label) for label in ax2.get_yticks()]
#ax2.set_yticklabels(ylabels)

plt.show()

mpld3.enable_notebook()
mpld3.save_html(fig2, "./mpld3_htmltooltip_colors.html")