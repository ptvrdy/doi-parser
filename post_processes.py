from constants import organization_to_ror_lookup
from constants import collections_to_doi_lookup
from constants import series_to_doi_lookup
from constants import resource_type_lookup
from constants import language_dict
import requests

#this function matches "Workroom ID" to Alternateidentifier
def workroom_id(json_list):
    for json_obj in json_list:
        if 'Workroom ID' in json_obj.keys():
            accession_number = json_obj.pop('Workroom ID')
            json_obj.setdefault('alternateIdentifiers', []).append({'alternateIdentifier': accession_number, 'alternateIdentifierType': "ROSA P Accession Number"})
    return json_list

#this function matches "ROSAP_ID" to Alternateidentifier
def ROSAP_ID(json_list):
    for json_obj in json_list:
        if 'ROSAP_ID' in json_obj.keys():
            swat_id = json_obj.pop('ROSAP_ID')
            json_obj.setdefault('alternateIdentifiers', []).append({'alternateIdentifier': swat_id, 'alternateIdentifierType': "CDC SWAT Identifier"})
    return json_list
    
#this function matches "ROSAP_URL" to url
def ROSAP_URL(json_list):
    for json_obj in json_list:
        if 'ROSAP_URL' in json_obj.keys():
            url = json_obj.pop('ROSAP_URL').strip()
            json_obj['url'] = url
    return json_list

#this function matches "sm:Collection" to RelatedIdentifier
def sm_Collection(json_list):
    for json_obj in json_list:
        if 'sm:Collection' in json_obj.keys():
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
    return json_list

#this function matches "sm:Digital Object Identifier" to doi, prefix and id
def sm_digital_object_identifier(json_list):
    for json_obj in json_list:
        if 'sm:Digital Object Identifier' in json_obj.keys():
            doi = json_obj.pop('sm:Digital Object Identifier')
            doi = doi.replace('https://doi.org/','').strip()
            json_obj['id']=doi
            json_obj.setdefault('attributes', {})['doi']=doi
            prefix, suffix = doi.split('/')
            json_obj.setdefault('attributes', {})['prefix']=prefix
            json_obj.setdefault('attributes', {})['suffix']=suffix
    return json_list
            
#this function matches "Title" to titles
def title(json_list):
    for json_obj in json_list:
        title = json_obj.pop('Title')
        json_obj.setdefault('titles', []).append({'title': title})
    return json_list

#this function matches "Alternative Title" to title and title type
def alt_title(json_list):
    for json_obj in json_list:
        alt_title = json_obj.pop('Alternative Title')
        json_obj.setdefault('titles', []).append({'title': alt_title, 'title_type': 'AlternativeTitle'})
    return json_list
        
#this function matches "Published Date" to Publication Year, Date, and dateType
def publication_date(json_list):
    for json_obj in json_list:
        if 'Published Date' in json_obj.keys():
            date = json_obj.pop('Published Date')
            json_obj.setdefault('dates', []).append({'date': date, 'dateType': 'Issued'})
            published_year = date[:4]
            json_obj['PublicationYear']=published_year
    return json_list

#this function matches "sm:Format" to ResourceType and resourceTypeGeneral
def resource_type(json_list):
    for json_obj in json_list:
            if 'sm:Format' and 'sm:Resource Type' in json_obj.keys():
                resource_type_general = json_obj.pop('sm:Format')
                resource_type = json_obj.pop('sm:Resource Type')
                if resource_type in resource_type_lookup:
                    resource_type = resource_type.strip()
                    resource_type_general = resource_type_general.strip()
                    json_obj.setdefault('Types', {})['resourceTypeGeneral']=resource_type_general
                    json_obj.setdefault('Types', {})['ResourceType']=resource_type_lookup[resource_type]
    return 

#this function matches "sm:Creator" to creators and splits it.
def creators(json_list):
    for json_obj in json_list:
        if 'sm:Creator' in json_obj.keys():
            creators = json_obj.pop('sm:Creator').split('\\n')
            for creator in creators:
                creator = creator.strip()
                last_name, first_name = creator.split(',')
                last_name = last_name.strip()
                first_name = first_name.strip()
                if "|" in first_name:
                    first_name, ORCID = first_name.split('|')
                    ORCID = ORCID.strip()
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
    return json_list

def get_ror_info(corporate_creator):
    # Check if the corporate creator exists in the dictionary
    if corporate_creator in organization_to_ror_lookup:
        ror_id = organization_to_ror_lookup[corporate_creator]
        # You can extract other relevant information from the URL or dictionary
        # (e.g., language, display value) if available.
        return ror_id
    # Query the ROR API
    API_URL = 'https://api.dev.ror.org/v2/organizations'
    try:
        corporate_creator_clean = corporate_creator.replace('United States. ','').strip()
        corporate_creator_clean = corporate_creator.replace('Department of Transportation. ','').strip()
        response = requests.get(API_URL, params={'query': corporate_creator_clean})
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
                return ror_id, ror_name, ror_name_lang
            else:
                # Handle the case when the API isn't working
                print(f"API request failed for '{corporate_creator_clean}'")
    except Exception as e:
        print(f"Error fetching ROR data for '{corporate_creator}': {e}")
    return None

def corporate_creator(json_list):
    for json_obj in json_list:
        if 'sm:Corporate Creator' in json_obj.keys():
            corporate_creators = json_obj.pop('sm:Corporate Creator').split('\\n')
            for corporate_creator in corporate_creators:
                corporate_creator = corporate_creator.strip()
                ror_id = get_ror_info(corporate_creator)
                if ror_id:
                    json_obj.setdefault('creators', []).append({
                        'name': corporate_creator, 
                        'nameType': 'Organization', 
                        'nameIdentifier': ror_id, 
                        'nameIdentifierScheme': 'ROR', 
                        'schemeURI': 'https://ror.org/'
                    })
    return json_list
                        
#this functions matches "sm:Contributor" to the contributors object list
def contributors(json_list):
    for json_obj in json_list:
        if 'sm:Contributor' in json_obj.keys():
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
    return json_list

#this function matches "sm:Corporate Publisher" to their ROR ID if they have them        
def publisher(json_list):
	for json_obj in json_list:
		if 'sm:Corporate Publisher' in json_obj.keys():
			publisher_names = json_obj['sm:Corporate Publisher'].split('\\n')
			for publisher_name in publisher_names:
				publisher_name = publisher_name.strip()
				if publisher_name in organization_to_ror_lookup:
					json_obj.setdefault('publishers', []).append({
						'name': publisher_name,
						'schemeUri': 'https://ror.org',
						'publisherIdentifier': organization_to_ror_lookup[publisher_name],
						'publisherIdentifierScheme': 'ROR',
						'lang': 'en'})
	return json_list

#this function matches "sm:Key words" to subjects
def keywords(json_list):
    for json_obj in json_list:
        if 'sm:Key words' in json_obj.keys():
            keywords_list = json_obj['sm:Key words'].split('\\n')
            for keyword in keywords_list:
                keyword = keyword.strip()
                json_obj.setdefault('subjects', []).append({
                    'subject': keyword,
                    'subjectScheme': 'Transportation Research Thesaurus',
                    'schemeURI': 'https://trt.trb.org/'
                })
    return json_list

#this function matches "sm:Report Number" to alternateIdentifier
def report_number(json_list):
    for json_obj in json_list:
        if 'sm:Report Number' in json_obj.keys():
            report_number = json_obj.pop('sm:Report Number')
            report_number = report_number.strip()
            json_obj.setdefault('alternateIdentifiers', []).append({'alternateIdentifier': report_number, 'alternateIdentifierType': "DOT Report Number"})
    return json_list

#this function matches "Grants, Contracts, Cooperative Agreements" to alternateIdentifier
def contract_number(json_list):
    for json_obj in json_list:
        if 'Grants, Contracts, Cooperative Agreements' in json_obj.keys():
            contract_number = json_obj.pop('Grants, Contracts, Cooperative Agreements')
            contract_number = contract_number.strip()
            json_obj.setdefault('alternateIdentifiers', []).append({'alternateIdentifier': contract_number, 'alternateIdentifierType': "DOT Contract, Grant, or Cooperative Agreement Number"})
    return json_list

#this function matches "sm:ResearchHub ID" to alternateIdentifier
def researchHub_id(json_list):
    for json_obj in json_list:
        if 'sm:ResearchHub ID' in json_obj.keys():
            researchhub_id = json_obj.pop('sm:ResearchHub ID')
            researchhub_id = researchhub_id.strip()
            json_obj.setdefault('alternateIdentifiers', []).append({'alternateIdentifier': researchhub_id, 'alternateIdentifierType': "DOT ResearchHub Display ID"})
    return json_list

#this function matches "Content Notes" to 'Descriptions'/TechnicalInfo
def content_notes(json_list):
    for json_obj in json_list:
        if 'Content Notes' in json_obj:
            content_note = json_obj.pop('Content Notes')
            content_note = content_note.strip()
            json_obj.setdefault('Descriptions', []).append({'description': content_note, 'lang': 'en', 'descriptionType': 'TechnicalInfo'})
    return json_list

#this function matches "Language" to language
def language(json_list):
    for json_obj in json_list:
        if 'Language' in json_obj.keys():
            language = json_obj.pop('Language')
            language = language.strip()
            if language in language_dict:
                json_obj['language']=language
    return json_list

#this function matches "Edition" to version
def edition(json_list):
    for json_obj in json_list:
        if 'Edition' in json_obj.keys():
            version = json_obj.pop('Edition')
            version = language.strip()
            json_obj['version']=version
    return json_list

#this function matches Series and their DOIs to IsPartOf to the correct related identifier structure
def series(json_list):
    for json_obj in json_list:
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
    return json_list

#this function matches 'Description' to 'Descriptions'/Abstract
def description(json_list):
    for json_obj in json_list:
        if 'Description' in json_obj:
            description = json_obj.pop('Description')
            json_obj.setdefault('Descriptions', []).append({'description': description, 'lang': 'en', 'descriptionType': 'Abstract'})
    return json_list

#this function adds the HostingInstitution element to each record as a Contributor
def hosting_institution(json_list):
    for json_obj in json_list:
        if 'site_url' in json_obj and 'https://highways.dot.gov/' in json_obj['site_url']:
            json_obj.setdefault('Contributors', []).append({
                'name': 'United States. Department of Transportation. Federal Highway Administration', 
                'nameType': 'Organizational', 
                'contributorType': 'HostingInstitution', 
                'lang': 'en', 
                'nameIdentifiers': [
                            {'nameIdentifier': "https://ror.org/0473rr271", "nameIdentifierScheme": 'ROR', 'schemeURI': "https://ror.org/"}
                        ]})
        else:
            json_obj.setdefault('Contributors', []).append({
                'name': 'United States. Department of Transportation. National Transportation Library', 
                'nameType': 'Organizational', 
                'contributorType': 'HostingInstitution', 
                'lang': 'en', 
                'nameIdentifiers': [
                            {'nameIdentifier': "https://ror.org/00snbrd52", "nameIdentifierScheme": 'ROR', 'schemeURI': "https://ror.org/"}
                ]})
    return json_list

#this function matches the heading "full name" to the DOE object "authors." This is used when an organization is responsible for authorship
def corporate_creator(json_list):
    for json_obj in json_list:
        if 'corporate_creator' in json_obj.keys():
            corporate_creators = json_obj.pop('corporate_creator').split(';')
            for corporate_creator in corporate_creators:
                corporate_creator = corporate_creator.strip()
                json_obj.setdefault('authors', []).append({'full_name': corporate_creator})
    return json_list

#this function adds the NTL contributor element to each record. Since each DOI record is always hosted by the National Transportation Library, this is the same for every record.
def NTL_Hosting_Institution(json_list):
    for json_obj in json_list:
        if 'site_url' in json_obj and 'https://highways.dot.gov/' in json_obj['site_url']:
            json_obj.setdefault('contributors', []).append({
                'full_name': 'United States. Department of Transportation. Federal Highway Administration',
                'contributor_type': 'HostingInstitution'
            })
        else:
            json_obj.setdefault('contributors', []).append({
                'full_name': 'United States. Department of Transportation. National Transportation Library',
                'contributor_type': 'HostingInstitution'
            })
    return json_list

#this function matches corporate contributors to the contributor type "Sponsor"
def corporate_contributor(json_list):
    for json_obj in json_list:
        if 'corporate_contributor' in json_obj.keys():
            corporate_contributors = json_obj.pop('corporate_contributor').split(';')
            for corporate_contributor in corporate_contributors:
                corporate_contributor = corporate_contributor.strip()
                json_obj.setdefault('contributors', []).append({'full_name': corporate_contributor, 'contributor_type': 'Sponsor'})
    return json_list

#this function matches publishers to their ROR ID if they have them        
def publisher_has_ROR(json_list):
	for json_obj in json_list:
		if 'publisher_name' in json_obj.keys():
			publisher_names = json_obj['publisher_name'].split(';')
			for publisher_name in publisher_names:
				publisher_name = publisher_name.strip()
				if publisher_name in organization_to_ror_lookup:
					json_obj.setdefault('publishers', []).append({
						'name': publisher_name,
						'schemeUri': 'https://ror.org',
						'nameIdentifier': organization_to_ror_lookup[publisher_name],
						'publisherIdentifierScheme': 'ROR',
						'lang': 'en'})
	return json_list

#this function matches Collection DOIs to IsPartOf to the correct related identifier structure
def collection_DOI(json_list):
    for json_obj in json_list:
        if 'collection' in json_obj:
            collection_dois = json_obj.pop('collection').split(';')
            for collection_doi in collection_dois:
                if collection_doi in collections_to_doi_lookup:
                    # Create a new DOI-related entry
                    doi_entry_collection = {
                        'identifier_type': 'DOI',
                        'identifier_value': collections_to_doi_lookup[collection_doi],
                        'relation_type': 'IsPartOf'
                    }
                    # Initialize 'related_identifiers' if not already present
                    json_obj.setdefault('related_identifiers', []).append(doi_entry_collection)
    return json_list

#this function matches Series DOIs to IsPartOf to the correct related identifier structure
def series_DOI(json_list):
    for json_obj in json_list:
        if 'series' in json_obj:
            series_dois = json_obj.pop('series').split(';')
            for series_doi in series_dois:
                if series_doi in series_to_doi_lookup:
                    # Create a new DOI-related entry
                    doi_entry_series = {
                        'identifier_type': 'DOI',
                        'identifier_value': series_to_doi_lookup[series_doi],
                        'relation_type': 'IsPartOf'
                    }
                    # Initialize 'related_identifiers' if not already present
                    json_obj.setdefault('related_identifiers', []).append(doi_entry_series)
    return json_list