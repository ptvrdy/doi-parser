from constants import acronym_to_url_lookup as pub_to_ror
from constants import collections_to_doi_lookup
from constants import series_to_doi_lookup

#this function matches "Workroom ID" to Alternateidentifier
def workroom_id(json_list):
    for json_obj in json_list:
        if 'Workroom ID' in json_obj.keys():
            accession_number = json_obj.pop('Workroom ID')
            json_obj.setdefault('Alternateidentifier', []).append({'Alternate Identifier': accession_number, 'alternateIdentifierType': "ROSA P Accession Number"})
    return json_list

#this function matches "ROSAP_ID" to Alternateidentifier
def ROSAP_ID(json_list):
    for json_obj in json_list:
        if 'ROSAP_ID' in json_obj.keys():
            swat_id = json_obj.pop('ROSAP_ID')
            json_obj.setdefault('Alternateidentifier', []).append({'Alternate Identifier': swat_id, 'alternateIdentifierType': "CDC SWAT Identifier"})
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
				if publisher_name in pub_to_ror:
					json_obj.setdefault('publishers', []).append({
						'name': publisher_name,
						'schemeUri': 'https://ror.org',
						'nameIdentifier': pub_to_ror[publisher_name],
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