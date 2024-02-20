import codecs
import csv
import sys
import json
import requests
	
def unit_test():
	csv_fp = open('test/unit test input.csv', 'r', encoding='utf-8')
	json_fp = open('test/unit test output.json', 'r', encoding='utf-8')

	expected_output = json.load(json_fp)

	test_output = post_process_output(csv_to_json(csv.reader(csv_fp)))

	csv_fp.close()
	json_fp.close()

	try:
		assert expected_output == test_output
	except AssertionError as e:
		print("Expected Output:", expected_output)
		print("Actual Output:", test_output)
		raise e

def csv_to_json(csv_reader):
	output = []
	header_row = True
	keys = {}

	for row in csv_reader:
		if header_row:
			print("=> Parsing CSV")
			row[0] = row[0].strip(codecs.BOM_UTF8.decode(sys.stdin.encoding))
			keys = {i:row[i].strip() for i in range(len(row)) if row[i] != ''}
			
			header_row = False
			continue

		output_obj = {}
		for i in range(len(keys)):
			
			key = keys[i]
			element = row[i]

			if element != ''.strip():
				output_obj[key] = element
		
		if output_obj != {}:
			output.append(output_obj)

	return output

def post_process_output(json_list):
	for json_obj in json_list:
		if 'full_name' in json_obj.keys():
			full_name = json_obj.pop('full_name')
			json_obj['authors'] = [{'full_name': full_name}]
	return json_list


def main():
	unit_test()

	if len(sys.argv) != 2:
		print("Error: Please provide a filename", file=sys.stderr)
		sys.exit(1)

	print("=> Starting File Read: %s" % sys.argv[1])
	fp = open(sys.argv[1], 'r', encoding='utf-8')

	
	output = post_process_output(csv_to_json(csv.reader(fp)))
			
	fp.close()
	print("=> Finished Parsing\n")
	print(json.dumps(output[0], indent=2))
	should_continue = input("\n=> Does the above look good? [y/N]: ").upper() == 'Y'

	if not should_continue:
		print("Aborting...")
		sys.exit(2)

	out_filename = sys.argv[1].rstrip('csv') + 'json'
	print("=> Starting Output Write: %s " % out_filename)
	
	fpo = open(out_filename, 'w')
	json.dump(output, fpo, indent=2)
	

	should_continue = input("\n=> Do you want to send the request now? [y/N]: ").upper() == 'Y'

	if not should_continue:
		print("=> Done !")
		fpo.close()
		sys.exit(0)

	print("=> Preparing Request")

	url = "https://www.osti.gov/iad2/api/records"

	payload = json.dumps(output)
 
	config = open("config.txt", "r")
	
	headers = {
	  'Authorization': config.read(),
	  'Content-Type': 'application/json',
	  'Cookie': 'BIGipServerwww.osti.gov_pool=1132494278.20480.0000'
	}
 
	config.close()

	print("=> Sending Request")
	response = requests.request("POST", url, headers=headers, data=payload)

	print("=> Handling Response: %s" % response.status_code)
	if response.status_code != 200:
		print("=> POST did not fire successfully! %s" % response.status_code)
	else:
		print("=> Writing Response to file")
		fpo.write('\n\n---------------------------------------------------------------------------------\n\nRESULTS\n\n')
		json.dump(response.json(), fpo, indent=2)
		fpo.close()
		print("=> Done !")
	

if __name__ == '__main__':
	main()