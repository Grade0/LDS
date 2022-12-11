#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:26:44 2022

@author: davide
"""

from pathlib import Path
import csv
from rich.console import Console
from rich.progress import track
import pycountry_convert as pc
import ast
import collections

answer_full = Path("dataset/answerdatacorrect.csv")
subject_metadata = Path("dataset/subject_metadata.csv")


# Define the tables path and headers
answerTable = Path("tables/answer.csv")
answerHeader = ["QuestionId", "UserId", "AnswerId", "CorrectAnswer", "AnswerValue", "Confidence", "SubjectId", "IsCorrect", "OrganizationId", "DateId"]

organizationTable = Path("tables/organization.csv")
organizationHeader = ["Organizationid", "GroupId", "QuizId", "SchemeOfWorkId"]

dateTable = Path("tables/date.csv")
dateHeader = ["DateId", "Date", "Day", "Month", "Year", "Quarter"]

subjectTable = Path("tables/subject.csv")
subjectHeader = ["SubjectId","Description"]

userTable = Path("tables/user.csv")
userHeader = ["UserId", "DateOfBirthId", "GeoId", "Gender"]

geoTable = Path("tables/geography.csv")
geoHeader = ["GeoId", "Region", "CountryName", "Continent"]

# support variables
regions = {}
userGeoId = {}
answerOrgId = {}
birth_tms = {}
answer_tms = {}
orgIds = {}
dateIds = {}

def extract_table(file, header):
    console.log(f"Extracting {file}\nwith header: {header}…")
    ids = 0
    
    elIds = set()
    
    with open(file, mode="w+") as targetFile:
        targetFile.write(f"{','.join(header)}\n")
        
        with open(answer_full) as sourceFile:
            # Iterate over 538835 rows 
            for row in track(csv.DictReader(sourceFile), total=538835):
                execute = 1
                to_write = ""
                merge_ids = ',"['
                date_write = ""
                
                # if extracting table is answer
                if "answer" in file.stem:
                    orgId = answerOrgId.get(row["AnswerId"])
                    dateId =  answer_tms.get(row["AnswerId"])
                    
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
                    to_write = f'{to_write},{orgId},{dateId}'
                        
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
                            
                            sub_lev = {}
                            
                            #iterate over id, if match add the subjectName 
                            #in a dictionary indexed by "Level"
                            for index in subjectIds:
                                for sub in subjectRows:
                                    if index == int(sub["SubjectId"]):
                                        sub_lev[sub["Level"]] = sub["Name"]
                                        break
                            # sort the dictionary by key (level)
                            sub_ordered = collections.OrderedDict(sorted(sub_lev.items()))
                            
                            #combine the values to get row
                            for s_key, s_value in sub_ordered.items():
                                to_write = f'{to_write}{s_value}, '
                            
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
                            merge_ids = f'{merge_ids}{row_value}, '
                    
                    merge_ids = f'{merge_ids[:-2]}]"'
                    
                    # check the uniqueness of organizationId obtained
                    if orgIds.get(merge_ids) == None:
                        ids += 1
                        orgIds[merge_ids] = ids
                        to_write = f",{ids}{to_write}"
                        #this var is used for parse the correct organizzationId for answer table
                        answerOrgId[row["AnswerId"]] = ids
                    else:
                        #idem for not uniqueness ids
                        answerOrgId[row["AnswerId"]] = orgIds.get(merge_ids)
                        execute = 0
                    
                # if extracting table is user
                elif "user" in file.stem:
                    # check the uniqueness of the value
                    if row["UserId"] not in elIds:
                        elIds.add(row["UserId"])
                        #this dict is used to get the correct GeoId
                        geoId = userGeoId.get(row["UserId"])
                        #this dict is used to get the correct dateOfBirthId
                        dateOfBirthId = birth_tms.get(row["UserId"])
                        
                        to_write = f'{to_write},{row["UserId"]},{dateOfBirthId},{geoId},{row["Gender"]}'
                    else:
                        execute = 0
                
                # if extracting table is date
                elif "date" in file.stem:
                    dateOfBirth = row["DateOfBirth"]
                    dateAnswered = row["DateAnswered"][:10]
                    
                    # Here we check the uniqueness of DateOfBirth
                    if dateIds.get(dateOfBirth) == None:
                        # increase the index
                        ids += 1
                        # this dict is used to parse the correct dateOfBirthId for user table
                        birth_tms[row["UserId"]] = ids
                        #this set is used for uniqueness
                        dateIds[dateOfBirth] = ids
                        
                        
                        # Compute che value of Quarter by month
                        month = int(dateOfBirth[5:7])
                        if month <= 3: q = 1
                        elif month > 3 and month <= 6: q = 2
                        elif month > 6 and month <= 9: q = 3
                        else: q = 4
                        to_write = f'{to_write},{ids},{dateOfBirth},{dateOfBirth[8:10]},{dateOfBirth[5:7]},{dateOfBirth[:4]},{q}'
                        
                    else:
                        birth_tms[row["UserId"]] = dateIds.get(dateOfBirth)
                        execute = 0
                     
                    # Here we check the uniqueness of DateAnswered
                    if dateIds.get(dateAnswered) == None:
                        # increase the index
                        ids += 1
                        # this dict is used to parse the correct Dateid for answer table
                        answer_tms[row["AnswerId"]] = ids
                        #this set is used for uniqueness
                        dateIds[dateAnswered] = ids
                        
                        # Compute che value of Quarter by month
                        month = int(dateAnswered[5:7])
                        if month <= 3: q = 1
                        elif month > 3 and month <= 6: q = 2
                        elif month > 6 and month <= 9: q = 3
                        else: q = 4
                        date_write = f'{date_write},{ids},{dateAnswered},{dateAnswered[8:10]},{dateAnswered[5:7]},{dateAnswered[:4]},{q}'
                        targetFile.write(f"{date_write[1:]}\n")
                    else:
                        answer_tms[row["AnswerId"]] = dateIds.get(dateAnswered)
                        execute = 0
                        
                             
                #Write the new row to the file
                if(execute):
                    targetFile.write(f"{to_write[1:]}\n")
                    
console = Console()
       
# Split tables
extract_table(organizationTable, organizationHeader)
extract_table(dateTable, dateHeader)
extract_table(answerTable, answerHeader)   
extract_table(geoTable, geoHeader)
extract_table(subjectTable, subjectHeader)
extract_table(userTable, userHeader)

console.log("Extraction completed!")