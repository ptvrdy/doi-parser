from constants import (
    collections_to_doi_lookup,
    series_to_doi_lookup,
    resource_type_lookup,
    language_dict,
    iana_mime_type_lookup
)

import logging
import pandas as pd

from utils import (
    get_ror_info,
    delete_unwanted
)

# logging.basicConfig(filename="process.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#this function removes unneeded columns from the CSV: "Main Document URL", "Supporting Documents URLs", "sm:Publisher", "Geographical Coverage", "sm:Rights Statement"
def delete_unwanted_columns(json_list):
    for json_obj in (json_list):
        delete_unwanted(json_obj, "Main Document URL")
        delete_unwanted(json_obj, "Supporting Documents URLs")
        delete_unwanted(json_obj, "sm:Publisher")
        delete_unwanted(json_obj, "sm:Geographical Coverage")
        delete_unwanted(json_obj, "Primary URL")
        delete_unwanted(json_obj, "Supporting Files")
        delete_unwanted(json_obj, "Personal Publisher(s)")
        delete_unwanted(json_obj, "Geographical Coverage")
    return json_list

#this function matches "Workroom ID" to Alternateidentifier
def workroom_id(json_list):
    for index, json_obj in enumerate(json_list):
        if "Workroom ID" in json_obj or "Workroom_ID" in json_obj:
            accession_number = json_obj.pop("Workroom ID", json_obj.pop("Workroom_ID", None))
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
    
#this function matches "ISSN" to Alternateidentifier
def issn_number(json_list):
    for json_obj in json_list:
        if "ISSN" in json_obj:
            issn = json_obj.pop("ISSN")
            json_obj.setdefault("alternateIdentifiers", []).append({
                "alternateIdentifier": issn,
                "alternateIdentifierType": "ISSN"
            })
    
#this function matches "ROSAP URLs" to url
def rosap_url(json_list):
    for index, json_obj in enumerate(json_list):
        rosap_key = None
        for candidate_key in ("ROSAP URLs", "ROSAP_URL", "ROSAP URL", "ROSAP_URLs"):
            if candidate_key in json_obj:
                rosap_key = candidate_key
                break
        if rosap_key is not None:
            url = json_obj.pop(rosap_key)
            json_obj["url"] = url
            if "https://highways.dot.gov/" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "Federal Highway Administration", 
                    "nameType": "Organizational", 
                    "contributorType": "HostingInstitution", 
                    "lang": "en", 
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://ror.org/0473rr271", 
                         "nameIdentifierScheme": "ROR", 
                         "schemeUri": "https://ror.org/"}
                    ]
                })
            elif "https://cms.fhwa.dot.gov/" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "Federal Highway Administration", 
                    "nameType": "Organizational", 
                    "contributorType": "HostingInstitution", 
                    "lang": "en", 
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://ror.org/0473rr271", 
                         "nameIdentifierScheme": "ROR", 
                         "schemeUri": "https://ror.org/"}
                    ]
                })
            elif "geodata.bts.gov" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "Bureau of Transportation Statistics",
                    "nameType": "Organizational",
                    "contributorType": "HostingInstitution",
                    "lang": "en",
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://ror.org/05xfdey77",
                         "nameIdentifierScheme": "ROR",
                         "schemeUri": "https://ror.org/"}
                    ]
                })
            elif "https://services.arcgis.com" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "Bureau of Transportation Statistics",
                    "nameType": "Organizational",
                    "contributorType": "HostingInstitution",
                    "lang": "en",
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://ror.org/05xfdey77",
                         "nameIdentifierScheme": "ROR",
                         "schemeUri": "https://ror.org/"}
                    ]
                })
            elif "https://rosap.ntl.bts.gov/" in url:
                json_obj.setdefault("contributors", []).append({
                    "name": "National Transportation Library", 
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
        if "sm:Collection" in json_obj or "Collection(s) in json_obj":
            collections = json_obj.pop("sm:Collection", json_obj.pop("Collection(s)", ""))
            collections = collections.split(";") if collections else []
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
        elif json_obj.get("Digital Object Identifier") and json_obj['Digital Object Identifier'].strip():
            sm_digital_object_identifier(json_obj)
        else:
            logging.info(f"Setting to draft state for row {i}")
            draft_state(json_obj)
    return json_list

#this function matches "sm:Digital Object Identifier" to doi, prefix and id
def sm_digital_object_identifier(json_obj):
    doi = json_obj.pop("sm:Digital Object Identifier", json_obj.pop("Digital Object Identifier", None))
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
        if "Alternative Title" in json_obj or "Alternate Title" in json_obj:
            alt_title = json_obj.pop("Alternative Title", json_obj.pop("Alternate Title", None))
            json_obj.setdefault("titles", []).append({
                "title": alt_title, 
                "titleType": "AlternativeTitle", 
                "lang": "en"
                })
    return json_list
        
#this function matches "Published Date" to Publication Year, Date, and dateType
def publication_date(json_list):
    for index, json_obj in enumerate(json_list):
        date = json_obj.pop("Published Date", json_obj.pop("Publication Date", None))
        json_obj.setdefault("dates", []).append({"date": date, "dateType": "Issued"})
        published_year = date[:4]
        json_obj["publicationYear"] = int(published_year)
    return json_list

#this function matches "sm:Format" to ResourceType and resourceTypeGeneral
def resource_type(json_list):
    for index, json_obj in enumerate(json_list):
            if "sm:Format" and "sm:Resource Type" in json_obj or "Format" and "Resource Type" in json_obj:
                format_type = json_obj.pop("sm:Format", json_obj.pop("Format", ""))
                resource_type = json_obj.pop("sm:Resource Type", json_obj.pop("Resource Type", None))
                resource_type_general = json_obj.pop("sm:Resource Type", json_obj.pop("Resource Type", None))
                if resource_type_general in resource_type_lookup:
                    resource_type_general = resource_type_general.strip()
                    resource_type = resource_type.strip()
                    json_obj.setdefault("types", {})["resourceType"]=resource_type
                    json_obj.setdefault("types", {})["resourceTypeGeneral"]=resource_type_lookup[resource_type_general]
                    if format_type in iana_mime_type_lookup:
                        json_obj.setdefault("formats", []).append(iana_mime_type_lookup[format_type])
                    else:
                        logging.warn(f"Format {format_type} is not found in the lookup for row {index +1}.")
                else:
                    logging.warn(f"Resource type {resource_type_general} is not found in the lookup for row {index + 1}.")
            else:
                logging.info(f"sm: Format and/or sm:Format not found in row {index + 1}.")
    return json_list

#this function matches "sm:Creator" to creators and splits it.
def creators(json_list):
    for index, json_obj in enumerate(json_list):
        # Retrieve the contracting officer names for this row
        officer_names = set(json_obj.get("_contracting_officer_names", [])) 
        
        if "sm:Creator" in json_obj or "Personal Creator(s)" in json_obj:
            creators = json_obj.pop("sm:Creator", json_obj.pop("Personal Creator(s)", ""))
            creators = creators.split("\n") if creators else []
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
                
                first_name = first_name.strip()
                last_name = last_name.strip()
                
                ORCID = None
                if "|" in first_name:
                    first_name, ORCID = first_name.split("|")
                    ORCID = ORCID.strip()
                    if ORCID.startswith("(ORCID: "):
                        ORCID = ORCID.replace("(ORCID: ","")
                    if not ORCID.startswith("https://orcid.org/"):
                        ORCID = "https://orcid.org/" + ORCID
                
                # Skip if the creator is already a contracting officer
                if (last_name, first_name) in officer_names:
                    logging.info(f"Skipping duplicate creator '{first_name} {last_name}' (already a contracting officer).")
                    continue
                
                entry = {
                    "name": last_name.strip() + ", " + first_name.strip(),
                    "nameType": "Personal", 
                    "givenName": first_name, 
                    "familyName": last_name, 
                }
                
                if ORCID is not None:
                    entry['nameIdentifiers'] = [
                        {
                        "nameIdentifier": ORCID, 
                        "nameIdentifierScheme": "ORCID", 
                        "schemeUri": "https://orcid.org/"
                        }
                    ]
                json_obj.setdefault("creators", []).append(entry)
                
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

def contracting_officer(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Contracting Officer" in json_obj or "Contracting Officer" in json_obj:
            contracting_officers = json_obj.pop("sm:Contracting Officer", json_obj.pop("Contracting Officer", ""))
            contracting_officers = contracting_officers.strip()
            contracting_officers = contracting_officers.replace(";", "\n").split("\n") if contracting_officers else []
            
            # Store contracting officer names for deduplication
            officer_names = set()

            for contracting_officer in contracting_officers:
                contracting_officer = contracting_officer.strip()
                last_name, first_name = contracting_officer.split(",")
                last_name = last_name.strip()
                first_name = first_name.strip()

                if "|" in first_name:
                    first_name, ORCID = first_name.split("|")
                    ORCID = ORCID.strip()
                    if ORCID.startswith("(ORCID: "):
                        ORCID = ORCID.replace("(ORCID: ","")
                    if not ORCID.startswith("https://orcid.org/"):
                        ORCID = "https://orcid.org/" + ORCID
                    json_obj.setdefault("contributors", []).append({
                        "name": last_name.strip() + ", " + first_name.strip(),
                        "nameType": "Personal",
                        "givenName": first_name,
                        "familyName": last_name,
                        "contributorType": "Other",
                        "nameIdentifiers": [
                            {"nameIdentifier": ORCID, "nameIdentifierScheme": "ORCID", "schemeUri": "https://orcid.org/"}
                        ]})
                else:
                    json_obj.setdefault("contributors", []).append({
                        "name": contracting_officer,
                        "nameType": "Personal",
                        "givenName": first_name,
                        "familyName": last_name,
                        "contributorType": "Other"
                    })
                officer_names.add((last_name, first_name))  # Add to deduplication set

            # Store contracting officers in the JSON for access in other functions
            json_obj["_contracting_officer_names"] = list(officer_names)  # Convert set to list
        else:
            logging.info(f"sm:Contracting Officer not found for row {index + 1}.")
    return json_list


def contributors(json_list):
    for index, json_obj in enumerate(json_list):
        # Retrieve the contracting officer names for this row
        officer_names = set(json_obj.get("_contracting_officer_names", [])) 

        if "sm:Contributor" in json_obj or "Personal Contributor(s)" in json_obj:
            contributors = json_obj.pop("sm:Contributor", json_obj.pop("Personal Contributor(s)", ""))
            contributors = contributors.split("\n") if contributors else []

            for contributor in contributors:
                contributor = contributor.strip()
                last_name, first_name = contributor.split(",")
                last_name = last_name.strip()
                first_name = first_name.strip()

                ORCID = None
                if "|" in first_name:
                    first_name, ORCID = first_name.split("|")
                    ORCID = ORCID.strip()
                    if ORCID.startswith("(ORCID: "):
                        ORCID = ORCID.replace("(ORCID: ","")
                    if not ORCID.startswith("https://orcid.org/"):
                        ORCID = "https://orcid.org/" + ORCID
                    
                    
                # Skip if the contributor is already a contracting officer
                if (last_name, first_name) in officer_names:
                    logging.info(f"Skipping duplicate contributor '{first_name} {last_name}' (already a contracting officer).")
                    continue
                
                entry = {
                    "name": last_name.strip() + ", " + first_name.strip(),
                    "nameType": "Personal",
                    "givenName": first_name.strip(),
                    "familyName": last_name,
                    "contributorType": "Researcher",
                }
                
                if ORCID is not None:
                    entry['nameIdentifiers'] = [
                        {"nameIdentifier": ORCID, "nameIdentifierScheme": "ORCID", "schemeUri": "https://orcid.org/"}
                    ]
                json_obj.setdefault("contributors", []).append(entry)
        else:
            logging.info(f"sm:Contributor not found for row {index + 1}.")
    return json_list


#loading TRT file
file_path_trt = "TRT/TRT - Export 20241028.xlsx"
trt_data = pd.read_excel(file_path_trt)

# Combining all "Concept" columns (B to M) to find the first non-empty term, bypassing hierarchy
concept_columns = trt_data.loc[:, 'concept':'concept.11'] 

# Apply a function that finds the first non-empty value in each row of concept columns
trt_data['concept'] = concept_columns.apply(lambda row: next((term for term in row if pd.notna(term)), None), axis=1)

# Extracting needed columns for term and URI, replaces URI from Closed Pool Party API Link to Public Terms URI
trt_terms_df = trt_data[['uri', 'concept']].dropna(subset=['uri', 'concept'])
trt_terms_df['uri'] = trt_terms_df['uri'].str.replace(
    "https://km.nationalacademies.org/TRT-developmentv6/",
    "https://trt.trb.org/term/"
)

# Creating a keywords dictionary with TRT term validation and adding URI classificationCode
trt_lookup = dict(zip(trt_terms_df['concept'].str.strip().str.lower(), trt_terms_df['uri']))

def keywords(json_list):
    for index, json_obj in enumerate(json_list):
        if "sm:Key words" in json_obj or "Keywords (TRT Term(s) and Subject Keywords concatenated)" in json_obj:
            keywords_str = json_obj.pop("sm:Key words", json_obj.pop("Keywords (TRT Term(s) and Subject Keywords concatenated)", None))
            if keywords_str.endswith(", "):
                    keywords_str = keywords_str[:-2]
            if ", " in keywords_str:
                keywords_str = keywords_str.replace(", ", "\n").strip()
            keywords_str = keywords_str.split("\n")
            for keyword in keywords_str:
                keyword = keyword.strip()
                trt_code = trt_lookup.get(keyword.lower())
                if trt_code:
                    json_obj.setdefault("subjects", []).append({
                        "subject": keyword,
                        "schemeUri": "https://trt.trb.org/",
                        "subjectScheme": "Transportation Research Thesaurus",
                        "classificationCode": trt_code
                    })
                else: logging.info(f"Term '{keyword}' is not found in the TRT and was excluded.")
        else: 
            logging.info(f"sm:Key words not found for row {index + 1}.")
    return json_list

#this function matches "sm:Report Number" to alternateIdentifier
def report_number(json_list):
    for json_obj in json_list:
        if "sm:Report Number" in json_obj or "Report Number(s)" in json_obj:    
            report_numbers = json_obj.pop("sm:Report Number", json_obj.pop("Report Number(s)", None))
            report_numbers = report_numbers.strip()
            report_numbers = report_numbers.split(";")
            for report_number in report_numbers:
                report_number = report_number.strip()
                json_obj.setdefault("alternateIdentifiers", []).append({
                    "alternateIdentifier": report_number, 
                    "alternateIdentifierType": "USDOT Report Number"
                })
    return json_list

#this function matches "Grants, Contracts, Cooperative Agreements" to alternateIdentifier
def contract_number(json_list):
    for json_obj in json_list:
        if "Grants, Contracts, Cooperative Agreements" in json_obj or "Contract Number(s)" in json_obj:
            contract_numbers = json_obj.pop("Grants, Contracts, Cooperative Agreements", json_obj.pop("Contract Number(s)", ""))
            contract_numbers = contract_numbers.strip()
            contract_numbers = contract_numbers.split(";")
            for contract_number in contract_numbers:
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
        if "sm:ResearchHub ID" in json_obj or "ResearchHub ID" in json_obj:
            researchhub_id = json_obj.pop("sm:ResearchHub ID", json_obj.pop("ResearchHub ID", None))
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
        if "Content Notes" in json_obj or "Public Note" in json_obj:
            content_note = json_obj.pop("Content Notes", json_obj.pop("Public Note", None)).strip()
            json_obj.setdefault("descriptions", []).append({
                "lang": "en", 
                "description": content_note, 
                "descriptionType": "TechnicalInfo"
                })
            if curation_note_level_b in content_note or curation_note_level_a in content_note:
                json_obj.setdefault("contributors", []).append({
                    "name": "Tvrdy, Peyton", 
                    "nameType": "Personal", 
                    "givenName": "Peyton", 
                    "familyName": "Tvrdy", 
                    "contributorType": "DataCurator", 
                    "nameIdentifiers": [
                        {"nameIdentifier": "https://orcid.org/0000-0002-9720-4725", "nameIdentifierScheme": "ORCID", "schemeUri": "https://orcid.org/"}
                    ]  
                })
    return json_list

# this function matches Rights Statements to licenses
def rights(json_list):
    for index, json_obj in enumerate(json_list):
        rights_key = None
        for candidate_key in ("sm:Rights Statement", "Rights Statement", "Rights_Statement", "Copyright"):
            if candidate_key in json_obj:
                rights_key = candidate_key
                break
        if rights_key is not None:
            rights = json_obj.pop(rights_key)
            if "Attribution 4.0 International" in rights or "https://creativecommons.org/licenses/by/4.0/" in rights:
                json_obj.setdefault("rightsList", []).append({
                    "rights": "Creative Commons Attribution 4.0 International",
                    "rightsUri": "https://creativecommons.org/licenses/by/4.0/legalcode",
                    "schemeUri": "https://spdx.org/licenses/",
                    "rightsIdentifier": "cc-by-4.0",
                    "rightsIdentifierScheme": "SPDX"
                    })
            elif "Zero" in rights or "https://creativecommons.org/publicdomain/zero/1.0/legalcode" in rights:
                json_obj.setdefault("rightsList", []).append({
                    "rights": "Creative Commons Zero v1.0 Universal",
                    "rightsUri": "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
                    "schemeUri": "https://spdx.org/licenses/",
                    "rightsIdentifier": "cc0-1.0",
                    "rightsIdentifierScheme": "SPDX"
                    })
            elif "Public Domain" in rights or "Open Access" in rights:
                json_obj.setdefault("rightsList", []).append({
                    "rights": "Creative Commons Public Domain Dedication and Certification",
                    "rightsUri": "https://creativecommons.org/publicdomain/mark/1.0/deed.en",
                    "schemeUri": "https://spdx.org/licenses/",
                    "rightsIdentifier": "cc-pdm-1.0",
                    "rightsIdentifierScheme": "SPDX"
                })
            else:
                logging.info(f"No license or rights statement for row {index + 1}.")
    return json_list
                
#this function matches "Language" to language
def language(json_list):
    for index, json_obj in enumerate(json_list):
        if "Language" in json_obj or "Language(s)" in json_obj:
            language = json_obj.pop("Language", json_obj.pop("Language(s)", None))
            language = language.strip()
            if language in language_dict:
                json_obj["language"]=language_dict[language]
            else:
                logging.warn(f"Language {language} not found in language dictionary for row {index + 1}.")
        else:
            logging.info(f"Language not found for row {index + 1}.")
    return json_list

#this function matches "Edition" to version
def edition(json_list):
    for json_obj in json_list:
        if "sm:Edition" in json_obj or "Edition" in json_obj:
            version = json_obj.pop("sm:Edition", json_obj.pop("Edition", None))
            version = version.strip()
            json_obj["version"]=version
    return json_list

#this function matches Series and their DOIs to IsPartOf to the correct related identifier structure
def series(json_list):
    for index, json_obj in enumerate(json_list):
        if "Series Name" in json_obj or "Is Part of" in json_obj:
            series_dois = json_obj.pop("Series Name", json_obj.pop("Is Part of", ""))
            series_dois = series_dois.split("\n") if series_dois else []
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
        require("types" in json_obj, "Resource Type wasn't called yet")
        if "Description" in json_obj or "Abstract" in json_obj:
            description = json_obj.pop("Description", json_obj.pop("Abstract", None))
            if "resourceTypeGeneral" == "Collection":
                json_obj.setdefault("descriptions", []).append({
                "lang": "en", 
                "description": description, 
                "descriptionType": "SeriesInformation"
                })
            else:
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
        json_obj['schemaVersion'] = "https://schema.datacite.org/meta/kernel-4.6/"
    return json_list

# This function will drop unnecessary information
def drop_and_pop(json_list):
    for json_obj in json_list:
        if "_contracting_officer_names" in json_obj:
            json_obj.pop("_contracting_officer_names")
    return json_list

# this function wraps the entire payload in the "data" structure with the type of "dois". This also puts all the metadata created in the process into the object "attributes."
def wrap_object(json_list):
    output_list = list()
    for json_obj in json_list:
        output_obj = {"data": {"type": "dois", "attributes": json_obj}}
        output_list.append(output_obj)
    return output_list

def require(condition, description):
    if not condition:
        raise Exception(description)