from constants import (
    collections_to_doi_lookup,
    series_to_doi_lookup,
    resource_type_lookup,
    language_dict
)

import logging

from utils import (
    get_ror_info,
    delete_unwanted
)

# logging.basicConfig(filename="process.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#this function removes unneeded columns from the CSV: "Main Document URL", "Supporting Documents URLs", "sm:Publisher", "Geographical Coverage", "sm:Contracting Officer", "sm:Rights Statement"
def delete_unwanted_columns(json_list):
    for json_obj in (json_list):
        delete_unwanted(json_obj, "Main Document URL")
        delete_unwanted(json_obj, "Supporting Documents URLs")
        delete_unwanted(json_obj, "sm:Publisher")
        delete_unwanted(json_obj, "sm:Geographical Coverage")
        delete_unwanted(json_obj, "sm:Contracting Officer")
        delete_unwanted(json_obj, "sm:Rights Statement")
    return json_list

#this function matches "Workroom ID" to Alternateidentifier
def workroom_id(json_list):
    for index, json_obj in enumerate(json_list):
        if "Workroom ID" in json_obj:
            accession_number = json_obj.pop("Workroom ID")
            json_obj.setdefault("alternateIdentifiers", []).append({
                "alternateIdentifier": accession_number, 
                "alternateIdentifierType": "DOT ROSA P Accession Number"
            })
        else:
            logging.info(f"Workroom ID not found for row {index +1}.")
    return json_list

#this function matches "ROSAP ID" to Alternateidentifier
def rosap_id(json_list):
    for index, json_obj in enumerate(json_list):
        if "ROSAP ID" in json_obj or "ROSAP_ID" in json_obj:
            swat_id = json_obj.pop("ROSAP ID", json_obj.pop("ROSAP_ID", None))
            json_obj.setdefault("alternateIdentifiers", []).append({
                "alternateIdentifier": swat_id, 
                "alternateIdentifierType": "CDC SWAT Identifier"
                })
        else:
            logging.info(f"ROSAP ID not found for row {index + 1}.")
    return json_list
    
#this function matches "ROSAP URLs" to url
def rosap_url(json_list):
    for index, json_obj in enumerate(json_list):
        if "ROSAP URLs" in json_obj or "ROSAP_URL" in json_obj:
            url = json_obj.pop("ROSAP URLs", json_obj.pop("ROSAP_URL", None)).strip()
            json_obj["url"] = url
            if "https://highways.dot.gov/" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "United States. Department of Transportation. Federal Highway Administration", 
                    "nameType": "Organizational", 
                    "contributorType": "HostingInstitution", 
                    "lang": "en", 
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://ror.org/0473rr271", 
                         "nameIdentifierScheme": "ROR", 
                         "schemeUri": "https://ror.org/"}
                    ]
                })
            elif "https://rosap.ntl.bts.gov/" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "United States. Department of Transportation. National Transportation Library", 
                    "nameType": "Organizational", 
                    "contributorType": "HostingInstitution", 
                    "lang": "en", 
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://ror.org/00snbrd52", 
                         "nameIdentifierScheme": "ROR", 
                         "schemeUri": "https://ror.org/"}
                    ]
                })
            else:
                logging.warn(f"ROSAP URLs contributor not mapped for {index + 1}. URL: ${url}")
        else:
            logging.info(f"ROSAP URL not found for row {index + 1}.")
    return json_list

#this function matches "sm:Collection" to RelatedIdentifier
def sm_Collection(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Collection" in json_obj:
            collections = json_obj.pop("sm:Collection").split(";")
            for collection in collections:
                collection = collection.strip()
                if collection in collections_to_doi_lookup:
                    #Create a new DOI-related entry
                    doi_entry_collection = {
                        "relatedIdentifier": collections_to_doi_lookup[collection],
                        "relatedIdentifierType": "DOI",
                        "relationType": "IsPartOf",
                        "resourceTypeGeneral": "Collection"
                    }
                    #Initialize "related_identifiers" if not already present
                    json_obj.setdefault("relatedIdentifiers", []).append(doi_entry_collection)
                else:
                    logging.warn(f"Collection {collection} not found in lookup for row {index + 1}.")
        else:
            logging.info(f"sm:Collection not found for row {index + 1}.")
    return json_list


def handle_draft_vs_publish(json_list):
    for i, json_obj in enumerate(json_list):
        if json_obj.get("sm:Digital Object Identifier") and json_obj['sm:Digital Object Identifier'].strip():
            sm_digital_object_identifier(json_obj)
        else:
            logging.info(f"Setting to draft state for row {i}")
            draft_state(json_obj)
    return json_list

#this function matches "sm:Digital Object Identifier" to doi, prefix and id
def sm_digital_object_identifier(json_obj):
    doi = json_obj.pop("sm:Digital Object Identifier")
    doi_identifier = doi.replace("https://doi.org/","").strip()
    json_obj["doi"]= doi_identifier

    prefix, suffix = doi_identifier.split('/', 2)
    json_obj["prefix"] = prefix
    json_obj["event"]= "publish"

#this function registers the DOI and the metadata in the "draft" state. This state functions much like a reserve. The attribute "prefix", without the attribute "doi", triggers suffix auto-generation.
def draft_state(json_obj):
    json_obj['prefix'] = "10.21949" # TODO: redo config.txt to something better !

            
#this function matches "Title" to titles
def title(json_list):
    for json_obj in json_list:
        logging.debug("My object is " + str(json_obj))
        title = json_obj.pop("Title")
        json_obj.setdefault("titles", []).append({
            "title": title, 
            "lang": "en"
            })
    return json_list

#this function matches "Alternative Title" to title and title type
def alt_title(json_list):
    for json_obj in (json_list):
        if "Alternative Title" in json_obj:
            alt_title = json_obj.pop("Alternative Title")
            json_obj.setdefault("titles", []).append({
                "title": alt_title, 
                "titleType": "AlternativeTitle", 
                "lang": "en"
                })
    return json_list
        
#this function matches "Published Date" to Publication Year, Date, and dateType
def publication_date(json_list):
    for index, json_obj in enumerate(json_list):
        date = json_obj.pop("Published Date")
        json_obj.setdefault("dates", []).append({"date": date, "dateType": "Issued"})
        published_year = date[:4]
        json_obj["publicationYear"] = int(published_year)
    return json_list

#this function matches "sm:Format" to ResourceType and resourceTypeGeneral
def resource_type(json_list):
    for index, json_obj in enumerate(json_list):
            if "sm:Format" and "sm:Resource Type" in json_obj:
                resource_type = json_obj.pop("sm:Format")
                resource_type_general = json_obj.pop("sm:Resource Type")
                if resource_type_general in resource_type_lookup:
                    resource_type_general = resource_type_general.strip()
                    resource_type = resource_type.strip()
                    json_obj.setdefault("types", {})["resourceType"]=resource_type
                    json_obj.setdefault("types", {})["resourceTypeGeneral"]=resource_type_lookup[resource_type_general]
                else:
                    logging.warn(f"Resource type {resource_type_general} is not found in the lookup for row {index + 1}.")
            else:
                logging.info(f"sm: Format and/or sm:Format not found in row {index + 1}.")
    return json_list

#this function matches "sm:Creator" to creators and splits it.
def creators(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Creator" in json_obj:
            creators = json_obj.pop("sm:Creator").split("\n")
            for creator in creators:
                creator = creator.strip()
                parts = creator.split(",")
                
                if len(parts) == 2:
                        last_name, first_name = parts
                elif len(parts) > 2:
                    last_name, first_name = parts[0], " ".join(parts[1:])
                else:
                    logging.error(f"Unexpected format for creator: {creator}")
                    continue # Skip to the next creator
                
                if "|" in first_name:
                    first_name, ORCID = first_name.split("|")
                    ORCID = ORCID.strip()
                    if ORCID.startswith("https://orcid.org/"):
                        ORCID = ORCID.replace("https://orcid.org/", "")
                    json_obj.setdefault("creators", []).append({
                        "name": creator, 
                        "nameType": "Personal", 
                        "givenName": first_name.strip(), 
                        "familyName": last_name.strip(), 
                        "nameIdentifiers": [{
                            "nameIdentifier": ORCID, 
                            "nameIdentifierScheme": "ORCID", 
                            "schemeUri": "https://orcid.org/"}
                        ]})
                else:
                    json_obj.setdefault("creators", []).append({
                        "name": creator, 
                        "nameType": "Personal", 
                        "givenName": first_name.strip(), 
                        "familyName": last_name.strip()
                        })
        else:
            logging.info(f"sm:Creator not found for row {index + 1}.")
    return json_list

def process_corporate_field(json_list, field_name):
    for index, json_obj in enumerate(json_list):
        if field_name in json_obj:
            corporate_values = json_obj.pop(field_name).split("\n")
            logging.debug("My object is " + str(corporate_values))
            for corporate_value in corporate_values:
                corporate_value = corporate_value.strip()
                ror_id, ror_name = get_ror_info(corporate_value)
                
                # Now define the field_mapping using corporate_value
                field_mapping = {
                    "sm:Corporate Creator": {
                        "name": corporate_value,
                        "key": "creators",
                        "nameType": "Organizational",
                    },
                    "sm:Corporate Contributor": {
                        "name": corporate_value,
                        "key": "contributors",
                        "nameType": "Organizational",
                        "contributorType": "Sponsor",
                    },
                    # TODO: decouple this into a new method, should look like {"publisher": {"name": "..."}}
                    "sm:Corporate Publisher": {
                        "name": corporate_value,
                        "key": "publisher",
                    },
                }

                output_structure = field_mapping.get(field_name, {})
                
                if ror_id:
                    if field_name == "sm:Corporate Publisher":
                        entry = {
                            "name": ror_name,
                            "schemeUri": "https://ror.org/",
                            "publisherIdentifier": ror_id,
                            "publisherIdentifierScheme": "ROR"
                        }
                    elif field_name == "sm:Corporate Contributor":
                        entry = {
                            "name": ror_name,
                            "nameType": "Organizational",
                            "contributorType": "Sponsor",
                            "nameIdentifiers": [{
                                "schemeUri": "https://ror.org/",
                                "nameIdentifier": ror_id,
                                "nameIdentifierScheme": "ROR"}
                            ]
                        }
                    else:
                        entry = {
                            "name": ror_name,
                            "nameType": "Organizational",
                            "nameIdentifiers": [
                                {
                                    "schemeUri": "https://ror.org/",
                                    "nameIdentifier": ror_id,
                                    "nameIdentifierScheme": "ROR"
                                }
                            ]
                        }
                else:
                    entry = {
                        **{k: v for k, v in output_structure.items() if k != "key"}
                    }
                    logging.info(f"ROR for {corporate_value} not found for row {index + 1}.")
                    
                if field_name == "sm:Corporate Publisher":
                    json_obj[output_structure["key"]] = entry
                else:
                    json_obj.setdefault(output_structure["key"], []).append(entry)
        else:
            logging.info(f"{field_name} not found for row {index + 1}.")
    return json_list

# This function matches "sm:Contributor" to the contributors object list
def contributors(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Contributor" in json_obj:
            contributors = json_obj.pop("sm:Contributor").split("\n")
            for contributor in contributors:
                contributor = contributor.strip()
                last_name, first_name = contributor.split(",")
                last_name = last_name.strip()
                first_name = first_name.strip()
                if "|" in first_name:
                    first_name, ORCID = first_name.split("|")
                    ORCID = ORCID.strip()
                    json_obj.setdefault("contributors", []).append({
                        "name": contributor, 
                        "nameType": "Personal", 
                        "givenName": first_name, 
                        "familyName": last_name, 
                        "contributorType": "Researcher", 
                        "nameIdentifiers": [
                            {"nameIdentifier": ORCID, "nameIdentifierScheme": "ORCID", "schemeUri": "https://orcid.org/"}
                        ]})
                else:
                    json_obj.setdefault("contributors", []).append({
                        "name": contributor, 
                        "nameType": "Personal", 
                        "givenName": first_name, 
                        "contributorType": "Researcher",
                        "familyName": last_name})
        else:
            logging.info(f"sm:Contributor not found for row {index + 1}.")
    return json_list


                        
#this functions matches "sm:Contributor" to the contributors object list
def contributors(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Contributor" in json_obj:
            contributors = json_obj.pop("sm:Contributor").split("\n")
            for contributor in contributors:
                contributor = contributor.strip()
                last_name, first_name = contributor.split(",")
                last_name = last_name.strip()
                first_name = first_name.strip()
                if "|" in first_name:
                    first_name, ORCID = first_name.split("|")
                    ORCID = ORCID.strip()
                    json_obj.setdefault("contributors", []).append({
                        "name": contributor, 
                        "nameType": "Personal", 
                        "givenName": first_name, 
                        "familyName": last_name, 
                        "contributorType": "Researcher", 
                        "nameIdentifiers": [
                            {"nameIdentifier": ORCID, "nameIdentifierScheme": "ORCID", "schemeUri": "https://orcid.org/"}
                        ]})
                else:
                    json_obj.setdefault("contributors", []).append({
                        "name": contributor, 
                        "nameType": "Personal", 
                        "givenName": first_name, 
                        "contributorType": "Researcher",
                        "familyName": last_name})
        else:
            logging.info(f"sm:Contributor not found for row {index + 1}.")
    return json_list

#this function matches "sm:Key words" to subjects
def keywords(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Key words" in json_obj:
            keywords_str = json_obj.pop("sm:Key words")
            if keywords_str.endswith(", "):
                    keywords_str = keywords_str[:-2]
            keywords_str = keywords_str.split("\n")
            for keyword in keywords_str:
                keyword = keyword.strip()
                json_obj.setdefault("subjects", []).append({
                    "subject": keyword,
                    "schemeUri": "https://trt.trb.org/",
                    "subjectScheme": "Transportation Research Thesaurus"
                })
        else:
            logging.info(f"sm:Key words not found for row {index + 1}.")
    return json_list

#this function matches "sm:Report Number" to alternateIdentifier
def report_number(json_list):
    for json_obj in json_list:
        if "sm:Report Number" in json_obj:
            report_number = json_obj.pop("sm:Report Number")
            report_number = report_number.strip()
            json_obj.setdefault("alternateIdentifiers", []).append({
                "alternateIdentifier": report_number, 
                "alternateIdentifierType": "USDOT Report Number"
                })
    return json_list

#this function matches "Grants, Contracts, Cooperative Agreements" to alternateIdentifier
def contract_number(json_list):
    for json_obj in json_list:
        if "Grants, Contracts, Cooperative Agreements" in json_obj:
            contract_number = json_obj.pop("Grants, Contracts, Cooperative Agreements")
            contract_number = contract_number.strip()
            json_obj.setdefault("fundingReferences", []).append({
                "funderName": "U.S. Department of Transportation",
                "awardNumber": contract_number, 
                "funderIdentifier": "https://ror.org/02xfw2e90", 
                "funderIdentifierType": "ROR"
                })
    return json_list

#this function matches "sm:ResearchHub ID" to alternateIdentifier
def researchHub_id(json_list):
    for json_obj in json_list:
        if "sm:ResearchHub ID" in json_obj:
            researchhub_id = json_obj.pop("sm:ResearchHub ID")
            researchhub_id = researchhub_id.strip()
            json_obj.setdefault("alternateIdentifiers", []).append({
                "alternateIdentifier": researchhub_id, 
                "alternateIdentifierType": "USDOT ResearchHub Display ID"})
    return json_list

#this function matches "Content Notes" to "Descriptions"/TechnicalInfo
def content_notes(json_list):
    for json_obj in json_list:
        curation_note_level_b = "CoreTrustSeal's curation level \"B. Logical-Technical Curation.\""
        curation_note_level_a = "CoreTrustSeal's curation level \"A. Active Preservation\""
        if "Content Notes" in json_obj:
            content_note = json_obj.pop("Content Notes").strip()
            json_obj.setdefault("descriptions", []).append({
                "lang": "en", 
                "description": content_note, 
                "descriptionType": "TechnicalInfo"
                })
            if curation_note_level_b in content_note or curation_note_level_a in content_note:
                json_obj.setdefault("contributors", []).append({
                    "name": "Peyton Tvrdy", 
                    "nameType": "Personal", 
                    "givenName": "Peyton", 
                    "familyName": "Tvrdy", 
                    "contributorType": "DataCurator", 
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://orcid.org/0000-0002-9720-4725", "nameIdentifierScheme": "ORCID", "schemeUri": "https://orcid.org/"}
                    ]  
                })
    return json_list

#this function matches "Language" to language
def language(json_list):
    for index, json_obj in enumerate(json_list):
        if "Language" in json_obj:
            language = json_obj.pop("Language")
            language = language.strip()
            if language in language_dict:
                json_obj["language"]=language
            else:
                logging.warn(f"Language {language} not found in language dictionary for row {index + 1}.")
        else:
            logging.info(f"Language not found for row {index + 1}.")
    return json_list

#this function matches "Edition" to version
def edition(json_list):
    for json_obj in json_list:
        if "sm:Edition" in json_obj:
            version = json_obj.pop("sm:Edition")
            version = version.strip()
            json_obj["version"]=version
    return json_list

#this function matches Series and their DOIs to IsPartOf to the correct related identifier structure
def series(json_list):
    for index, json_obj in enumerate(json_list):
        if "Series Name" in json_obj:
            series_dois = json_obj.pop("Series Name").split("\n")
            for series_doi in series_dois:
                if series_doi in series_to_doi_lookup:
                    # Create a new DOI-related entry
                    doi_entry_series = {
                        "relatedIdentifierType": "DOI", 
                        "relatedIdentifier": series_to_doi_lookup[series_doi], 
                        "relationType": "IsPartOf",
                        "resourceTypeGeneral": "Collection"
                    }
                    # Initialize "related_identifiers" if not already present
                    json_obj.setdefault("relatedIdentifiers", []).append(doi_entry_series)
                else:
                    logging.warn(f"Series {series_doi} not found in series dictionary for row {index + 1}.")
    return json_list

#this function matches "Description" to "Descriptions"/Abstract
def description(json_list):
    for index, json_obj in enumerate(json_list):
        if "Description" in json_obj:
            description = json_obj.pop("Description")
            json_obj.setdefault("descriptions", []).append({
                "lang": "en", 
                "description": description, 
                "descriptionType": "Abstract"
                })
        else:
            logging.info(f"Description not found for row {index + 1}.")
    return json_list

# this function declares the schema version at the end of the payload. This statement is required for objects to be accepted by the DataCite API
def schema(json_list):
    for json_obj in json_list:
        json_obj['schemaVersion'] = "https://schema.datacite.org/meta/kernel-4.5/"
    return json_list

# this function wraps the entire payload in the "data" structure with the type of "dois". This also puts all the metadata created in the process into the object "attributes."
def wrap_object(json_list):
    output_list = list()
    for json_obj in json_list:
        output_obj = {"data": {"type": "dois", "attributes": json_obj}}
        output_list.append(output_obj)
    return output_list
