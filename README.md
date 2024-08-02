# README for DOI Parser Version 2.0 for DataCite   

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) <img src="https://img.shields.io/badge/json-000000?style=for-the-badge&logo=json&logoColor=white" alt="JSON" height="28"> <a href="https://creativecommons.org/licenses/by/4.0"><img src="https://licensebuttons.net/l/by/3.0/88x31.png" alt="licensebuttons by" height="28"></a> <a href="https://datacite.org/"><img src="https://datacite.org/wp-content/uploads/2023/05/DataCite-Logo_secondary.png" alt="DataCite" height="28"></a> <a href="https://ror.org"><img src="https://raw.githubusercontent.com/ror-community/ror-logos/main/ror-icon-rgb.svg" alt="Research Organization Registry (ROR)" height="28"></a>    

National Transportation Library (NTL). Bureau of Transportation Statistics (BTS), U.S. Department of Transportation (USDOT). [ROR ID: https://ror.org/00snbrd52](https://ror.org/00snbrd52)  
2024-08-02  

## Link to Project  
Archive Link: <https://github.com/ptvrdy/doi-parser>  

## Tables of Contents  
A. [General Information](#a-general-information)  
B. [Sharing/Access & Policies Information](#b-sharingaccess-and-policies-information)  
C. [Data and Related Files Overview](#c-file-overview)  
D. [Software Information](#d-software-information)  
E. [File Specific Information](#e-file-specific-information)  
F. [Update Log](#f-update-log)  

## A. General Information  

**Title of Program:**  DOI Parser Version 2.0 for DataCite

**Description of the Program:** This program takes CSV metadata files and transforms them into DataCite Schema JSON files based off of the CSV headings. This version of the program is compliant with the DataCite Schema Version 4.5. The purpose of the program is convert already existing metadata to the DataCite schema and post to the DataCite API to update/create DOI metadata. The program then returns the API Response and generates a CSV of the DOIs updated/created and that item's title. This program aims to streamline DOI metadata management by converting metadata to the DataCite schema, posting to their API, and returning relevant response data. 

**Special Features of This Program:**
1. Maps CSV headings to [DataCite Schema](https://schema.datacite.org/meta/kernel-4.5), crosswalking the metadata to the DataCite schema  
2. For organizations that are contributors, creators, or publishers, searches the [ROR API](https://ror.org/) to retrieve ROR Display Names and ROR IDs  
3. If the organization has a ROR ID, the program asks the user to confirm the match provided by the ROR API. If the API is down or cannot confirm a match, the user can manually add ROR information. If there is no ROR ID for an organization, the user can skip ROR input
4. The program then takes the confirmed ROR information or the user input of ROR information and appends it to the organization creator, contributor, or publisher as a 'nameIdentifier' 
4. The program then saves confirmed matches, either user input or ROR matches, to a CSV called 'confirmed_matched_ror.csv' so that users will not have to match the same metadata/inputs between sessions  
5. Once all organizations have been matched to their ROR IDs or skipped, the program displays the first data row of the CSv converted to DataCite JSON schema so the user can validate that the information provided is correct. The user has the opportunity to continue or abort.  
6. If the user would like to continue, the program then asks if they would like to post to the DataCite API. The user has the opportunity to continue or abort.
7. If the user would like to post to the DataCite API, each JSON object is posted to the DataCite API. The program then lets the user know the API response.
8. If the API response is 201, then the API response is logged in the a .log file named after the input CSV.
9. The DOIs and the Titles of each item submitted to and returned by the API is then recorded in a CSV named after the input CSV + doi_results.
10. The program finishes and prints "Done!"  

**Dataset Archive Link:** <https://github.com/ptvrdy/doi-parser>  
**DataCite Schema version:** <https://schema.datacite.org/meta/kernel-4.5>  

**Authorship Information:**  

>  *Co-Author Contact Information*  
>  Name: Peyton Tvrdy <a href="https://orcid.org/0000-0002-9720-4725"><img src="/orcid_id_logo.PNG" height="19"> ([0000-0002-9720-4725](https://orcid.org/0000-0002-9720-4725))   
>  Institution: National Transportation Library [(ROR ID: https://ror.org/00snbrd52)](https://ror.org/00snbrd52)   
>  Email: peyton.tvrdy.ctr@dot.gov  

>  *Co-Author Contact Information*  
>  Name: Joseph Lambeth  
>  Email: josephwlambeth@gmail.com  

## B. Sharing/Access and Policies Information  

**Recommended citation for the data:**  

>  Tvrdy, Peyton and Joseph Lambeth. (2024). DOI Parser Version 2.0 for DataCite. <https://github.com/ptvrdy/doi-parser>  

**Licenses/restrictions placed on the data:** https://creativecommons.org/licenses/by/4.0  
 
## C. File Overview  

File List for doi-parser  

>  1. Filename: config.txt  
>  Short Description:  This folder contains the authentication information for this program to use the DataCite API. Please put in your own authentication information in the format of "Basic YourIdentificationHere" for this program to work.    

>  2. Filename: confirmed_matches_ror.csv  
>  Short Description:  This file contains the ROR ID matches you have made using this program.   

>  3. Filename: confirmed_matches.py  
>  Short Description:  This python file saves and loads confirmed_matches_ror.csv to load/save ROR data.   

>  4. Filename: constants.py  
>  Short Description:  This file contains the constant values needed for the program to run properly, including ISO-639 Language codes, the ROR API link, frequently used ROR IDs, NTL collection DOIs, NTL series DOIs, and a mapping of NTL resource type values to DataCite resource types.  

>  5. Filename: doi_parser.py
>  Short Description:  This is the main python file that loads the CSV, conducts the transformation, and posts the DataCite API.  

>  6. Filename: LICENSE
>  Short Description: This is the license file. 

>  7. Filename: post_processes.py
>  Short Description:  This python file has all the functions used on the CSV data for processing. To implement this program at your institution, this file will need to be heavily edited to change the input CSV headings and change some contains values.  

>  8. Filename: README.md
>  Short Description:  This file is the README file you are reading now. It contains helpful background information about the program its function.  

>  9. Filename: requirements.txt
>  Short Description:  This file contains the python libraries that are required for this program. You can install these libraries on your own or use the pip command found in [Software Information](#d-software-information). 

>  10. Filename: utils.py  
>  Short Description:  This file contains the functions for searching the ROR API and manually confirming ROR information. It also deletes unnecessary columns from the input CSV.  

## D. Software Information  

**Instrument or software-specific information needed to interpret the data:** This software is best run through command prompt. It is best edited with Visual Studio Code. Microsoft Excel was used to make the csv files. To run this software, open the command prompt and navigate to the folder that contains this program. Then, type the following command:  

`python doi_parser.py` + CSV file  
ex: `python doi_parser.py CSV_1_20240101.csv`  

**Required Python Libraries:** For this software to work correctly, please install the python libraries of 'colorama' and 'requests.' To install these automatically, please run the following command in command prompt. Ensure you have pip already installed.  

```  
pip install -r requirements.txt
```

## E. File Specific Information  

1. constants.py  
This file contains information that is relevant to my organization, NTL. This dictionary should be changed with values that are relevant to your institution.  

2. post-processes.py  
This file is where you would make adjustments to my functions and add your own. If implementing these functions at your institution, make sure that you change the function 'NTL_Hosting_Institution' to your institution or the institution that will host the item. Additionally, pay special attention to changing all identifiers and the content note for CoreTrustSeal curation levels.  

## F. Update Log  

This README.md file was originally created on 2024--08-02 by Peyton Tvrdy ([0000-0002-9720-4725](https://orcid.org/0000-0002-9720-4725)), Data Management and Data Curation Fellow, National Transportation Library <peyton.tvrdy.ctr@dot.gov>  
 
2024-08-02: Version 2.0 Project Launch and README created  
