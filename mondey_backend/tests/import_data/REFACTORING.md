# Refactoring that would be good to do:

## Summary
My notes because the code has changed a fair amount and these changes could be relevant(but may not be worth doing now)
The answer saving code is slightly tricky to understand, because to get the actual "plain text" answer from the data,
you need to look up a response code sometimes, and sometimes use the raw data etc. I have labelled that as "response_label"
in the code - this could be a bit clearer perhaps.

The hardcoded parts are defined in the hardcoded_additional_data_answers.py file which handles directly saving additional
data to the right question answers as User/Child answers.

## Correctly identify which child_ids are actual child.id values and which are the CASE IDs from the data import
E.g.
```
def get_childs_parent_id(session: Session, child_id: int) -> int:
```
Originally this genuinely took the child ID. However, now, it takes the childs CASE name, which then must look up by
email for the right child to find their parent.

So the argument should because case_id.

As it can be confusing to the reader of this code in the future - child_id is misleading when it is the CASE ID and not
the actual child.id variable.

## Avoid importing the import_session in small utility functions - either pass it as an arg or dependency inject it
Right now in order to have a separate DB for the import process, we use a local directory and session. But importing
it this way is not ideal.

## Pass the data around as a dataframe between functions, rather than reading from the same data_path CSVs
This way of doing things means we do data deduplication by modifying the actual CSV before the script runs;
this is reliable but not ideal

## Consolidate the functionality which is linked together, maybe into a Python class, rather than having these files

## Remove obsolete postprocessing code and other files

## Consolidate import_all.py with await align_additional_data_to_current_answers.py to be one script, rather than two
Because right now they do similar things and overlap in terms of code. They could each become one function in a 
Python class for managing processing import data e.g. `initialize` or `run`

## Refactor import_childrens_question_answers_data.py
IMO this is high priority alongside handling the child id/case ID better.
- It should become two files:
- One for creation initial questions from the labels CSV (only on initial first import) and
- One for importing answers to the (pre-existing, just created) children

## Remove all the extra print statements
mostly for debug between user vs child question answers etc.

## Move soem of the valid CSV validation out of the routers file / controller 

## In routers/research.py, improve the path solution/decide where to git commit the labels encoded and questions_specificed CSVs (but not actual data)