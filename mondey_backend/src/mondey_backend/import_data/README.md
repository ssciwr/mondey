# Importing

## About
This script allows us to bulk import data on children, milestones, and to what level those children have achieved
 those milestones. It also imports questions answered about the children/parents which are in the SoSci data.
The labels and mapped values are in German.

## Input: CSV data files
Variables.csv (adjust in utils.py): the milestones meta data, like their IDs, and title.
Data.csv: the data on what values to save for milestone achievement, and question answers.
Coding.csv: (exported from xlsx): this is used to generate the questions meta data themselves and answer options.

## Practical Use
Run import_all.py once you have the three CSV data files in this directory, and your test database (so within *this* directory)
 will contain the imported milestones/children/answers and data for those.

### How to get the CSV files
Export them from SoSCi. The columns must be the same and the script can dynamically deal with additional fields, but
it will default to make assumptions (e.g. that a select-based question answer on a child row is a "question about the child",
not about the parent.). You can overwrite import_childrens_questions_answers_data.py parent_questions to change this,
and make the questions be about the Beobachter/parent".

## Design
The import process is split across several files, which can be run individually as a CLI. These handle importing each CSV
file part. The import_all.py script deals with processing all of them.

Each file, including import_all.py, has tests to make sure they correctly imported the data.

## Tests/data samples
The tests mainly assert data has been mapped correctly and small fine parts worked correctly (e.g. group full names from
acronym look up keys)
