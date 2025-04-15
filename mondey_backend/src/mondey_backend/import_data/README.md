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
- Run the migration `migration.sql` to add the "name" field to milestones. It signifies presently, that a milestone was
matched to imported data from a CSV. To do this, you'll need to first have the
database, so I suggest running python3 -m import_milestones_metadata.py, which will fail because of the migration being
missing, then running the migration manually, then running import_milestones_meta again to check it now works (so that
you apply the migration to the right database)
- Run `import_all.py` once you have the four CSV data files in this directory(three from the researchers in one batch,
then the other with later, further details), and your "current" database (so within *this* directory)
 will contain the imported milestones/children/answers and data for those once it finishes, by updating existing milestones.
- Then change your DB settings to explore the "current_db" in the UI or by a local database connector tool.
- If satisfied, take a back up of the live "/db" files (both mondey.db and user.db), and paste the current_mondey.db and
current_users.db files into that directory, renaming them to remove the "current_" prefix, to update the live data!

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

## The delinetion between importing and correction.
The import scripts always load in actual data from CSVs.

The correction scripts change the (valid) psychology format data into a more sensible data format for our system
(where compatibility is needed), and often a more consolidated, numerical "flattened" form. For example, if a question
had free text answers with two values like "Pregnancy Duration + Incubator period": "34+2", "38", "40", "32,3", then the correction changes
this into two separate questions.
