#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:28:34 2022

@author: davide
"""

import pyodbc
from pathlib import Path
import csv
from rich.progress import track
from rich.console import Console
import pandas as pd

def open_conn():
    server = "tcp:131.114.72.230"  # lds.di.unipi.it
    database = "Group_24_DB"
    username = "Group_24"
    password = "HBL87UE9"
    connectionString = (
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    cn = pyodbc.connect(connectionString)
    return cn, cn.cursor()

def close_conn(cn, cursor):
    cursor.close()
    cn.close()
    
    
def get_header_types(name: str):
    if name == "answers":
        return ["int",   #QuestionId
                "int",   #UserId
                "int",   #AnswerId
                "int",   #CorrectAnswer
                "int",   #AnswerValue
                "float", #Confidence
                "str",   #SubjectId
                "int",   #IsCorrect
                "str",   #OrganizationId
                "str"    #DateId
                ]
    elif name == "geography":
        return ["int", #GeoId
                "str", #Region
                "str", #CountryName
                "str"  #Continent
                ]
    elif name == "organization":
        return ["str",  #OrganizationId
                "int",  #GroupId
                "int",  #QuizId
                "float" #SchemeOfWorkId
                ]
    elif name == "subject":
        return [
            "str", #SubjectId
            "str"  #Description
            ]
    elif name == "date":
        return ["str", #DateId
                "str", #Date
                "int", #Day
                "int", #Month
                "int", #Year
                "int"  #Quarter
                ]
    elif name == "user":
        return ["int", #UserId
                "str", #DateOfBirthId
                "int", #GeoId
                "int"  #Gender
                ]
    else:
        raise ValueError("get_header_type got a strange name.")
        
        
def load_table(name: str, my_path: Path, csv_len: int):
    # 0. get header types
    header = get_header_types(name)
    # 1. open connection to server
    cn, cursor = open_conn()

    # 2. load table into memory
    with open(my_path) as source:
        reader = csv.DictReader(source)
        

        # 3. write table onto server, row by row? Remember the data-types
        commit_counter = 0
        for row in track(reader, total=csv_len, description=f"{name}:"):
            to_send = ""
            for i, value in enumerate(row.values()):
                if header[i] == "str":
                    # check if there's an apostrophe in the string and "escape" it
                    position = value.find('"')
                    if position != -1:
                        value = f'{value[:position]}"{value[position:]}'
                    to_send = f"{to_send},'{value}'"
                else:
                    to_send = f"{to_send},{value}"
            try:
                query = f"INSERT INTO [Group_24].[{name}] VALUES ({to_send[1:]});"
                cursor.execute(query)
            except Exception as e:
                print(f"Program failed on query {query}\nwith exception {e}")
                close_conn(cn, cursor)
            # commit once every 100 rows/queries
            commit_counter += 1
            if commit_counter == 100:
                cn.commit()
                commit_counter = 0
        # if there are "leftover" rows, commit them too.
        if commit_counter > 0:
            cn.commit()
    # 4. close connection
    close_conn(cn, cursor)

console = Console()
tables = {}

answer_path = Path("tables/answer.csv")
org_path = Path("tables/organization.csv")
date_path = Path("tables/date.csv")
subject_path = Path("tables/subject.csv")
user_path = Path("tables/user.csv")
geo_path = Path("tables/geography.csv")

answer_len = len(pd.read_csv(answer_path))-1
org_len = len(pd.read_csv(org_path))-1
date_len = len(pd.read_csv(date_path))-1
subject_len = len(pd.read_csv(subject_path))-1
user_len = len(pd.read_csv(user_path))-1
geo_len = len(pd.read_csv(geo_path))-1



tables["organization"] = (org_path, org_len)
tables["date"] = (date_path, date_len)
tables["subject"] = (subject_path, subject_len)
tables["user"] = (user_path, user_len)
tables["geography"] = (geo_path, geo_len)
tables["answers"] = (answer_path, answer_len)


console.log("Loading…")

for name, path_and_len in tables.items():
    load_table(name, path_and_len[0], csv_len=path_and_len[1])

console.log(f"Loaded {len(tables)} tables onto server.")