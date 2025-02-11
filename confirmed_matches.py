import csv
import logging
import os

# Load confirmed user matches from the CSV file if it already exists
def load_confirmed_matches():
    confirmed_matches = {}
    csv_file = "confirmed_matched_ror.csv"
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                confirmed_matches[row['rosap_name']] = {"ror_id": row['ror_id'], 'ror_name':row['ror_name']}

    return confirmed_matches

# Saves the confirmed matches to the JSON file
def save_confirmed_matches(matches):
    try:
        csv_file = "confirmed_matched_ror.csv"
        with open(csv_file, 'w', newline='') as f:
            fieldnames = ["rosap_name", "ror_id", "ror_name"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for rosap_name, ror_entries, in matches.items():
                ror_id = ror_entries['ror_id']
                ror_name = ror_entries['ror_name']
                writer.writerow({"rosap_name":rosap_name, "ror_id": ror_id, "ror_name": ror_name})
    except IOError as e:
        logging.warning(f"Unable to write 'confirmed_matched_ror.csv' due to {e}")

# Load confirmed matches
confirmed_matches = load_confirmed_matches()