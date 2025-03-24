"""
This file should parse each column and if it is a childs question, save it.
Select options will (as in `ChildQuestion` class/SQL model) just be saved as plaintext answers.

Care must be taken for freetext options. Those seem to be generally indicated by a "_" or "_01" affix to the question,
e.g.:

FE03 <-- will be a code-mapped answer
FE03_01 <-- optional freetext answer (when present, overwrites the code-mapped answer)

They are also easy to tell apart because the "Type" will be "TEXT" not "ORDINAL". e.g.

FE01 <-- ORDINAL (e.g. 1, 2, 3, 4, 5, 6, 7 -9) (where these are mapped to 1 = Deutschland, 2 = Sweden, usw).
FE01_031 <-- TEXT (e.g. "Frankreich")

"""

"""
Import is_milestone(row) from `import_milestones_metadata` and exclude all those plus TIME ones, and then lastly exclude
the ones we use already for importing base children (e.g. birth year)


Try and assign every other ordinal/text column as a Question to Children as custom questions about children.

"""


"""
Important to ask Igor: FE01 and FK01 are both "Birth year". Is FK01 from the parent? Which parent?
It is just labelled birth year.

FE01 has more recent years (up to 2025), while FK01 only has at latest 2010.

"""
