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
def load_confirmed_matches():
    if os.path.exists(confirmed_matched_ror):
        with open(confirmed_matched_ror, 'r') as f:
            return json.load(f)
    return {}

# Saves the confirmed matches to the JSON file
def save_confirmed_matches(matches):
    with open(confirmed_matched_ror, 'w') as f:
        json.dump(matches, f, indent = 4)

confirmed_matches = load_confirmed_matches

# Prompts users to manually provide ROR ID for an organization if API search was not successful and didn't find a good match
def ror_manual_entry(corporate_creator):
    ror_id = input("Please enter the ROR ID (either the full URL or just the ID): ").strip()
    if ror_id.startswith("https://ror.org/"):
        ror_id = ror_id.split('/')[-1]
    return ror_id
        
# Prompts user to verify the match the ROR API provided and saves the confirmed match 
def verify_match(corporate_creator_clean, ror_id, ror_name):
    user_input = input(f"ROR would like to match '{corporate_creator_clean}' to '{ror_name}' (ROR ID: {ror_id}). Is this a correct match? (y/n): ").strip().lower()
    if user_input == 'y':
        confirmed_matches[corporate_creator_clean] = ror_id
        save_confirmed_matches(confirmed_matches)
        return True
    return False

def get_ror_info(corporate_creator):
    # Check if the corporate creator exists in the dictionary
    if corporate_creator in organization_to_ror_lookup:
        logging.info(f"Picking {corporate_creator} from organization_to_ror_lookup")
        ror_id = organization_to_ror_lookup[corporate_creator]
        return ror_id
    
    # Check if the corporate creator has been confirmed before
    if corporate_creator in confirmed_matches:
        logging.info(f'Using previously confirmed match for {corporate_creator}.')
        return confirmed_matches[corporate_creator]
    
    # Query the ROR API
    API_URL = 'https://api.dev.ror.org/v2/organizations'
    try:
        corporate_creator_clean = corporate_creator.replace('United States. ','').strip()
        corporate_creator_clean = corporate_creator.replace('Department of Transportation. ','').strip()
        logging.info(f"Preparing ORG ID Request for {corporate_creator_clean}")
        response = requests.get(API_URL, params={'query': corporate_creator_clean})
        logging.info(f"Org ID Response Status: {response.status_code}")
        if response.status_code == 200:
            ror_data = response.json()
            if ror_data.get('items'):
                closest_match = ror_data['items'][0]
                # Extract relevant information from the API response
                ror_id = closest_match['id']
                for name_entry in closest_match.get('names', []):
                    if 'ror_display' in name_entry.get('types', []):
                        ror_name = name_entry.get('value')
                        ror_name_lang = name_entry.get('lang')
                        break # Stop after finding the first 'ror_display' name
                        # Verify the match with the user
                        if verify_match(corporate_creator_clean, ror_id, ror_name):
                            return ror_id
                        else:
                            ror_id - ror_manual_entry()
                            return ror_id
                    else:
                        logging.error(f"No items found in ROR response for {corporate_creator_clean}")
                        ror_id = ror_manual_entry()
                return ror_id, ror_name, ror_name_lang
            else:
                logging.error(f"Malformed ROR response for {corporate_creator_clean}")
                ror_id = ror_manual_entry()
                return ror_id, ror_name, ror_name_lang
        else:
            # TODO: any other status codes I need to handle?
            # TODO: in some circumstances, can I resolve this with manual entry prompting?
            
            # Handle the case when the API isn't working
            logging.error(f"API request failed for '{corporate_creator_clean}'")
            ror_id = ror_manual_entry()
    except Exception as e:
        logging.error(f"Error fetching ROR data for '{corporate_creator}': {e}")
        sys.exit(1)
    return None
