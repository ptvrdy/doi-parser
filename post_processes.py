from constants import acronym_to_url_lookup as pub_to_ror
from constants import collections_to_doi_lookup

#this function matches the heading "full name" to the DOE object "authors." This is used when an organization is responsible for authorship
def corporate_creator(json_list):
	for json_obj in json_list:
		if 'corporate_creator' in json_obj.keys():
			full_name = json_obj.pop('corporate_creator')
			json_obj.setdefault('authors', []).append({'full_name': full_name})
	return json_list

#this function adds the NTL contributor element to each record. Since each DOI record is always hosted by the National Transportation Library, this is the same for every record.
def NTL_Hosting_Institution(json_list):
    for json_obj in json_list:
        json_obj.setdefault('contributors', []).append({'full_name': 'United States. Department of Transportation. National Transportation Library',
				'contributor_type': 'HostingInstitution',
				#'nameIdentifier': 'https://ror.org/00snbrd52',
				#'schemeUri': 'https://ror.org',
				#'publisherIdentifierScheme': 'ROR'
				})
    return json_list

#this function matches corporate contributors to the contributor type "Sponsor"
def corporate_contributor(json_list):
	for json_obj in json_list:
		if 'corporate_contributor' in json_obj.keys():
			full_name = json_obj.pop('corporate_contributor')
			json_obj.setdefault('contributors', []).append({'full_name': full_name, 'contributor_type': 'Sponsor'})
	return json_list

#this function matches publishers to RORs if they have them        
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

#this function matches Series DOIs/IsPartOf to the correct related identifier structure
#def series_DOI(json_list):
	for json_obj in json_list:
		if 'collection_series_identifier' in json_obj.keys():
			series_dois = json_obj['collection_series_identifier'].split(';')
			for series_doi in series_dois:
				if series_doi in collections_to_doi_lookup:
					json_obj.setdefault('related_identifiers', []).append({'identifier_type': 'DOI', 'identifier_value': collections_to_doi_lookup[series_doi], 'relation_type': 'IsPartOf'})
		return json_list

def series_DOI(json_list):
    for json_obj in json_list:
        if 'collection_series_identifier' in json_obj:
            series_dois = json_obj['collection_series_identifier'].split(';')
            for series_doi in series_dois:
                if series_doi in collections_to_doi_lookup:
                    # Create a new DOI-related entry
                    doi_entry = {
                        'identifier_type': 'DOI',
                        'identifier_value': collections_to_doi_lookup[series_doi],
                        'relation_type': 'IsPartOf'
                    }
                    # Initialize 'related_identifiers' if not already present
                    json_obj.setdefault('related_identifiers', []).append(doi_entry)
    return json_list