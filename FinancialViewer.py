# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 20:29:35 2019

@author: dosre
"""

import numpy as np
import mysql.connector
import matplotlib.pyplot as plt
from bokeh.palettes import Category10, Category20

colors = Category20[20]

cnx = mysql.connector.connect(user='root', password='Roviary13Roce',
                              host='127.0.0.1', database='giraffe')

cursor = cnx.cursor()

cursor.execute("SELECT * FROM finances")

data = [list(month) for month in cursor.fetchall()]

# Adds chq and sav for total sum 
total = []
for yr_month, chq, sav in data:
    total.append([yr_month, chq+sav])
total = np.array(total)

print(total)

fig, ax = plt.subplots(figsize=(5, 3))
ax.plot(range(total[:, 1].size), total[:, 1], color="grey")
for x, y, c in zip(range(total[:, 1].size), total[:, 1], Category10[10]):
    ax.plot(x, y, "o", markersize=8, color=c)
temp = [0] + [int(i) for i in total[:, 0]]
ax.set_xticklabels(temp)
ax.set_ylabel("Total Worth ($)")
ax.set_xlabel("Year-Month (yrmn)")
ax.set_title("Net Worth per Month")
plt.savefig(
    "C:\\Users\\dosre\\OneDrive\\Documents\\Personal Folder\\Finances and Taxes\\"+
    "networth.png")
plt.show()

change = total[:, 1] - np.roll(total[:, 1], 1)
change = change[1:]

fig, ax = plt.subplots(figsize=(5, 3))
for x, y, c in zip(range(change.size), change, Category10[10][1:]):
    ax.bar(x, y, color=c)
ax.axhline(0, color="k")
temp = [int(i) for i in total[:, 0]]
ax.set_ylabel("Income ($)")
ax.set_xlabel("Year-Month (yrmn)")
ax.set_xticklabels(temp)
ax.set_title("Income per Month")
plt.savefig(
    "C:\\Users\\dosre\\OneDrive\\Documents\\Personal Folder\\Finances and Taxes\\"+
    "income.png")
plt.show()

cnx.close()