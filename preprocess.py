#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:25:33 2022

@author: davide
"""

import pandas as pd

df = pd.read_csv("dataset/answerdatacorrect.csv")

# Check for missing values
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

print("\nThe Dataframe has " + str(df.shape[1]) + " columns.\n"
                                              "There are " + str(mis_val_table_ren_columns.shape[0]) +
      " column with missing value.\n")

# Check for unique and duplicates values
df_len = len(df)
print("The csv file has a total of",len(df), "rows:")
print("- AnswerId has",len(df['AnswerId'].unique()), "unique values and", df.duplicated(['AnswerId']).sum(), "duplicates")
print("- UserId has",len(df['UserId'].unique()), "unique values and",df.duplicated(['UserId']).sum(), "duplicates")
print("- SubjectId has",len(df['SubjectId'].unique()), "unique values and",df.duplicated(['SubjectId']).sum(), "duplicates")
print("- Organization Table will have a total", df.groupby(['GroupId','QuizId','SchemeOfWorkId']).ngroups, "unique rows (GroupId, QuizId, SchemeOfWorkId)")
print("- Geography Table will have a total", len(df['Region'].unique()), "unique rows (Region)")

# Data trasformation
print("\nValues of original column CountyCode: \n", df['CountryCode'].unique())
df['CountryCode'] = df['CountryCode'].replace('uk', 'gb')
df.to_csv("dataset/answerdatacorrect.csv", index=False)
print("\nIn order to match [ISO 3166-1 alpha-2] standard of country code, it was applied a transformation for the code 'uk' to 'gb'")
