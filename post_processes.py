from constants import (
    collections_to_doi_lookup,
    series_to_doi_lookup,
    resource_type_lookup,
    language_dict
)

import logging

from utils import (
    get_ror_info
)

# logging.basicConfig(filename='process.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#this function removes unneeded columns from the CSV: "Main Document URL", "Supporting Documents URLs", "sm:Publisher", "Geographical Coverage", "sm:Contracting Officer", "sm:Rights Statement"
def delete_unwanted_columns(json_list):
    for json_obj in (json_list):
        json_obj.pop('Main Document URL', None)
        json_obj.pop('Supporting Documents URLs', None)
        json_obj.pop('sm:Publisher', None)
        json_obj.pop('Geographical Coverage', None)
        json_obj.pop('sm:Contracting Officer', None)
        json_obj.pop('sm:Rights Statement', None)
    return json_list

#this function matches "Workroom ID" to Alternateidentifier
def workroom_id(json_list):
    for index, json_obj in enumerate(json_list):
        if 'Workroom ID' in json_obj:
            accession_number = json_obj.pop('Workroom ID')
            json_obj.setdefault('alternateIdentifiers', []).append({
                'alternateIdentifier': accession_number, 
                'alternateIdentifierType': "DOT ROSA P Accession Number"
                })
        else:
            logging.info(f'Workroom ID not found for row {index +1}.')
    return json_list

#this function matches "ROSAP_ID" to Alternateidentifier
def ROSAP_ID(json_list):
    for index, json_obj in enumerate(json_list):
        if 'ROSAP_ID' in json_obj:
            swat_id = json_obj.pop('ROSAP_ID')
            json_obj.setdefault('alternateIdentifiers', []).append({
                'alternateIdentifier': swat_id, 
                'alternateIdentifierType': "CDC SWAT Identifier"
                })
        else:
            logging.info(f'ROSAP_ID not found for row {index + 1}.')
    return json_list
    
#this function matches "ROSAP_URL" to url
def ROSAP_URL(json_list):
    for index, json_obj in enumerate(json_list):
        if 'ROSAP_URL' in json_obj:
            url = json_obj.pop('ROSAP_URL').strip()
            json_obj['url'] = url
            if 'https://highways.dot.gov/' in url:
                json_obj.setdefault('Contributors', []).append({
                    'name': 'United States. Department of Transportation. Federal Highway Administration', 
                    'nameType': 'Organizational', 
                    'contributorType': 'HostingInstitution', 
                    'lang': 'en', 
                    'nameIdentifiers': [
                        {'nameIdentifier': "https://ror.org/0473rr271", 
                         "nameIdentifierScheme": 'ROR', 
                         'schemeURI': "https://ror.org/"}
                    ]
                })
            elif 'https://rosap.ntl.bts.gov/' in url:
                json_obj.setdefault('Contributors', []).append({
                    'name': 'United States. Department of Transportation. National Transportation Library', 
                    'nameType': 'Organizational', 
                    'contributorType': 'HostingInstitution', 
                    'lang': 'en', 
                    'nameIdentifiers': [
                        {'nameIdentifier': "https://ror.org/00snbrd52", 
                         "nameIdentifierScheme": 'ROR', 
                         'schemeURI': "https://ror.org/"}
                    ]
                })
            else:
                logging.warn(f"ROSAP_URL contributor not mapped for {index + 1}. URL: ${url}")
        else:
            logging.info(f'ROSAP_URL not found for row {index + 1}.')
    return json_list

#this function matches "sm:Collection" to RelatedIdentifier
def sm_Collection(json_list):
    for index, json_obj in enumerate(json_list):
        if 'sm:Collection' in json_obj:
            collections = json_obj.pop('sm:Collection').split(';')
            for collection in collections:
                collection = collection.strip()
                if collection in collections_to_doi_lookup:
                    #Create a new DOI-related entry
                    doi_entry_collection = {
                        'relatedIdentifier': collections_to_doi_lookup[collection],
                        'relatedIdentifierType': 'DOI',
                        'relationType': 'IsPartOf'
                    }
                    #Initialize 'related_identifiers' if not already present
                    json_obj.setdefault("relatedIdentifiers", []).append(doi_entry_collection)
                else:
                    logging.warn(f'Collection {collection} not found in lookup for row {index + 1}.')
        else:
            logging.info(f'sm:Collection not found for row {index + 1}.')
    return json_list

#this function matches "sm:Digital Object Identifier" to doi, prefix and id
def sm_digital_object_identifier(json_list):
    for index, json_obj in enumerate(json_list):
        if 'sm:Digital Object Identifier' in json_obj:
            doi = json_obj.pop('sm:Digital Object Identifier')
            doi = doi.replace('https://doi.org/','').strip()
            json_obj['id']=doi
            json_obj.setdefault('attributes', {})['doi']=doi
            prefix, suffix = doi.split('/')
            json_obj.setdefault('attributes', {})['prefix']=prefix
            json_obj.setdefault('attributes', {})['suffix']=suffix
        else:
            logging.info(f'DOI not found for row {index + 1}.')
    return json_list
            
#this function matches "Title" to titles
def title(json_list):
    for json_obj in json_list:
        title = json_obj.pop('Title')
        json_obj.setdefault('titles', []).append({'title': title})
    return json_list

#this function matches "Alternative Title" to title and title type
def alt_title(json_list):
    for json_obj in (json_list):
        if 'Alternative Title' in json_obj:
            alt_title = json_obj.pop('Alternative Title')
            json_obj.setdefault('titles', []).append({
                'title': alt_title, 
                'title_type': 'AlternativeTitle'
                })
    return json_list
        
#this function matches "Published Date" to Publication Year, Date, and dateType
def publication_date(json_list):
    for index, json_obj in enumerate(json_list):
        date = json_obj.pop('Published Date')
        json_obj.setdefault('dates', []).append({'date': date, 'dateType': 'Issued'})
        published_year = date[:4]
        json_obj['PublicationYear']=published_year
    return json_list

#this function matches "sm:Format" to ResourceType and resourceTypeGeneral
def resource_type(json_list):
    for index, json_obj in enumerate(json_list):
            if 'sm:Format' and 'sm:Resource Type' in json_obj:
                resource_type_general = json_obj.pop('sm:Format')
                resource_type = json_obj.pop('sm:Resource Type')
                if resource_type in resource_type_lookup:
                    resource_type = resource_type.strip()
                    resource_type_general = resource_type_general.strip()
                    json_obj.setdefault('Types', {})['resourceTypeGeneral']=resource_type_general
                    json_obj.setdefault('Types', {})['ResourceType']=resource_type_lookup[resource_type]
                else:
                    logging.warn(f'Resource type {resource_type} is not found in the lookup for row {index + 1}.')
            else:
                logging.info(f'sm: Format and/or sm:Resource Type not found in row {index + 1}.')
    return json_list

#this function matches "sm:Creator" to creators and splits it.
def creators(json_list):
    for index, json_obj in enumerate(json_list):
        if 'sm:Creator' in json_obj:
            creators = json_obj.pop('sm:Creator').split('\\n')
            for creator in creators:
                creator = creator.strip()
                last_name, first_name = creator.split(',')
                last_name = last_name.strip()
                first_name = first_name.strip()
                if "|" in first_name:
                    first_name, ORCID = first_name.split('|')
                    ORCID = ORCID.strip()
                    if ORCID.startswith("https://orcid.org/"):
                        ORCID = ORCID.replace('https://orcid.org/', '')
                    json_obj.setdefault('creators', []).append({
                        'name': creator, 
                        'nameType': 'Personal', 
                        'givenName': first_name, 
                        'familyName': last_name, 
                        'nameIdentifiers': [
                            {'nameIdentifier': ORCID, "nameIdentifierScheme": 'ORCID', 'schemeURI': "https://orcid.org/"}
                        ]})
                else:
                    json_obj.setdefault('creators', []).append({
                        'name': creator, 
                        'nameType': 'Personal', 
                        'givenName': first_name, 
                        'familyName': last_name})
        else:
            logging.info(f'sm:Creator not found for row {index + 1}.')
    return json_list

def process_corporate_field(json_list, field_name):
    # Define a mapping of field names to output structures for "sm:Corporate Creator", "sm:Corporate Contributor", and "sm:Corporate Publisher"
    field_mapping = {
        'sm:Corporate Creator': {
            'key': 'creators',
            'nameType': 'Organization',
            'contributorType': 'Sponsor',
        },
        'sm:Corporate Contributor': {
            'key': 'contributors',
            'nameType': 'Organization',
            'contributorType': 'Sponsor',
        },
        'sm:Corporate Publisher': {
            'key': 'publishers',
            'lang': 'en',
        },
    }
    for index, json_obj in enumerate(json_list):
        if field_name in json_obj:
            corporate_values = json_obj.pop(field_name).split('\\n')
            for corporate_value in corporate_values:
                corporate_value = corporate_value.strip()
                ror_id, ror_name, ror_lang = get_ror_info(corporate_value)
                output_structure = field_mapping.get(field_name, {})
                if ror_id:
                    entry ={
                        'name': ror_name, 
                        'name_identifier': ror_id, 
                        'nameIdentifierScheme': 'ROR', 
                        'schemeURI': 'https://ror.org/',
                        'lang': ror_lang
                    }
                else:
                    json_obj.setdefault(output_structure['key'], []).append({
                        'name': corporate_value, 
                        **output_structure.get('additional_fields', {})
                    })
                logging.info(f'{field_name} ROR for {corporate_value} not found for row {index + 1}.')
        else:
            logging.info(f'{field_name} not found for row {index + 1}.')
    return json_list

                        
#this functions matches "sm:Contributor" to the contributors object list
def contributors(json_list):
    for index, json_obj in enumerate(json_list):
        if 'sm:Contributor' in json_obj:
            contributors = json_obj.pop('sm:Contributor').split('\\n')
            for contributor in contributors:
                contributor = contributor.strip()
                last_name, first_name = contributor.split(',')
                last_name = last_name.strip()
                first_name = first_name.strip()
                if "|" in first_name:
                    first_name, ORCID = first_name.split('|')
                    ORCID = ORCID.strip()
                    json_obj.setdefault('contributors', []).append({
                        'contributorName': contributor, 
                        'nameType': 'Personal', 
                        'givenName': first_name, 
                        'familyName': last_name, 
                        'contributorType': 'Researcher', 
                        'nameIdentifiers': [
                            {'nameIdentifier': ORCID, "nameIdentifierScheme": 'ORCID', 'schemeURI': "https://orcid.org/"}
                        ]})
                else:
                    json_obj.setdefault('contributors', []).append({
                        'contributorName': contributor, 
                        'nameType': 'Personal', 
                        'givenName': first_name, 
                        'contributorType': 'Researcher',
                        'familyName': last_name})
        else:
            logging.info(f'sm:Contributor not found for row {index + 1}.')
    return json_list

#this function matches "sm:Key words" to subjects
def keywords(json_list):
    for index, json_obj in enumerate(json_list):
        if 'sm:Key words' in json_obj:
            keywords_str = json_obj['sm:Key words'].split('\\n')
            if keywords_str.endswith(', '):
                    keywords_str = keywords_str[:-2]
            for keyword in keywords_str:
                keyword = keyword.strip()
                json_obj.setdefault('subjects', []).append({
                    'subject': keyword,
                    'subjectScheme': 'Transportation Research Thesaurus',
                    'schemeURI': 'https://trt.trb.org/'
                })
        else:
            logging.info(f'sm:Key words not found for row {index + 1}.')
    return json_list

#this function matches "sm:Report Number" to alternateIdentifier
def report_number(json_list):
    for json_obj in enumerate:
        if 'sm:Report Number' in json_obj:
            report_number = json_obj.pop('sm:Report Number')
            report_number = report_number.strip()
            json_obj.setdefault('alternateIdentifiers', []).append({
                'alternateIdentifier': report_number, 
                'alternateIdentifierType': "DOT Report Number"
                })
    return json_list

#this function matches "Grants, Contracts, Cooperative Agreements" to alternateIdentifier
def contract_number(json_list):
    for json_obj in json_list:
        if 'Grants, Contracts, Cooperative Agreements' in json_obj:
            contract_number = json_obj.pop('Grants, Contracts, Cooperative Agreements')
            contract_number = contract_number.strip()
            json_obj.setdefault('alternateIdentifiers', []).append({
                'alternateIdentifier': contract_number, 
                'alternateIdentifierType': "DOT Contract, Grant, or Cooperative Agreement Number"
                })
    return json_list

#this function matches "sm:ResearchHub ID" to alternateIdentifier
def researchHub_id(json_list):
    for json_obj in json_list:
        if 'sm:ResearchHub ID' in json_obj:
            researchhub_id = json_obj.pop('sm:ResearchHub ID')
            researchhub_id = researchhub_id.strip()
            json_obj.setdefault('alternateIdentifiers', []).append({
                'alternateIdentifier': researchhub_id, 
                'alternateIdentifierType': "DOT ResearchHub Display ID"})
    return json_list

#this function matches "Content Notes" to 'Descriptions'/TechnicalInfo
def content_notes(json_list):
    for json_obj in json_list:
        curation_note = "National Transportation Library (NTL) Curation Note: This dataset has been curated to CoreTrustSeal's curation level \"B. Logical-Technical Curation.\""
        if 'Content Notes' in json_obj:
            content_note = json_obj.pop('Content Notes').strip()
            json_obj.setdefault('Descriptions', []).append({
                'description': content_note, 
                'lang': 'en', 
                'descriptionType': 'TechnicalInfo'
                })
            if curation_note in content_note:
                json_obj.setdefault('contributors', []).append({
                    'contributorName': "Peyton Tvrdy", 
                    'nameType': 'Personal', 
                    'givenName': "Peyton", 
                    'familyName': "Tvrdy", 
                    'contributorType': 'DataCurator', 
                    'nameIdentifiers': [
                        {'nameIdentifier': "https://orcid.org/0000-0002-9720-4725", "nameIdentifierScheme": 'ORCID', 'schemeURI': "https://orcid.org/"}
                    ]  
                })
    return json_list

#this function matches "Language" to language
def language(json_list):
    for index, json_obj in enumerate(json_list):
        if 'Language' in json_obj:
            language = json_obj.pop('Language')
            language = language.strip()
            if language in language_dict:
                json_obj['language']=language
            else:
                logging.warn(f'Language {language} not found in language dictionary for row {index + 1}.')
        else:
            logging.info(f'Language not found for row {index + 1}.')
    return json_list

#this function matches "Edition" to version
def edition(json_list):
    for json_obj in json_list:
        if 'Edition' in json_obj:
            version = json_obj.pop('Edition')
            version = language.strip()
            json_obj['version']=version
    return json_list

#this function matches Series and their DOIs to IsPartOf to the correct related identifier structure
def series(json_list):
    for index, json_obj in enumerate(json_list):
        if 'Series Name' in json_obj:
            series_dois = json_obj.pop('Series Name').split('\\n')
            for series_doi in series_dois:
                if series_doi in series_to_doi_lookup:
                    # Create a new DOI-related entry
                    doi_entry_series = {
                        'relatedIdentifierType': 'DOI', 
                        'relatedIdentifier': series_to_doi_lookup[series_doi], 
                        'relationType': 'IsPartOf'
                    }
                    # Initialize 'related_identifiers' if not already present
                    json_obj.setdefault("relatedIdentifiers", []).append(doi_entry_series)
                else:
                    logging.warn(f'Series {series_doi} not found in series dictionary for row {index + 1}.')
    return json_list

#this function matches 'Description' to 'Descriptions'/Abstract
def description(json_list):
    for index, json_obj in enumerate(json_list):
        if 'Description' in json_obj:
            description = json_obj.pop('Description')
            json_obj.setdefault('Descriptions', []).append({
                'description': description, 
                'lang': 'en', 
                'descriptionType': 'Abstract'
                })
        else:
            logging.info(f'Description not found for row {index + 1}.')
    return json_list
