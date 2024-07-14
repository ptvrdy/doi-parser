import codecs
import csv
import sys
import json
import logging
import requests
from post_processes import *

logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler('default_process.log')],
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s')

# DOI Prefix for the testing environment
doi_prefix = "10.80510"

def read_csv_file(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        rows = [row[0].strip() for row in csv_reader if row]
    return rows

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
	unit_test()

	if len(sys.argv) != 2:
		logging.error("Error: Please provide a filename")
		handlers= logging.StreamHandler(), logging.FileHandler('system_failure_process.log')
		logging.getLogger().addHandler(handlers)
		sys.exit(1)
  
	log_filename = sys.argv[1].rstrip('csv') + 'log'
	logging.getLogger().addHandler(logging.FileHandler(log_filename))
  
	try:
		logging.info(f"=> Starting File Read: {sys.argv[1]}")
		with open(sys.argv[1], 'r', encoding='utf-8') as fp:
			csv_reader = csv.reader(fp)
			output = csv_to_json(csv_reader)

		
		output = do_post_process(output)
				
		logging.info("=> Finished Parsing\n")
		print(json.dumps(output[0], indent=2))
		should_continue = input("\n=> Does the above look good? [y/N]: ").upper() == 'Y'

		if not should_continue:
			print("Aborting...")
			sys.exit(2)

		out_filename = sys.argv[1].rstrip('csv') + 'json'
		logging.info("=> Starting Output Write: %s " % out_filename)
		
		fpo = open(out_filename, 'w')
		json.dump(output, fpo, indent=2)

		# Ask users if they would like to post the request to the DataCite API
		should_continue = input("\n=> Do you want to send the request now? [y/N]: ").upper() == 'Y'

		if not should_continue:
			logging.info("=> Done !")
			sys.exit(0)

		logging.info("=> Preparing Request")

		url = "https://api.test.datacite.org/dois"
		payload = json.dumps(output)

		# Read username and password from config.txt
		with open("config.txt", "r", encoding='utf-8') as config_file:
			config_lines = config_file.readlines()
			username = ""
			password = ""
			for line in config_lines:
				if line.startswith("username"):
					username = line.split("=")[1].strip()
				elif line.startswith("password"):
					password = line.split("=")[1].strip()

		if not username or not password:
			logging.error("Username or password not found in config.txt")
			sys.exit(1)

		# Encode username and password for Basic Authentication
		auth_header = codecs.encode(f"{username}:{password}", 'ascii').decode().replace('\n', '')

		headers = {
			'Authorization': 'Basic ' + auth_header,
			'Content-Type': 'application/vnd.api+json',
		}

		logging.info("=> Sending Request")
		response = requests.post(url, headers=headers, data=payload)

		logging.info("=> Handling Response: {response.status_code}")
		if response.status_code != 200:
			logging.error("=> POST did not fire successfully! {response.status_code}")
		else:
			with open(out_filename, 'a', encoding='utf-8') as fpo:
				logging.info("=> Writing Response to file")
				fpo.write('\n\n---------------------------------------------------------------------------------\n\nRESULTS\n\n')
				json.dump(response.json(), fpo, indent=2)
			logging.info("=> Done !")
   
	except Exception as e:
		logging.error(f"An error occurred: {e}")
		sys.exit(1)

def do_post_process(output):
	for func in (delete_unwanted_columns,
     		workroom_id,
			rosap_id,
			rosap_url,
			sm_Collection,
			sm_digital_object_identifier,
			title,
			alt_title,
			publication_date,
			resource_type,
			creators,
			lambda x: process_corporate_field(x, "sm:Corporate Creator"),
			lambda x: process_corporate_field(x, "sm:Corporate Contributor"),
			lambda x: process_corporate_field(x, "sm:Corporate Publisher"),
			contributors,
			keywords,
			report_number,
			contract_number,
			researchHub_id,
			content_notes,
			language,
			edition,
			series,
			description,
   			schema,
      		wrap_object):

		output = func(output)
	return output
 

if __name__ == '__main__':
	main()