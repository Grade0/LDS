#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:26:44 2022

@author: davide
"""

from pathlib import Path
import csv

answer_full = Path("Dataset/answerdatacorrect.csv")


# Define the answer table
answerTable = Path("Tables/answer.csv")
answerHeader = ["QuestionId", "UserId", "AnswerId", "SubjectId", "OrganizationId", "DateId"]
answerOthers = ["AnswerValue", "CorrectAnswer", "Confidence", "iscorrect"]

organizationTable = Path("Tables/organization.csv")
organizationHeader = ["Organizationid"]
organizationOthers = ["GroupId", "QuizId", "SchemeOfWorkId"]

dateTable = Path("Tables/date.csv")
dateHeader = ["DateId"]
dateOthers = ["Date", "Day", "Month", "Year", "Quarter"]

subjectTable = Path("Tables/subject.csv")
subjectHeader = ["SubjectId"]
subjectOthers = ["Description"]

userTable = Path("Tables/user.csv")
userHeader = ["UserId", "DateOfBirthId", "GeoId"]
userOthers = ["Gender"]

geoTable = Path("Tables/geography.csv")
geoHeader = ["GeoId"]
geoOthers = ["Region", "Country_Name", "Continent"]

def extract_table(file, header):
    print(f"Extracting {file}\nwith header: {header}…")
    ids = -1
    with open(file, mode="w+") as targetFile:
        targetFile.write(f"{','.join(header)}\n")
        with open(answer_full) as sourceFile:
            sourceRows = csv.DictReader(sourceFile)
            for row in sourceRows:
                to_write = ""
                for row_key, row_value in row.items():
                    if row_key in header:
                        to_write = f"{to_write},{row_value}"
                if "answer" in file.stem:
                    if row["AnswerValue"] == row["CorrectAnswer"]:
                        to_write = f"{to_write},1"
                    else:
                        to_write = f"{to_write},0"
                targetFile.write(f"{to_write[1:]}\n")

                
extract_table(answerTable , answerOthers)   
            
            
# problemi da risolvere:
    #manca OrganizationId, DateId, GeoId (come generarle? In che ordine?)
    #SubjectId prensenta delle virgole la suo interno (conflitto con delimitatore)