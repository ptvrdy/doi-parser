import codecs
from colorama import Fore, Back, init
from confirmed_matches import (
    save_confirmed_matches,
    confirmed_matches
)
import constants
import csv
import json
import logging
from post_processes import *
import requests
import sys
import traceback
from utils import (
	doi_publish
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARN)

logging.basicConfig(handlers=[stream_handler],
					level=logging.INFO,
                    format=constants.LOG_FORMAT)

init(autoreset=True)

# DOI Prefix for the testing environment
doi_prefix = "10.21949"

# this is where your input csv is read, each row is equal to 1 DOI record/request
def read_csv_file(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        rows = [row[0].strip() for row in csv_reader if row]
    return rows

# unit test work is a work in progress. not currently running
def unit_test():
	try:
		with open('Version 2.0 unit test/unit test input.csv', 'r', encoding='utf-8') as csv_fp:
			csv_reader = csv.reader(csv_fp)
			with open('Version 2.0 unit test/unit test output.json', 'r', encoding='utf-8') as json_fp:
				expected_output = json.load(json_fp)

				test_output = do_post_process(csv_to_json(csv_reader))

				assert expected_output == test_output, "Test failed: Output does not match expected output"

	except AssertionError as e:
		logging.error(f"Assertion error: {e}")
		logging.error(f"Expected Output: {json.dumps(expected_output, indent=2)}")
		logging.error(f"Actual Output: {json.dumps(test_output, indent=2)}")
		raise e
	except Exception as e:
		logging.error(f"An error occurred during unit testing: {e}")
		traceback.print_exception(e, limit=5)
		raise e

#this function converts the csv file to json
def csv_to_json(csv_reader):
    output = []
    header_row = True
    keys = {}

    for row in csv_reader:
        if header_row:
            logging.info("=> Parsing CSV")
            row[0] = row[0].strip(codecs.BOM_UTF8.decode('utf-8'))
            keys = {i: row[i].strip() for i in range(len(row)) if row[i].strip()}
            header_row = False
            continue
        
        output_obj = {}
        for i in range(len(keys)):
            key = keys[i]
            element = row[i].strip() if i < len(row) else ''
            if element:
                output_obj[key] = element
        
        if output_obj:
            output.append(output_obj)
    
    return output

    

def main():
	#unit_test()

	# if user forgets to say which CSV to read for input
	if len(sys.argv) != 2:
		file_handler = logging.FileHandler('default_process.log')
		logging.getLogger().addHandler(file_handler)
		file_handler.setLevel(logging.INFO)
		logging.error(f"{Fore.RED}Error: Please provide a filename")
		sys.exit(1)
  
	# this changes the log names so that it is named after the input file and not a generic file name that will be overwritten
	log_filename = sys.argv[1].rstrip('csv') + 'log'
	local_file_handler = logging.FileHandler(log_filename)
	local_file_handler.setLevel(logging.INFO)
	local_file_handler.setFormatter(logging.Formatter(constants.LOG_FORMAT))
	logging.getLogger().addHandler(local_file_handler)
  
	try:
		print(f"{Back.WHITE}{Fore.GREEN}\n===============================================================================================================")
		print(f"{Back.WHITE}{Fore.GREEN}         Welcome to DOI Parser!                                                                                ")
		print(f"{Back.WHITE}{Fore.GREEN}===============================================================================================================")
		logging.info(f"====> Starting File Read: {sys.argv[1]}")
		print(f"{Fore.YELLOW}\n\n====> Starting File Read: {sys.argv[1]}")
		with open(sys.argv[1], 'r', encoding='utf-8') as fp:
			csv_reader = csv.reader(fp)
			output = csv_to_json(csv_reader)

		# this initializes post_processes.py
		output = do_post_process(output)
		print(f"{Fore.YELLOW}\n\n\n\n====> Now beginning transformation processes...")
		print(f"\n====> Now Reviewing ROR Info...")
		print(f"\n===============================================================================================================")
		
		
  		# this saves any confirmed matches to the confirmed matches csv at the end of the post_processes
		save_confirmed_matches(confirmed_matches)
		
		# this prints the 1st individual item of the CSV in the JSON DataCite schema to spot any errors you might have made/check the structure
		logging.info("====> Finished Parsing\n")
		print(f"{Fore.YELLOW}\n\n\n====> Finished Parsing\n")
		print(json.dumps(output[0], indent=2))
		should_continue = input(f"{Fore.CYAN}\n====> Does the above look good? [y/N]: ").upper() == 'Y'

		if not should_continue:
			print(f"{Fore.RED}Aborting...")
			sys.exit(2)

		# this gets the file names so that the API entire response can be record and the DOIs/Titles can be recorded in a CSV
		out_filename_json = sys.argv[1].rstrip('csv') + 'json'
		out_filename_dois_csv = sys.argv[1].replace('.csv', '') + "_doi_results.csv"
		logging.info(f"{Fore.YELLOW}\n\n====> Starting Output Write: %s " % out_filename_json)
		print(f"{Fore.YELLOW}\n\n====> Starting Output Write: %s " % out_filename_json)
		logging.info(f"{Fore.YELLOW}\n\n====> Starting Output Write: %s " % out_filename_dois_csv)
		print(f"{Fore.YELLOW}\n\n====> Starting Output Write: %s " % out_filename_dois_csv)
		
		fpo = open(out_filename_json, 'w')
		csv_file =  open(out_filename_dois_csv, 'w', newline='', encoding='utf-8')
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow(['DOI', 'Title'])  # Write the header row
   
		json.dump(output, fpo, indent=2)

		# Ask users if they would like to post the request to the DataCite API
		should_continue = input(f"{Fore.CYAN}\n\n====> Do you want to send the request now? [y/N]: ").upper() == 'Y'

		if not should_continue:
			logging.info(f"{Fore.GREEN}\n====> Done !")
			print(f"{Fore.GREEN}\n====> Done !")
			sys.exit(0)

		url = "https://api.datacite.org/dois/"
  
		# Read basic authentication from config.txt
		with open("config.txt", "r", encoding='utf-8') as config_file:
			config_lines = config_file.readlines()
			basic = ""
			for line in config_lines:
				if line.startswith("Basic"):
					basic = line.split(" ")[1].strip()
		if not basic:
			logging.error(f"{Fore.RED}Authentication not found in config.txt")
			print(f"{Fore.RED}Authentication not found in config.txt")
			sys.exit(1)
	

		headers = {
			"content-type": "application/json",
			"User-Agent": "doi_parser.py/2.0 (https://github.com/ptvrdy/doi-parser; mailto:peyton.tvrdy.ctr@dot.gov)",
			"authorization": "Basic " + basic
		}
  
		for obj in output:
			logging.info(f"\n====> Preparing Request")
			print(f"\n====> Preparing Request")

			logging.debug(f"{headers}")

			logging.info(f"{Fore.YELLOW}===> Sending Request")
			response = doi_publish(url, obj, headers)

			logging.info("====> Handling Response: {response.status_code}")
			if response.status_code // 100 != 2:
				logging.debug(f"{Fore.RED}====> POST did not fire successfully! {response.status_code}")
				print(f"{Fore.RED}====> POST did not fire successfully! {response.status_code}. Please read the log file to debug.")
				logging.debug(f"The json response body is {response.json()}")
			else:
				logging.info(f"{Fore.YELLOW}====> Writing DOIs and Titles to {out_filename_dois_csv}")
				print(f"{Fore.YELLOW}====> Writing DOIs and Titles to {out_filename_dois_csv}")
				data = response.json()
    
				# Access the attributes
				attributes = data.get('data').get('attributes', {})

				# Retrieve the id and titles from attributes
				doi_id = attributes.get('doi', 'No ID')  # Use a default value if 'id' is not found
				titles = attributes.get('titles', [])


				# Process the titles
				title = None  # Initialize title variable
				for response_title in titles:
					if 'titleType' not in response_title:
						title = response_title['title']
						break  # Break if you want only the first title without 'titleType'

				if title:  # Only write if title is found
					logging.info(f"{Fore.YELLOW}====> Writing DOIs and Titles to {out_filename_dois_csv}")
					csv_writer.writerow(["https://doi.org/" + doi_id, title])
				else:
					logging.warning(f"{Fore.RED}====> No suitable title found for DOI {doi_id}")

			with open(out_filename_json, 'a', encoding='utf-8') as fpo:
				logging.info(f"{Fore.YELLOW}====> Writing Response to JSON file {out_filename_json}")
				fpo.write("\n\n---------------------------------------------------------------------------------\n\nRESULTS\n\n")
				# fpo.write(f"\n{doi['id']},{doi['title']}")
				json.dump(response.json(), fpo, indent=2)

		csv_file.close()
		
		logging.info(f"{Fore.GREEN}====> Done !")
		print(f"{Fore.GREEN}====> Done !")
   
	except Exception as e:
		logging.error(f"{Fore.RED}An error occurred: {e}")
		traceback.print_exception(e)
		sys.exit(1)

def do_post_process(output):
	for func in (delete_unwanted_columns,
     		# High Priority Runs
			rosap_url,
			sm_Collection,
			handle_draft_vs_publish,
			title,
			alt_title,
			publication_date,
			resource_type,
			contracting_officer,
			creators,
			lambda x: process_corporate_field(x, "sm:Corporate Creator"),
			lambda x: process_corporate_field(x, "sm:Corporate Contributor"),
			lambda x: process_corporate_field(x, "sm:Corporate Publisher"),
   			series,
			# Lower Priority Runs
			contributors,
			keywords,
			report_number,
			contract_number,
			researchHub_id,
			content_notes,
   			workroom_id,
			rosap_id,
   			rights,
			language,
			edition,
			description,
   			schema,
			drop_and_pop,
      		wrap_object):

		output = func(output)
	return output
 

if __name__ == '__main__':
	main()