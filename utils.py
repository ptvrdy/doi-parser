from constants import (
    organization_to_ror_lookup,
    confirmed_matched_ror,
)
import json
import logging
import os
import requests
import sys

# Load confirmed user matches from the JSON file if it already exists
# TODO: do CSV or something instead writing straight to the PY file
def load_confirmed_matches():
    if os.path.exists(confirmed_matched_ror):
        with open(confirmed_matched_ror, 'r') as f:
            return json.load(f)
    return {}

# Saves the confirmed matches to the JSON file
def save_confirmed_matches(matches):
    with open(confirmed_matched_ror, 'w') as f:
        json.dump(matches, f, indent = 4)

# Load confirmed matches
confirmed_matches = load_confirmed_matches()

# Prompts users to manually provide ROR ID for an organization if API search was not successful and didn't find a good match
def ror_manual_search(corporate_creator):
    ror_id = input("Please enter the ROR ID (either the full URL or just the ID): ").strip() # TODO: how do i back out of this???
    if ror_id.startswith("https://ror.org/"):
        ror_id = ror_id.replace("https://ror.org/", "") # ror_id.split('/')[-1]
    ror_name = input("Please enter the ROR Display Name for your organization: ").strip()
    ror_lang = input("Please enter the ROR language for your organization: ").strip()
    return ror_id, ror_name, ror_lang

# Prompts users to manually provide ROR ID information if the API isn't working
def ror_manual_addition(corporate_creator):
    while True:
        ror_id = input("Please enter the ROR ID (either the full URL or just the ID): ").strip()
        if not ror_id.startswith("https://ror.org/"):
            ror_id = "https://ror.org/" + ror_id
        ror_name = input("Please enter the ROR Display Name for your organization: ").strip()
        ror_lang = input("Please enter the ROR language for your organization: ").strip()
        user_input = input(f'You have entered the ROR ID or {ror_id}, the ROR Display Name of {ror_name} and the language of {ror_lang}. Is this correct? (Y/n): ').strip().upper() # TODO: what if they don't want to confirm or deny?
        
        if user_input == 'N':
            retry_input =(f'Would you like to retry entry? (y/n): ').strip().upper
            if retry_input != 'Y':
                return None, None, None
        else:
            return ror_id, ror_name, ror_lang   
    
        
# Prompts user to verify the match the ROR API provided and saves the confirmed match 
def verify_match(corporate_creator_clean, ror_id, ror_name, ror_lang):
    user_input = input(f"ROR would like to match '{corporate_creator_clean}' to '{ror_name}' (ROR ID: {ror_id}). Is this a correct match? (y/N): ").strip().upper() # TODO: inconsistent with other ROR ID Y/N prompt
    if user_input == 'Y':
        confirmed_matches[corporate_creator_clean] = {"ror_id": ror_id, "ror_name": ror_name, "ror_lang": ror_lang}
        save_confirmed_matches(confirmed_matches)
        return True
    return False

def get_ror_info(corporate_creator):
    # Check if the corporate creator exists in the dictionary
    if corporate_creator in organization_to_ror_lookup:
        logging.info(f"Picking {corporate_creator} from organization_to_ror_lookup")
        ror_id = organization_to_ror_lookup[corporate_creator][1]
        ror_name = corporate_creator
        ror_lang = organization_to_ror_lookup[corporate_creator][2]
        return ror_info['id'], ror_info['name'], ror_info['lang']
    
    # Check if the corporate creator has been confirmed before
    if corporate_creator in confirmed_matches:
        logging.info(f'Using previously confirmed match for {corporate_creator}.')
        ror_info = confirmed_matches[corporate_creator]
        return ror_info['id'], ror_info['name'], ror_info['lang']
    
    # Query the ROR API
    API_URL = 'https://api.dev.ror.org/v2/organizations' # TODO: this belongs in a constants file
    try:
        corporate_creator_clean = corporate_creator.replace('United States. ','').strip()
        corporate_creator_clean = corporate_creator.replace('Department of Transportation. ','').strip()
        logging.info(f"Preparing ORG ID Request for {corporate_creator_clean}")
        response = requests.get(API_URL, params={'query': corporate_creator_clean})
        logging.info(f"Org ID Response Status: {response.status_code}")
        # TODO: de-hadouken this if desired
        if response.status_code == 200:
            ror_data = response.json()
            if ror_data.get('items'):
                closest_match = ror_data['items'][0]
                # Extract relevant information from the API response
                ror_id = closest_match['id']
                for name_entry in closest_match.get('names', []):
                    if 'ror_display' in name_entry.get('types', []):
                        ror_name = name_entry.get('value')
                        ror_lang = name_entry.get('lang')
                        # Verify the match with the user
                        if verify_match(corporate_creator_clean, ror_id, ror_name, ror_lang):
                            confirmed_matches[corporate_creator_clean] = {
                                'id': ror_id, 
                                'name': ror_name, 
                                'lang': ror_lang
                            }
                            save_confirmed_matches(confirmed_matches)
                        else:
                            ror_id, ror_name, ror_lang = ror_manual_search(corporate_creator_clean)
                            return ror_id, ror_name, ror_lang
                    else:
                        logging.error(f"No items found in ROR response for {corporate_creator_clean}")
                        ror_id, ror_name, ror_lang = ror_manual_search(corporate_creator_clean)
                        return ror_id, ror_name, ror_lang
            else:
                logging.error(f"Malformed ROR response for {corporate_creator_clean}")
                ror_id, ror_name, ror_lang = ror_manual_addition(corporate_creator)
                return ror_id, ror_name, ror_lang
        else:
            # Handle the case when the API isn't working
            logging.error(f"API request failed for '{corporate_creator_clean}' with status code {response.status_code}.")
            ror_id, ror_name, ror_lang = ror_manual_addition(corporate_creator)
            return ror_id, ror_name, ror_lang
    except Exception as e:
        logging.error(f"Error fetching ROR data for '{corporate_creator}': {e}")
        sys.exit(1)
    return None, None, None
