import pandas as pd

"""
This file is NOT involved in the import process. It just helps us to generate a .csv so we can collaborate and understand
what properties/where questions should be stored.

Only the child/parent questions should be generated here, not mielstones.
"""

"""
Them motivation for the columns is things like that FE01 and FK01 are both "Birth year".
Is FK01 from the parent? Which parent?
It is just labelled birth year.

FE01 has more recent years (up to 2025), while FK01 only has at latest 2010. So it's more clear, but not always.

Then, some questions are required to have answers. We track that this way too.

"""

# Read the CSV file
df = pd.read_csv("labels_encoded.csv", encoding="UTF-16")

# 1. After row 168 (since that's when milestones end)
# 2. Unique questions
# 3. Not containing "TIME"
filtered_df = df.loc[
    (df.index > 170) & (df.index < 396), ["Variable", "Variable Label"]
].drop_duplicates(subset="Variable Label")
filtered_df = filtered_df[(~filtered_df["Variable"].str.contains("TIME", case=False))]

# Note this is hardcoded to the export from late March, 2025.
# If additional questions are added and row indexes of milestones change, then these limits need to change too.
# In the current data the meta questions are all together in one fragment: 170-396.
# The rest is milestones (before and after), required data, time data, and survey page data.

unwanted_vars = ["MISSING", "MISSREL", "MAXPAGE", "LASTPAGE"]
filtered_df = filtered_df[~filtered_df["Variable"].isin(unwanted_vars)]

# Create a dataframe for the output
output_df = pd.DataFrame(
    {
        "variable": filtered_df["Variable"],
        "question": filtered_df["Variable Label"],
        "isRequired": "",
        "isToParent": "",
    }
)

# Create a dataframe for the output

# Save to CSV
output_df.to_csv("questions.csv", index=False)

print("Questions extracted and saved to questions.csv")
print("\nPreview of extracted questions:")
print(output_df)
