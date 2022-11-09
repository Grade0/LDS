#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:26:44 2022

@author: davide
"""

from pathlib import Path
import csv
import pycountry_convert as pc
import ast

answer_full = Path("Dataset/answerdatacorrect.csv")
subject_metadata = Path("Dataset/subject_metadata.csv")


# Define the answer table
answerTable = Path("Tables/answer.csv")
answerHeader = ["QuestionId", "UserId", "AnswerId", "SubjectId", "OrganizationId", "DateId"]
answerOthers = ["AnswerValue", "CorrectAnswer", "Confidence", "IsCorrect"]

organizationTable = Path("Tables/organization.csv")
organizationHeader = ["Organizationid", "GroupId", "QuizId", "SchemeOfWorkId"]

dateTable = Path("Tables/date.csv")
dateHeader = ["DateId"]
dateOthers = ["DateOfBirth", "DateOfAnswer"]

subjectTable = Path("Tables/subject.csv")
subjectHeader = ["SubjectId","Description"]

userTable = Path("Tables/user.csv")
userHeader = ["UserId", "Gender", "GeoId", "DateOfBirthId"]

geoTable = Path("Tables/geography.csv")
geoHeader = ["GeoId", "Region", "Country_Name", "Continent"]

userGeoId = {}

def extract_table(file, header):
    print(f"Extracting {file}\nwith header: {header}…")
    ids = 0
    regions = {}
    elIds = set()
    orgIds = set()
    with open(file, mode="w+") as targetFile:
        targetFile.write(f"{','.join(header)}\n")
        
        with open(answer_full) as sourceFile:
            # Iterate over rows
            sourceRows = csv.DictReader(sourceFile)
            for row in sourceRows:
                to_write = ""
                org_write = ',"['
                # if extracting table is answer
                # then compare AnswerValue with CorrectAnswer
                # in order to get the correct value of IsCorrect
                if "answer" in file.stem:
                    for row_key, row_value in row.items():
                        if row_key in header:
                            to_write = f"{to_write},{row_value}"
                    if row["AnswerValue"] == row["CorrectAnswer"]:
                        to_write = f"{to_write},1"
                    else:
                        to_write = f"{to_write},0"
                        
                # if extracting table is answer
                elif "geography" in file.stem:
                
                    regionName = row["Region"]
                    userId = row["UserId"]
                    if regions.get(regionName) == None:
                        
                        ids += 1
                        regions[regionName] = ids
                        userGeoId[userId] = ids
                        
                        
                        # converting uk to gb according to ISO 3166-1 alpha-2 standard
                        if row["CountryCode"] == "uk": row["CountryCode"] = "gb"
                        #converting CountryCode to CountryName
                        country_name = pc.country_alpha2_to_country_name(row["CountryCode"].upper(), cn_name_format="default")
                        #converting CountryCode to Continent
                        continent_name = pc.country_alpha2_to_continent_code(row["CountryCode"].upper())
                        to_write = f"{to_write},{ids},{regionName},{country_name},{continent_name}"
                    else:
                        userGeoId[userId] = regions.get(regionName)
                        continue
                    
                # if extracting table is subject
                elif "subject" in file.stem:
                    if row["SubjectId"] not in elIds:
                        elIds.add(row["SubjectId"])
                        
                        to_write = f'{to_write},"{row["SubjectId"]}"'
                        
                        with open(subject_metadata, mode="r", encoding='utf-8-sig') as subjectFile:
                            subjectIds = ast.literal_eval(row["SubjectId"])
                            subjectRows = csv.DictReader(subjectFile)
                            to_write = f'{to_write},"'
                            for index in subjectIds:
                                for sub in subjectRows:
                                    if index == int(sub["SubjectId"]):
                                        to_write = f'{to_write}{sub["Name"]}, '
                                        break
                            to_write = f'{to_write[:-2]}"'
                    else:
                        continue
                            
                
                elif "organization" in file.stem:
                    # Combine the right values for the row 
                    for row_key, row_value in row.items():
                        if row_key in header:
                            to_write = f"{to_write},{row_value}"
                            org_write = f'{org_write}{row_value}, '
                                
                    to_write = f'{org_write[:-2]}]"{to_write}'
                    
                    if org_write not in orgIds:
                        orgIds.add(org_write)
                    else:
                        continue
                    
                elif "user" in file.stem:
                    # Combine the right values for the row 
                    if row["UserId"] not in elIds:
                        elIds.add(row["UserId"])
                        geoId = userGeoId.get(row["UserId"])
                        to_write = f'{to_write},{row["UserId"]},{row["Gender"]},{geoId}'
                    else:
                        continue
                    
                elif "date" in file.stem:
                    # Combine the right values for the row 
                    if row["UserId"] not in elIds:
                        elIds.add(row["UserId"])
                        geoId = userGeoId.get(row["UserId"])
                        to_write = f'{to_write},{row["UserId"]},{row["Gender"]},{geoId}'
                    else:
                        continue
                    
                elif "date" in file.stem:
                    # Combine the right values for the row 
                    for row_key, row_value in row.items():
                        if row_key in header:
                            to_write = f"{to_write},{row_value}"
                            org_write = f'{org_write}{row_value}, '
                                
                    to_write = f'{org_write[:-2]}]"{to_write}'
                    
                    if org_write not in orgIds:
                        orgIds.add(org_write)
                    else:
                        continue
                        
                #Write the new row to the file
                targetFile.write(f"{to_write[1:]}\n")
                
#extract_table(answerTable, answerOthers)   
#extract_table(geoTable, geoHeader)
#extract_table(subjectTable, subjectHeader)
#extract_table(dateTable, dateOthers)
extract_table(organizationTable, organizationHeader)
#extract_table(userTable, userHeader)
#extract_table(dateTable, dateHeader)


            
# problemi da risolvere:
    #manca OrganizationId, DateId, GeoId (come generarle? In che ordine?)
    #answer non funziona più dopo il cambio ordine con del codice
    