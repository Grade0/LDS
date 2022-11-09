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


# Define the tables path and headers
answerTable = Path("Tables/answer.csv")
answerHeader = ["QuestionId", "UserId", "AnswerId", "CorrectAnswer", "AnswerValue", "Confidence", "SubjectId", "IsCorrect", "OrganizationId", "DateId"]

organizationTable = Path("Tables/organization.csv")
organizationHeader = ["Organizationid", "GroupId", "QuizId", "SchemeOfWorkId"]

dateTable = Path("Tables/date.csv")
dateHeader = ["DateId", "Date", "Year", "Month", "Day", "Quarter"]

subjectTable = Path("Tables/subject.csv")
subjectHeader = ["SubjectId","Description"]

userTable = Path("Tables/user.csv")
userHeader = ["UserId", "Gender", "GeoId", "DateOfBirthId"]

geoTable = Path("Tables/geography.csv")
geoHeader = ["GeoId", "Region", "Country_Name", "Continent"]

# support variables
regions = {}
userGeoId = {}
answerOrgId = {}
birth_tms = {}
answer_tms = {}

def extract_table(file, header):
    print(f"Extracting {file}\nwith header: {header}…")
    ids = 0
    ids2 = 0
    
    elIds = set()
    orgIds = set()
    with open(file, mode="w+") as targetFile:
        targetFile.write(f"{','.join(header)}\n")
        
        with open(answer_full) as sourceFile:
            # Iterate over rows
            sourceRows = csv.DictReader(sourceFile)
            for row in sourceRows:
                execute = 1
                to_write = ""
                merge_write = ',"['
                date_write = ""
                
                # if extracting table is answer
                if "answer" in file.stem:
                    # iterate over the rows
                    for row_key, row_value in row.items():
                        
                        # check if the attribute is contained in header
                        if row_key in header:
                            # Since SubjectId contains comma we should add quotes to csv
                            if row_key == "SubjectId":
                                to_write = f'{to_write},"{row_value}"'
                            else:
                                to_write = f"{to_write},{row_value}"
                                
                    # compute the value of isCorrect
                    if row["AnswerValue"] == row["CorrectAnswer"]:
                        to_write = f"{to_write},1"
                    else:
                        to_write = f"{to_write},0"
                        
                    # concatenate elements in order to get the final row
                    to_write = f'{to_write},{answerOrgId.get("AnswerId")},{answer_tms.get("AnswerId")}'
                        
                # if extracting table is answer
                elif "geography" in file.stem:
                    regionName = row["Region"]
                    userId = row["UserId"]
                    
                    # check if the current regionName is unique
                    if regions.get(regionName) == None:
                        # then increase the index
                        ids += 1
                        # this dict is used for check the uniqueness
                        regions[regionName] = ids
                        # this dict is used for parse the correct geoId for user table
                        userGeoId[userId] = ids
                        
                        
                        # converting uk to gb according to ISO 3166-1 alpha-2 standard
                        if row["CountryCode"] == "uk": row["CountryCode"] = "gb"
                        #converting CountryCode to CountryName
                        country_name = pc.country_alpha2_to_country_name(row["CountryCode"].upper(), cn_name_format="default")
                        #converting CountryCode to Continent
                        continent_name = pc.country_alpha2_to_continent_code(row["CountryCode"].upper())
                        
                        # concatenate elements in order to get the final row
                        to_write = f"{to_write},{ids},{regionName},{country_name},{continent_name}"
                    else:
                        # this dict is used for parse the correct geoId for user table
                        userGeoId[userId] = regions.get(regionName)
                        #skip the write to csv because the key is already present
                        execute = 0
                    
                # if extracting table is subject
                elif "subject" in file.stem:
                    
                    # check if the current regionName is unique
                    if row["SubjectId"] not in elIds:
                        elIds.add(row["SubjectId"])
                        
                        to_write = f'{to_write},"{row["SubjectId"]}"'
                        
                        with open(subject_metadata, mode="r", encoding='utf-8-sig') as subjectFile:
                            # convert list-like string to real list
                            subjectIds = ast.literal_eval(row["SubjectId"])
                            # extract rows from the file
                            subjectRows = csv.DictReader(subjectFile)
                            
                            to_write = f'{to_write},"'
                            
                            #iterate over id, if match the get the subjectName
                            for index in subjectIds:
                                for sub in subjectRows:
                                    if index == int(sub["SubjectId"]):
                                        to_write = f'{to_write}{sub["Name"]}, '
                                        break
                            to_write = f'{to_write[:-2]}"'
                    else:
                        # skip the file write because is not unique
                        execute = 0
                            
                # if extracting table is organization
                elif "organization" in file.stem:
                    
                    # iterate over attributes
                    for row_key, row_value in row.items():
                        if row_key in header:
                            to_write = f"{to_write},{row_value}"
                            # this var is used to combine the attribute and get the organizationId
                            merge_write = f'{merge_write}{row_value}, '
                    
                    merge_write = f'{merge_write[:-2]}]"'
                    to_write = f'{merge_write}{to_write}'
                    
                    # check the uniqueness of organizationId obtained
                    if merge_write not in orgIds:
                        orgIds.add(merge_write)
                        #this var is used for parse the correct organizzationId for answer table
                        answerOrgId["AnswerId"] = f"{merge_write[1:]}"
                    else:
                        #idem for not uniqueness ids
                        answerOrgId["AnswerId"] = f"{merge_write[1:]}"
                        execute = 0
                    
                # if extracting table is user
                elif "user" in file.stem:
                    # check the uniqueness of the value
                    if row["UserId"] not in elIds:
                        elIds.add(row["UserId"])
                        #this dict is used to get the correct GeoId
                        geoId = userGeoId.get(row["UserId"])
                        to_write = f'{to_write},{row["UserId"]},{birth_tms.get("UserId")},{row["Gender"]},{geoId}'
                    else:
                        execute = 0
                
                # if extracting table is date
                elif "date" in file.stem:
                    #these set are used to check the uniqueness of dates
                    a_tms = set()
                    b_tms = set()
                    
                    # Here we check the uniqueness of DateOfBirth
                    if row["DateOfBirth"] not in b_tms:
                        # increase the index
                        ids += 1
                        # this dict is used to parse the correct dateOfBirthId for user table
                        birth_tms["UserId"] = f"birth_{ids}"
                        #this set is used for uniqueness
                        b_tms.add(row["DateOfBirth"])
                        
                        # Compute che value of Quarter by month
                        month = int(row["DateOfBirth"][5:7])
                        if month <= 3: q = 1
                        elif month > 3 and month <= 6: q = 2
                        elif month > 6 and month <= 9: q = 3
                        else: q = 4
                        to_write = f'{to_write},birth_{ids},{row["DateOfBirth"]},{row["DateOfBirth"][:4]},{row["DateOfBirth"][5:7]},{row["DateOfBirth"][8:10]},{q}'
                    else:
                        birth_tms["UserId"] = f"birth_{ids}"
                        execute = 0
                     
                    # Here we check the uniqueness of DateAnswered
                    if row["DateAnswered"] not in a_tms:
                        # increase the index
                        ids2 += 1
                        # this dict is used to parse the correct Dateid for answer table
                        answer_tms["AnswerId"] = f"answer_{ids2}"
                        #this set is used for uniqueness
                        a_tms.add(row["DateAnswered"])
                        
                        # Compute che value of Quarter by month
                        month = int(row["DateAnswered"][5:7])
                        if month <= 3: q = 1
                        elif month > 3 and month <= 6: q = 2
                        elif month > 6 and month <= 9: q = 3
                        else: q = 4
                        date_write = f'{date_write},answer_{ids2},{row["DateAnswered"][:10]},{row["DateAnswered"][:4]},{row["DateAnswered"][5:7]},{row["DateAnswered"][8:10]},{q}'
                        targetFile.write(f"{date_write[1:]}\n")

                    else:
                        answer_tms["AnswerId"] = f"answer_{ids2}"
                        
                             
                #Write the new row to the file
                if(execute):
                    targetFile.write(f"{to_write[1:]}\n")
       
# Split tables
extract_table(organizationTable, organizationHeader)
extract_table(dateTable, dateHeader)
extract_table(answerTable, answerHeader)   
extract_table(geoTable, geoHeader)
extract_table(subjectTable, subjectHeader)
extract_table(dateTable, dateHeader)
extract_table(userTable, userHeader)


    