#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:26:44 2022

@author: davide
"""

from pathlib import Path
import csv
import pycountry_convert as pc

answer_full = Path("Dataset/answerdatacorrect.csv")


# Define the answer table
answerTable = Path("Tables/answer.csv")
answerHeader = ["QuestionId", "UserId", "AnswerId", "SubjectId", "OrganizationId", "DateId"]
answerOthers = ["AnswerValue", "CorrectAnswer", "Confidence", "IsCorrect"]

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
geoHeader = ["GeoId", "Region", "Country_Name", "Continent"]

def extract_table(file, header):
    print(f"Extracting {file}\nwith header: {header}…")
    ids = 0
    regions = set()
    with open(file, mode="w+") as targetFile:
        targetFile.write(f"{','.join(header)}\n")
        
        with open(answer_full) as sourceFile:
            # Iterate over rows
            sourceRows = csv.DictReader(sourceFile)
            for row in sourceRows:
                to_write = ""
                # Combine the right values for the row
                for row_key, row_value in row.items():
                    if row_key in header:
                        if "geography" not in file.stem:
                            to_write = f"{to_write},{row_value}"
                        
                # if extracting table is answer-1 alpha-2
                # then compare AnswerValue with CorrectAnswer
                # in order to get the correct value of IsCorrect
                if "answer" in file.stem:
                    if row["AnswerValue"] == row["CorrectAnswer"]:
                        to_write = f"{to_write},1"
                    else:
                        to_write = f"{to_write},0"
                        
                if "geography" in file.stem:
                    regionName = row["Region"]
                    if regionName not in regions:
                        ids = ids + 1
                        regions.add(regionName)
                        
                        # converting uk to gb according to ISO 3166 standard
                        if row["CountryCode"] == "uk": row["CountryCode"] = "gb"
                        #converting CountryCode to CountryName
                        country_name = pc.country_alpha2_to_country_name(row["CountryCode"].upper(), cn_name_format="default")
                        #converting CountryCode to Continent
                        continent_name = pc.country_alpha2_to_continent_code(row["CountryCode"].upper())
                        to_write = f"{to_write},{ids},{regionName},{country_name},{continent_name}"
                    else:
                        continue
                #Write the new row to the file
                targetFile.write(f"{to_write[1:]}\n")
                
extract_table(answerTable, answerOthers)   
extract_table(geoTable, geoHeader)

            
# problemi da risolvere:
    #manca OrganizationId, DateId, GeoId (come generarle? In che ordine?)
    #SubjectId prensenta delle virgole la suo interno (conflitto con delimitatore)