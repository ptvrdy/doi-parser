import csv
import logging
import os

# Load confirmed user matches from the CSV file if it already exists
def load_confirmed_matches():
    confirmed_matches = {}
    csv_file = "confirmed_matched_ror_with_affiliations.csv"
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                confirmed_matches[row['rosap_name']] = {
                    "ror_id": row['ror_id'], 
                    'ror_name':row['ror_name'],
                    "affiliation_ror_id": row.get('affiliation_ror_id', '').strip(),
                    "affiliation_ror_name": row.get('affiliation_ror_name', '').strip()
                    }
    return confirmed_matches

# Saves the confirmed matches to the JSON file
def save_confirmed_matches(matches):
    try:
        csv_file = "confirmed_matched_ror_with_affiliations.csv"
        with open(csv_file, 'w', newline='') as f:
            fieldnames = ["rosap_name", "ror_id", "ror_name", "affiliation_ror_id", "affiliation_ror_name"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for rosap_name, ror_entries in matches.items():
                writer.writerow({
                    "rosap_name": rosap_name,
                    "ror_id": ror_entries.get("ror_id", ""),
                    "ror_name": ror_entries.get("ror_name", ""),
                    "affiliation_ror_id": ror_entries.get("affiliation_ror_id", ""),
                    "affiliation_ror_name": ror_entries.get("affiliation_ror_name", "")
                })
    except IOError as e:
        logging.warning(f"Unable to write 'confirmed_matched_ror_with_affiliations.csv' due to {e}")

# Load confirmed matches
confirmed_matches = load_confirmed_matches()
rejection_list = []