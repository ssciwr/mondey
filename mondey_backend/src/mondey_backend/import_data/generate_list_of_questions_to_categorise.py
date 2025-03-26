import pandas as pd

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
