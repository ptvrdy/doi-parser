
# README for DOI Parser for Postman 
National Transportation Library (NTL). Bureau of Transportation Statistics (BTS), U.S. Department of Transportation (USDOT)
2023-03-25
## Links to Dataset  
Dataset Archive Link: https://github.com/tvrdy-ctr/doi-parser

## Tables of Contents  
##### A. General Information  
##### B. Sharing/Access & Policies Information  
##### C. Data and Related Files Overview  
##### D. Software Information  
##### E. File Specific Information  
##### F. Update Log  
## A. General Information  

**Title of Program:**  DOI Parser for Postman

**Description of the Program:** This program takes CSV files and transforms them to JSON files that can then be pushed to the DOE's IAD API. These files are mostly compliant with Datacite's DOI metadata standards, but have important difference that are due to the DOE's IAD API. The record metadata is based off of Datacite's 4.4 schema version.

**Dataset Archive Link:** https://github.com/tvrdy-ctr/doi-parser

**Authorship Information:**  

>  *Principal Data Creator or Data Manager Contact Information*  
>  Name: Peyton Tvrdy ([0000-0002-9720-4725](https://orcid.org/0000-0002-9720-4725))   
>  Institution: National Transportation Library   
>  Email: peyton.tvrdy.ctr@dot.gov  

>  *Co-Author Contact Information*  
>  Name: Joseph Lambeth 
>  Email: josephwlambeth@gmail.com  

>  *Organizational Contact Information*  
>  Name: Peyton Tvrdy ([0000-0002-9720-4725](https://orcid.org/0000-0002-9720-4725))   
>  Institution: National Transportation Library   
>  Email: peyton.tvrdy.ctr@dot.gov  
 

## B. Sharing/Access and Policies Information  

**Recommended citation for the data:**  

>  Tvrdy, Peyton and Joseph Lambeth. (2024). DOI Parser for Postman Updates. https://github.com/tvrdy-ctr/doi-parser  

**Licenses/restrictions placed on the data:** https://creativecommons.org/licenses/by/4.0/legalcode  
 
## C. File Overview  

File List for the `Insert Full Dataset ZIP File Name Here: Ex: 12348_DATASET`  

>  1. Filename: test  
>  Short Description:  This folder contains the unit test csv and json files   

>  2. Filename: unit_test_original  
>  Short Description:  This folder contains the original unit test created for this project.  

>  3. Filename: constants.py  
>  Short Description:  Contains the dictionary that maps publishers to their ROR IDs.  

>  4. Filename: doi-parser.py  
>  Short Description:  Main python file that converts the csv file to json and posts to postman.  

>  5. Filename: post-processes.py
>  Short Description:  Contains all the functions used on the data after processing. 

>  6. Filename: product-type.json
>  Short Description:  Dictionary containing product type values to match DOE's IAD product type field.  

## D. Software Information  

**Instrument or software-specific information needed to interpret the data:** This software is best run through command prompt. It is best edited with visual studio code. Microsoft Excel was used to make csv files.  

## E. File Specific Information  

1. constants.py  
This file is the dictionary of ROR IDs used for the Publisher field. This dictionary should be changed with values that are relevant to your institution.  

2. post-processes.py  
This file is where you would make your additional functions. If implementing these functions at your institution, make sure that you change the function `NTL_Hosting_Institution` to your institution or the institution that will host the item.    

## F. Update Log  

This README.txt file was originally created on 2024-03-07 by Peyton Tvrdy ([0000-0002-9720-4725](https://orcid.org/0000-0002-9720-4725)), Data Management and Data Curation Fellow, National Transportation Library <peyton.tvrdy.ctr@dot.gov>  
 
2023-03-25: : Original file created
