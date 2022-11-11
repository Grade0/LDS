#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 23:55:49 2022

@author: davide
"""

import pyodbc
from pathlib import Path
import csv
from rich.progress import track
from rich.console import Console

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
    if name == "answer":
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
                "str", #Country_Name
                "str"  #Continent
                ]
    elif name == "organization":
        return ["str",  #OrganizationId
                "int",  #GroupId
                "int",  #QuizId
                "float" #SchemeOfWork
                ]
    elif name == "subject":
        return [
            "str", #SubjectId
            "str"  #Description
            ]
    elif name == "date":
        return ["str", #DateId
                "str", #Date
                "int", #Year
                "int", #Month
                "int", #Day
                "int"  #Quarter
                ]
    elif name == "user":
        return ["int", #DateId
                "int", #Gender
                "int", #GeoId
                "int"  #DateOfBirthId
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
        for row in track(reader, total=csv_len, description=f"{name}…"):
            to_send = ""
            for i, value in enumerate(row.values()):
                if header[i] == "str":
                    # check if there's an apostrophe in the string and "escape" it
                    position = value.find("'")
                    if position != -1:
                        value = f"{value[:position]}'{value[position:]}"
                    to_send = f"{to_send},'{value}'"
                else:
                    to_send = f"{to_send},{value}"
            try:
                query = f"INSERT INTO {name} VALUES ({to_send[1:]});"
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

# tables["Date"] = (Path("data/dates.csv"), 375)
# tables["Geography"] = (Path("data/countries.csv"), 124)
# tables["Player"] = (Path("data/players.csv"), 10074)
# tables["Tournament"] = (Path("data/tournaments.csv"), 4853)
tables["geography"] = (Path("Tables/geography.csv"), 75)


console.log("Loading…")

for name, path_and_len in tables.items():
    load_table(name, path_and_len[0], csv_len=path_and_len[1])

console.log(f"Loaded {len(tables)} tables onto server.")