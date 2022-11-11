#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 14:01:09 2022

@author: davide
"""

import pandas as pd

df = """Countries_ceck"""

df = pd.read_csv("Dataset/answerdatacorrect.csv")
# print(df.info())
#df_1 = pd.read_csv("data/inputs/countryinfo.tsv", sep="\t")

#print("Values in countries.csv, column counrty_name: \n", df['Region'].unique())

# print("Value in  countryinfo.tsv , column Country  :\n", df_1['Country'].unique())

mis_val = df.isnull().sum()
mis_val_percent = 100 * df.isnull().sum() / len(df)
mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
mis_val_table_ren_columns = mis_val_table.rename(
    columns={0: 'Missing Values', 1: '% of Total Values'})
mis_val_table_ren_columns = mis_val_table_ren_columns[
    mis_val_table_ren_columns.iloc[:, 1] != 0].sort_values(
    '% of Total Values', ascending=False).round(1)

print("MISSING VALUES")
print("--------------------")
print(mis_val)

print("\nIl Dataframe ha " + str(df.shape[1]) + " colonne.\n"
                                              "Ci sono " + str(mis_val_table_ren_columns.shape[0]) +
      " colonne che hanno missing value.")

    
# print(df['country_name'].unique())