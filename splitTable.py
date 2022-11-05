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
answerHeader = ["AnswerId", "QuestionId", "UserId", "OrganizationId", "DateId", "SubjectId"]
answerOthers = ["answer_value", "correct_answer", "iscorrect", "confidence"]

print(f"Extracting {answerTable}\nwith header: {answerHeader}…")
ids = set()
with open(answerTable, mode="w") as targetFile:
    targetFile.write(f"{','.join(answerHeader)}\n")
    with open(answer_full) as sourceFile:
        sourceRows = csv.DictReader(sourceFile)
        for row in sourceRows:
            to_write = ""
            for row_key, row_value in row.items():
                if row_key in answerHeader:
                    to_write = f"{to_write},{row_value}"
            targetFile.write(f"{to_write[1:]}\n")