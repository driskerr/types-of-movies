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
import mpld3
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
from sklearn.cluster import DBSCAN
import hdbscan
import scipy.cluster.hierarchy as hac
import seaborn as sns


path = '/Users/kerrydriscoll/Desktop/resumes/A24/types_of_A24.xlsx'
xls = pd.ExcelFile(path)
sheet = xls.sheet_names[-1] #get last sheet
df_final = pd.read_excel(xls, sheet)


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
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.gca().set_ylim(0,)
plt.gca().set_xlim(0,105)


titles = df_final['Title'].tolist()
tooltip = mpld3.plugins.PointHTMLTooltip(scatter, labels=titles, css=css, voffset=-10, hoffset=5)
mpld3.plugins.connect(fig, tooltip)

mpld3.enable_notebook()
mpld3.save_html(fig, "./mpld3_htmltooltip.html")
#mpld3.show()

sleep(random.uniform(0.3, 0.8))


"""
Perform DB Scan
"""
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

"""
Alternate HDBSCAN
"""
"""
X = list(map(list, zip(x, y)))
X = StandardScaler().fit_transform(X)
hdb = hdbscan.HDBSCAN(min_cluster_size=3, gen_min_span_tree=True).fit(X)
labels = hdb.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, labels))
      
unique_labels = set(labels)
unique_labels = sorted(list(unique_labels))

for k in unique_labels:
    class_member_mask = (labels == k)
    class_titles = [i[0] for i in zip(titles, class_member_mask) if i[1]==True] 
    print(k, class_titles)
      
palette = sns.color_palette()
cluster_colors = [sns.desaturate(palette[col], sat) 
                  if col >= 0 else (0.5, 0.5, 0.5) for col, sat in 
                  zip(hdb.labels_, hdb.probabilities_)]
plt.scatter(X[:, 0], X[:, 1], c=cluster_colors)
plt.show()
      
sleep(random.uniform(0.3, 0.8))
#"""

"""
Alternate HIERARCHICAL AGGLOMERATIVE CLUSTERING
"""
#"""
X = np.asarray(list(map(list, zip(x, y))))
X = StandardScaler().fit_transform(X)


z = hac.linkage(X, method='complete')
knee = np.diff(z[::-1, 2], 2)
knee[knee.argmax()] = 0
num_clust = knee.argmax() + 2
labels = hac.fcluster(z, num_clust, 'maxclust')

unique_labels = set(labels)
#"""
    

"""
Apply Types
"""

fig2, ax2 = plt.subplots(subplot_kw=dict(axisbg='#F0F0F0'))
X = np.asarray(list(map(list, zip(x, y))))
unique_labels = set(labels)
unique_labels = sorted(list(unique_labels))
#colors = ['#0C857F', '#FB0101', '#F6FE07', '#211B92']
#edges= ['#085652', '#950101', '#cad101', '#171367']

colors = ['#71B779', '#0E9C95','#F798B5','#FE8C06','#9D5B9A','#8D8D8D', '#CBB977', '#69B3CE', '#907A56']
edges =  ['#387044', '#085652','#EF3A71','#B76301','#5D355A','#747474', '#BDA652', '#43A0C1', '#705F43']
if min(unique_labels) == -1: #only the case for dbscan items that were not classified
    colors = [[0, 0, 0, 1]] + colors
    edges= ['k'] + edges
else:
    core_samples_mask = np.repeat(True, len(labels))
    
for k, col, ed in zip(unique_labels, colors, edges):
    
    class_member_mask = (labels == k)
    
    xy = X[class_member_mask & core_samples_mask]
    scatter1 = ax2.scatter(xy[:, 0], xy[:, 1], c=col, edgecolor=ed, s=55, alpha=0.4)
    
    labels1=[i[0] for i in zip(titles, class_member_mask & core_samples_mask) if i[1]==True]
    if xy.size != 0:         
        tooltip1 = mpld3.plugins.PointHTMLTooltip(scatter1, labels=labels1, css=css, voffset=-10, hoffset=5)
        mpld3.plugins.connect(fig2, tooltip1)
    """
    #DBSCAN items not in "core" sample
    
    xy = X[class_member_mask & ~core_samples_mask]
    scatter2 = ax2.scatter(xy[:, 0], xy[:, 1], c=col, edgecolor=ed, s=30, alpha=0.2)
    
    labels2=[i[0] for i in zip(titles, class_member_mask & ~core_samples_mask) if i[1]==True]         
    if xy.size != 0:         
        tooltip2 = mpld3.plugins.PointHTMLTooltip(scatter2, labels=labels2, css=css, voffset=-10, hoffset=5)
        mpld3.plugins.connect(fig2, tooltip2)
    """
             
    class_titles = [i[0] for i in zip(titles, class_member_mask) if i[1]==True]
    
    print(k, class_titles)
    


ax2.set_title('Types of A24 Films')
ax2.set_xlabel("Rotten Tomatoes Score")
ax2.set_ylabel("Domestic Box Office Gross (millions, 2015 $)")
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.yaxis.set_ticks_position('left')
ax2.xaxis.set_ticks_position('bottom')
plt.gca().set_ylim(0,)
plt.gca().set_xlim(0,105)

ax2.grid(color='#E3E3E3', linestyle='solid')

plt.show()


mpld3.enable_notebook()
if min(unique_labels) == -1:
    mpld3.save_html(fig2, "./mpld3_htmltooltip_colors_dbscan_{}.html".format(datetime.date.today().strftime("%Y-%m-%d")))
else:
    mpld3.save_html(fig2, "./mpld3_htmltooltip_colors_hac_{}.html".format(datetime.date.today().strftime("%Y-%m-%d")))
    
# add category labels to source Excel table    
category_dict = dict(zip(titles, labels))
df_final['Category'] = df_final['Title'].map(category_dict)

#path = '/Users/kerrydriscoll/Desktop/resumes/A24/types_of_A24.xlsx'
book = load_workbook(path)
book.remove_sheet(book.worksheets[-1])
writer = ExcelWriter(path, engine = 'openpyxl')
writer.book = book
df_final.to_excel(writer, sheet_name=datetime.date.today().strftime("%Y-%m-%d"))
writer.save()