from constants import (
    organization_to_ror_lookup,
    API_URL_Lookup,
)
import csv
import logging
import os
import requests
import sys

# Load confirmed user matches from the CSV file if it already exists
def load_confirmed_matches():
    confirmed_matches = {}
    csv_file = "confirmed_matched_ror.csv"
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ror_id = row["ror_id"]
                ror_name = row["ror_name"]
                confirmed_matches[ror_name] = (ror_id)
    return confirmed_matches

# Saves the confirmed matches to the JSON file
def save_confirmed_matches(matches):
    csv_file = "confirmed_matched_ror.csv"
    with open(csv_file, 'w', newline='') as f:
        fieldnames = ["ror_id", "ror_name"]
        writer = csv.DictWriter(f, fieldnames-fieldnames)
        writer.writeheader()
        for ror_id, ror_name, in matches.items():
            writer.writerow({"ror_id": ror_id, "ror_name": ror_name})

# Load confirmed matches
confirmed_matches = load_confirmed_matches()

# Prompts users to manually provide ROR ID for an organization if API search was not successful and didn't find a good match
def ror_manual_search(corporate_creator):
    while True:
        ror_id = input("Please enter the ROR ID (either the full URL or just the ID) or type 'exit' to cancel: ").strip()
        if ror_id.lower() == 'exit':
            return None, None, None
        if ror_id.startswith("https://ror.org/"):
            ror_id = ror_id.replace("https://ror.org/", "")
        ror_name = input("Please enter the ROR Display Name for your organization or type 'exit' to cancel: ").strip()
        if ror_name.lower() == 'exit':
            return None, None, None
        return ror_id, ror_name

# Prompts users to manually provide ROR ID information if the API isn't working
def ror_manual_addition(corporate_creator):
    while True:
        ror_id = input("Please enter the ROR ID (either the full URL or just the ID): or type 'exit' to cancel: ").strip()
        if ror_id.lower() == 'exit':
            return None, None, None
        if not ror_id.startswith("https://ror.org/"):
            ror_id = "https://ror.org/" + ror_id
        ror_name = input("Please enter the ROR Display Name for your organization or type exit to cancel: ").strip()
        if ror_name.lower() == 'exit':
            return None, None, None
        user_input_correct = input(f'You have entered the ROR ID {ror_id} and the ROR Display Name {ror_name}. Is this correct? (Y/n): ').strip().upper()
        if user_input_correct == 'N':
            retry_input = input('Would you like to retry entry? (y/n): ').strip().upper()
            if retry_input != 'N':
                return None, None, None
            else:
                continue
        elif user_input_correct == 'Y':
            return ror_id, ror_name
        
# Prompts user to verify the match the ROR API provided and saves the confirmed match 
def verify_match(corporate_creator_clean, ror_id, ror_name):
    while True:
        user_input = input(f"ROR would like to match '{corporate_creator_clean}' to '{ror_name}' (ROR ID: {ror_id}). Is this a correct match? (y/N): ").strip().upper()
        if user_input == 'N':
            return False
        if user_input == 'Y':
            confirmed_matches[corporate_creator_clean] = {"ror_id": ror_id, "ror_name": ror_name}
            save_confirmed_matches(confirmed_matches)
            return True
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
    

def get_ror_info(corporate_creator):
    # Check if the corporate creator exists in the dictionary
    if corporate_creator in organization_to_ror_lookup:
        logging.info(f"Picking {corporate_creator} from organization_to_ror_lookup")
        ror_id = organization_to_ror_lookup[corporate_creator][1]
        corporate_creator = corporate_creator.replace("United States. Department of Transportation. ", "")
        ror_name = corporate_creator
        return ror_info['id'], ror_info['name']
    
    # Check if the corporate creator has been confirmed before
    if corporate_creator in confirmed_matches:
        logging.info(f'Using previously confirmed match for {corporate_creator}.')
        ror_info = confirmed_matches[corporate_creator]
        return ror_info['id'], ror_info['name']
    
    # Query the ROR API
    API_URL = API_URL_Lookup["API_URL"]
    try:
        corporate_creator_clean = corporate_creator.replace('United States. ','').strip()
        corporate_creator_clean = corporate_creator.replace('Department of Transportation. ','').strip()
        logging.info(f"Preparing ORG ID Request for {corporate_creator_clean}")
        response = requests.get(API_URL, params={'affiliation': corporate_creator_clean})
        logging.info(f"Org ID Response Status: {response.status_code}")
        
        if response.status_code != 200:
            # Handle the case when the API isn't working
            logging.error(f"API request failed for '{corporate_creator_clean}' with status code {response.status_code}.")
            ror_id, ror_name = ror_manual_addition(corporate_creator)
            if ror_id is None:
                logging.info("User canceled manual entry.")
                return None, None, None
            return ror_id, ror_name
        
        if response.status_code == 200 and ror_data.get('items') is None: 
            logging.error(f"Malformed ROR response for {corporate_creator_clean}")
            ror_id, ror_name = ror_manual_addition(corporate_creator)
            if ror_id is None:
                logging.info("User canceled manual entry.")
                return None, None, None
            return ror_id, ror_name
        
        if response.status_code == 200 and ror_data.get('items') is None: 
            logging.error(f"Malformed ROR response for {corporate_creator_clean}")
            ror_id, ror_name = ror_manual_addition(corporate_creator)
            if ror_id is None:
                logging.info("User canceled manual entry.")
                return None, None, None
            return ror_id, ror_name
        
        ror_data = response.json()
        if ror_data.get('items'):
            items_list = ror_data['items']
            for item in items_list:
                if item.get('chosen') == True:
                    closest_match = item
                    break
            if closest_match is None:
                closest_match = ror_data['items'][0]
            if not ror_id.startswith("https://ror.org/"):
                ror_id = "https://ror.org/" + ror_id
            # Extract relevant information from the API response
            ror_id = closest_match['id']
            for name_entry in closest_match.get('names', []):
                if 'ror_display' in name_entry.get('types', []):
                    ror_name = name_entry.get('value')
                    # Verify the match with the user
                    if verify_match(corporate_creator_clean, ror_id, ror_name):
                        confirmed_matches[corporate_creator_clean] = {
                            'id': ror_id, 
                            'name': ror_name
                        }
                        save_confirmed_matches(confirmed_matches)
                        return ror_id, ror_name
                    else:
                        ror_id, ror_name = ror_manual_search(corporate_creator_clean)
                        if ror_id is None:
                            logging.info("User canceled manual search.")
                            return None, None, None
                        if verify_match(corporate_creator_clean, ror_id, ror_name):
                            confirmed_matches[corporate_creator_clean] = {
                            'id': ror_id, 
                            'name': ror_name
                        }
                            save_confirmed_matches(confirmed_matches)
                            return ror_id, ror_name
                        else:
                            logging.info("User cancelled verifying match. Proceeding to manual addition")
                            ror_id, ror_name = ror_manual_addition(corporate_creator_clean)
                            if ror_id is None:
                                logging.info("User canceled manual entry.")
                                return None, None, None
                            return ror_id, ror_name
    except Exception as e:
        logging.error(f"Error fetching ROR data for '{corporate_creator}': {e}")
        sys.exit(1)
    return None, None, None
