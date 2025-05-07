import csv
import json


# AI written to extract variable-name pairs.
def create_mapping_dicts(csv_path):
    """
    Create bidirectional mappings between variables and labels from a CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        tuple: (variables_to_labels, labels_to_variables) dictionaries
    """
    variables_to_labels = {}
    labels_to_variables = {}

    try:
        with open(csv_path, encoding="utf-16") as file:
            csv_reader = csv.reader(file)
            # Skip header row if it exists
            next(csv_reader, None)

            for row in csv_reader:
                if len(row) >= 2:
                    variable = row[0].strip()
                    label = row[1].strip()

                    if variable and label:  # Only add non-empty pairs
                        variables_to_labels[variable] = label
                        labels_to_variables[label] = variable
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    return variables_to_labels, labels_to_variables


def save_mappings_to_json(
    variables_to_labels, labels_to_variables, output_path_prefix="mappings"
):
    """
    Save the mapping dictionaries to JSON files.

    Args:
        variables_to_labels: Dictionary mapping variables to labels
        labels_to_variables: Dictionary mapping labels to variables
        output_path_prefix: Prefix for output filenames
    """
    # Save variables to labels mapping
    with open(f"{output_path_prefix}_var_to_label.json", "w", encoding="utf-8") as f:
        json.dump(variables_to_labels, f, ensure_ascii=False, indent=2)

    # Save labels to variables mapping
    with open(f"{output_path_prefix}_label_to_var.json", "w", encoding="utf-8") as f:
        json.dump(labels_to_variables, f, ensure_ascii=False, indent=2)

    print(
        f"Mappings saved to {output_path_prefix}_var_to_label.json and {output_path_prefix}_label_to_var.json"
    )


def main():
    csv_path = "labels_encoded.csv"

    # Create the mappings
    variables_to_labels, labels_to_variables = create_mapping_dicts(csv_path)

    # Print some statistics
    print(f"Found {len(variables_to_labels)} unique variable-label pairs")

    # Display a few examples
    print("\nSample variable to label mappings:")
    sample_items = list(variables_to_labels.items())[:5]
    for var, label in sample_items:
        print(f"  {var} -> {label}")

    print("\nSample label to variable mappings:")
    sample_items = list(labels_to_variables.items())[:5]
    for label, var in sample_items:
        print(f"  {label} -> {var}")

    # Save the mappings to JSON files
    save_mappings_to_json(variables_to_labels, labels_to_variables)


if __name__ == "__main__":
    main()
