from colorama import Fore, Style, init
from constants import (
    organization_to_ror_lookup,
    API_URL_Lookup,
)
import json
import logging
import requests
from confirmed_matches import (
    confirmed_matches
)
import sys

init(autoreset=True)

# Prompts users to manually provide ROR ID for an organization if API search was not successful and didn't find a good match
def ror_manual_search(corporate_creator):
    while True:
        ror_id = input(f"\nPlease enter the {Fore.CYAN}ROR ID {Style.RESET_ALL}(either the full URL or just the ID) or type 'exit' to cancel: ").strip()
        if ror_id.lower() == 'exit':
            return None, None
        if not ror_id.startswith("https://ror.org/"):
            ror_id = "https://ror.org/" + ror_id
        ror_name = input(f"Please enter the {Fore.CYAN}ROR Display Name{Style.RESET_ALL} for your organization or type 'exit' to cancel: ").strip()
        if ror_name.lower() == 'exit':
            return None, None
        user_input_correct = input(f"You have entered the ROR ID {Fore.GREEN}{ror_id}{Style.RESET_ALL} and the ROR Display Name {Fore.GREEN}{ror_name}{Style.RESET_ALL}. Is this correct? (Y/n): ").strip().upper()
        if user_input_correct == 'N':
            retry_input = input(f"\nWould you like to retry entry? (y/n): ").strip().upper()
            if retry_input == 'N':
                return None, None
            else:
                continue
        elif user_input_correct == 'Y':
            return ror_id, ror_name

# Prompts users to manually provide ROR ID information if the API isn't working
def ror_manual_addition(corporate_creator):
    while True:
        ror_id = input(f"\nPlease enter the {Fore.CYAN}ROR ID {Style.RESET_ALL}(either the full URL or just the ID): or type 'exit' to cancel: ").strip()
        if ror_id.lower() == 'exit':
            return None, None
        if not ror_id.startswith("https://ror.org/"):
            ror_id = "https://ror.org/" + ror_id
        ror_name = input(f"Please enter the {Fore.CYAN}ROR Display Name{Style.RESET_ALL} for your organization or type exit to cancel: ").strip()
        if ror_name.lower() == 'exit':
            return None, None
        user_input_correct = input(f"You have entered the ROR ID {Fore.GREEN}{ror_id}{Style.RESET_ALL} and the ROR Display Name {Fore.GREEN}{ror_name}{Style.RESET_ALL}. Is this correct? (Y/n): ").strip().upper()
        if user_input_correct == 'N':
            retry_input = input(f"\nWould you like to retry entry? (y/n): ").strip().upper()
            if retry_input == 'N':
                return None, None
            else:
                continue
        elif user_input_correct == 'Y':
            return ror_id, ror_name
        
# Prompts user to verify the match the ROR API provided and saves the confirmed match 
def verify_match(corporate_creator, ror_id, ror_name):
    while True:
        user_input = input(f"\n\nROR would like to match {Fore.GREEN}'{corporate_creator}{Style.RESET_ALL}' to {Fore.CYAN}'{ror_name}' (ROR ID: {ror_id}){Style.RESET_ALL}. Is this a correct match? (y/N): ").strip().upper()
        if user_input == 'N':
            return False
        if user_input == 'Y':
            confirmed_matches[corporate_creator] = {"ror_id": ror_id, "ror_name": ror_name}
            return True
        else:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'Y' or 'N'.")
    

def get_ror_info(corporate_creator):
    try:
        # Check if the corporate creator exists in the dictionary
        if corporate_creator in organization_to_ror_lookup:
            logging.info(f"Picking {corporate_creator} from organization_to_ror_lookup")
            ror_id = organization_to_ror_lookup[corporate_creator]
            corporate_creator = corporate_creator.replace("United States. Department of Transportation. ", "")
            ror_name = corporate_creator
            return ror_id, ror_name
        
        # Check if the corporate creator has been confirmed before
        if corporate_creator in confirmed_matches:
            logging.info(f'Using previously confirmed match for {corporate_creator}.')
            ror_info = confirmed_matches[corporate_creator]
            return ror_info['ror_id'], ror_info['ror_name']
        
        # Query the ROR API
        API_URL = API_URL_Lookup["API_URL"]
        logging.info(f"Preparing ORG ID Request for {corporate_creator}")
        
        response = requests.get(API_URL, params={'affiliation': corporate_creator})
        logging.info(f"Org ID Response Status: {response.status_code}")
        
        if response.status_code != 200:
            logging.error(f"API request failed for '{corporate_creator}' with status code {response.status_code}.")
            ror_id, ror_name = ror_manual_addition(corporate_creator)
            if ror_id is None:
                logging.info("User canceled manual entry.")
                return None, None
            
            return ror_id, ror_name
        
        ror_data = response.json()
        
        if ror_data.get('items') is None or len(ror_data.get('items')) == 0:
            logging.error(f"Malformed ROR response for {corporate_creator}")
            ror_id, ror_name = ror_manual_addition(corporate_creator)
            if ror_id is None:
                logging.info("User canceled manual entry.")
                return None, None
            
            return ror_id, ror_name
        
        items_list = ror_data['items']
        closest_match = None
        
        for item in items_list:
            if item.get('chosen', False):
                closest_match = item
                break
        
        if closest_match is None:
            closest_match = items_list[0]
        
        logging.debug(f"My Closest Match Is: {closest_match}")
        ror_id = closest_match["organization"]['id']
        
        for name_entry in closest_match['organization'].get('names', []):
            if 'ror_display' in name_entry.get('types', []):
                ror_name = name_entry.get('value')
                logging.debug("Taking ror_display as the name {ror_name}")
                if verify_match(corporate_creator, ror_id, ror_name):
                    confirmed_matches[corporate_creator] = {
                        'ror_id': ror_id, 
                        'ror_name': ror_name
                    }
                    return ror_id, ror_name
                else:
                    ror_id, ror_name = ror_manual_search(corporate_creator)
                    if ror_id is None:
                        logging.info("User canceled manual search.")
                        return None, None
                    if verify_match(corporate_creator, ror_id, ror_name):
                        confirmed_matches[corporate_creator] = {
                            'ror_id': ror_id, 
                            'ror_name': ror_name
                        }
                        return ror_id, ror_name
                    else:
                        logging.info("User cancelled verifying match. Proceeding to manual addition")
                        ror_id, ror_name = ror_manual_addition(corporate_creator)
                        if ror_id is None:
                            logging.info("User canceled manual entry.")
                            return None, None
                        return ror_id, ror_name
        
    except Exception as e:
        logging.error(f"Error fetching ROR data for '{corporate_creator}'", e)
        sys.exit(1)
    
    return None, None

def delete_unwanted(json_obj, key):
    if key in json_obj:
        del json_obj[key]
        
        
def doi_publish(url, obj, headers):
    payload = json.dumps(obj)
    if 'doi' in obj['data']['attributes']:
        doi = obj['data']['attributes']['doi']
        return requests.put(url + '/' + doi, data=payload, headers=headers)
    else:
        return requests.post(url, data=payload, headers=headers)