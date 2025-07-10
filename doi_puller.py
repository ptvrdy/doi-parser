import csv
from doi_parser import csv_to_json
import json
import requests
from urllib.parse import quote


def doi_api():
    finished = False
    page_number = 1
    url = "https://api.datacite.org/dois"
    
    dois = set()
    urls = set()
    
    while True:
        print("Querying page:", page_number)
        headers = {'Authorization': 'Basic RE9ULkRPVDpOVExEQHRhUzNydg=='}
        response = requests.get(url, headers=headers, params={'client-id': "dot.dot", "state": "registered", "page[number]": page_number, "page[size]": 25})
        
        if response.status_code != 200:
            print("Uh oh", response.status_code)
            break
        response_body = response.json()
        
        for doi in response_body["data"]:
            dois.add(doi['id'])
            urls.add(doi["attributes"]["url"])
        
        if not response_body['links'].get("next"):
            break
        page_number += 1
    
    return (dois, urls)


def main():
    with open("main_sheet.csv", 'r', encoding='utf-8') as f:
        main_sheet = csv.reader(f)
        main_dict = csv_to_json(main_sheet)

    (dois, urls) = doi_api()

    copied = []
    for csv_row in main_dict:
        if csv_row.get("ROSAP_URL") in urls or csv_row.get("sm:Digital Object Identifier") in dois:
            copied.append(csv_row)
            
    with open("doipull_version3.csv", "w", encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile)

        keys = copied[0].keys()
        csv_writer.writerow(keys)

        for csv_row in copied:
            csv_writer.writerow([csv_row[key] if key in csv_row else '' for key in keys])

    

if __name__ == "__main__":
    main()