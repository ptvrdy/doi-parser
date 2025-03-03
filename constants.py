LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s"

API_URL_Lookup = {
    "API_URL": "https://api.dev.ror.org/v2/organizations",
}
organization_to_ror_lookup = {
    "United States. Department of Transportation": "https://ror.org/02xfw2e90",
    "United States. Department of Transportation. Federal Aviation Administration": "https://ror.org/05q0y0j38",
    "United States. Department of Transportation. Federal Highway Administration": "https://ror.org/0473rr271",
    "United States. Department of Transportation. Federal Railroad Administration": "https://ror.org/0275ebj77",
    "United States. Department of Transportation. Federal Transit Administration": "https://ror.org/01mg0yh05",
    "United States. Department of Transportation. National Highway Traffic Safety Administration": "https://ror.org/04gcfqs37",
    "United States. Department of Transportation. United States Maritime Administration": "https://ror.org/055hae320",
    "United States. Department of Transportation. Volpe National Transportation Systems Center": "https://ror.org/04a2k6j28",
    "United States. Department of Transportation. Federal Motor Carrier Safety Administration": "https://ror.org/01jt5mq34",
    "United States. Department of Transportation. Bureau of Transportation Statistics": "https://ror.org/05xfdey77",
    "United States. Department of Transportation. Office of the Assistant Secretary for Research and Technology": "https://ror.org/0150hkx05",
    "United States. Department of Transportation. Intelligent Transportation Systems Joint Program Office": "https://ror.org/012cshy85",
    "United States. Department of Transportation. University Transportation Centers (UTC) Program": "https://ror.org/02jf59s11",
    "United States. Department of Transportation. National Transportation Library": "https://ror.org/00snbrd52",
    "United States. Department of Transportation. Federal Highway Administration. Turner-Fairbank Highway Research Center": "https://ror.org/04edx5729",
    "United States. Department of Transportation. Federal Aviation Administration. Office of Aviation. Civil Aerospace Medical Institute": "https://ror.org/043e04s74",
}
collections_to_doi_lookup = {
    "Advisory Circulars": "https://doi.org/10.21949/1530859", 
    "Air Quality + Sustainable Transportation Highlights": "https://doi.org/10.21949/y3r3-3y74",
    "Attitudes and Behavior Surveys": "https://doi.org/10.21949/45f6-zs20",
    "BTS Data Spotlight": "https://doi.org/10.21949/e6w2-7784",
    "BTS Ports": "https://doi.org/10.21949/1530821",
    "BTS Products": "https://doi.org/10.21949/1530822",
    "CAA and FAA Reports (CAAFAA)": "https://doi.org/10.21949/1530064",
    "Civil Aeronautics Manuals": "https://doi.org/10.21949/1530823",
    "Civil Aeronautics Regulations": "https://doi.org/10.21949/1530824",
    "Civil Aerospace Medical Institute": "https://doi.org/10.21949/1530825",
    "Climate Change Clearinghouse": "https://doi.org/10.21949/1530826",
    "Committee on the Marine Transportation System": "https://doi.org/10.21949/1530827",
    "Commodity Flow Survey": "https://doi.org/10.21949/1530828",
    "FAA Advisory Circulars": "https://doi.org/10.21949/1530829",
    "FAA Technical Library": "https://doi.org/10.21949/1530830",
    "Federal Aviation Administration": "https://doi.org/10.21949/1530831",
    "Federal Aviation Regulations": "https://doi.org/10.21949/1530860",
    "Federal Committee on Statistical Methodology": "https://doi.org/10.21949/1530832",
    "Federal Highway Administration": "https://doi.org/10.21949/1530833",
    "Federal Lands": "https://doi.org/10.21949/1530834",
    "Federal Railroad Administration": "https://doi.org/10.21949/1530835",
    "Federal Transit Administration": "https://doi.org/10.21949/1530836",
    "Federal Transit Administration 50th Anniversary (FTA 50)": "https://doi.org/10.21949/1530837",
    "FHWA's Fostering Multimodal Connectivity Newsletter": "https://doi.org/10.21949/0v1v-7343",
    "FHWA Highway History Website Articles": "https://doi.org/10.21949/hs6z-gp46",
    "Focus: Accelerating Infrastructure Innovations": "https://doi.org/10.21949/b8c6-qg59",
    "Freight Analysis Framework (FAF)": "https://doi.org/10.21949/eett-f241",
    "Highway Statistics Series: State Statistical Abstracts": "https://doi.org/10.21949/xjbx-6t40",
    "Historic Cab/Dot Orders": "https://doi.org/10.21949/1530861",
    "Innovator": "https://doi.org/10.21949/rqd2-ad80",
    "Intelligent Transportation Systems Joint Program Office": "https://doi.org/10.21949/1530838",
    "Investigations of Aircraft Accidents 1934-1965": "https://doi.org/10.21949/1530839",
    "Investigations of Railroad Accidents 1911-1993": "https://doi.org/10.21949/1530840",
    "ITS4US Phase 1": "https://doi.org/10.21949/x19d-9098",
    "ITS4US Phase 2 and Phase 3": "https://doi.org/10.21949/hkw8-hs16",
    "Manual on Uniform Traffic Control Devices for Streets and Highways": "https://doi.org/10.21949/e6ym-4204",
    "Maritime Administration": "https://doi.org/10.21949/1530862",
    "Memoranda & Guidance: Guidance": "https://doi.org/10.21949/tt5v-eh10",
    "National Conferences on Street and Highway Safety": "https://doi.org/10.21949/1530841",
    "National Transportation Atlas Database Archive": "https://doi.org/10.21949/1530842",
    "National Transportation Data Archive": "https://doi.org/10.21949/1504517",
    "News Releases and Newsletters": "https://doi.org/10.21949/1530063",
    "NHTSA - Behavioral Safety Research (NHTSA-BSR)": "https://doi.org/10.21949/1530843",
    "NHTSA - Behavioral Safety Research": "https://doi.org/10.21949/1530843", 
    "NHTSA BSR Countermeasures That Work": "https://doi.org/10.21949/rv1b-xg46",
    "NHTSA BSR Motor Vehicle Occupant Safety Survey": "https://doi.org/10.21949/r97k-9s30",
    "NHTSA BSR Traffic Safety Facts": "https://doi.org/10.21949/vtcz-qs22",
    "NHTSA BSR Traffic Tech": "https://doi.org/10.21949/e7xd-w126",
    "NHTSA - Vehicle Safety Research (NHTSA-VSR)": "https://doi.org/10.21949/1530844",
    "NHTSA-Vehicle Safety Research": "https://doi.org/10.21949/1530844",
    "NTL Publications": "https://doi.org/10.21949/1530845",
    "Papers by H.S. Fairbank - Frank Turner - T.H. Macdonald - (FTMPAPERS) (PBHF-FT-TM-F)": "https://doi.org/10.21949/1530846",
    "Pedestrian & Bike Forum Newsletter": "https://doi.org/10.21949/k6bx-0n11",
    "Pipeline and Hazardous Materials Safety Administration": "https://doi.org/10.21949/1530847",
    "Ports Resilience": "https://doi.org/10.21949/9tbf-2k24",
    "Public Access Resources": "https://doi.org/10.21949/1530848",
    "Public Roads": "https://doi.org/10.21949/1530849",
    "Realty Digest": "https://doi.org/10.21949/mh90-5s37",
    "Research & Technology Transporter": "https://doi.org/10.21949/0dhv-ek51",
    "Retiree Memoirs": "https://doi.org/10.21949/frsd-vv13",
    "Roadside and Crash Risk Studies": "https://doi.org/10.21949/arkv-0k07",
    "Safety Compass Newsletter": "https://doi.org/10.21949/nsh6-b216",
    "Secretary of Transportation Speeches": "https://doi.org/10.21949/1530850",
    "Special Issue - Weekly Motor Fuel Report": "https://doi.org/10.21949/ssbv-9r29",
    "Successes in Stewardship Newsletter": "https://doi.org/10.21949/zv5p-jf66",
    "State Road Maps": "https://doi.org/10.21949/1530851",
    "Texas Road Maps": "https://doi.org/10.21949/2rwc-j622",
    "Transportation Librarians Roundtable": "https://doi.org/10.21949/1530852",
    "United States Federal Motor Carrier Safety Administration": "https://doi.org/10.21949/1530853",
    "University Transportation Centers Program": "https://doi.org/10.21949/1530855",
    "US DOT Public Access Data Management Plans": "https://doi.org/10.21949/1530854",
    "US Transportation Collection": "https://doi.org/10.21949/1530855",
    "US Coast Guard Circulars": "https://doi.org/10.21949/1530856",
    "US Transportation Collection": "https://doi.org/10.21949/1530857",
    "Volpe Center Annual Accomplishments": "https://doi.org/10.21949/dwez-p084",
    "Volpe National Transportation Systems Center, Technical Reference Center": "https://doi.org/10.21949/1530858",
}
series_to_doi_lookup = {
    "Adams, Brock": "https://doi.org/10.21949/6n28-0t42",
    "Air Carrier Traffic Statistics (Green Book)": "https://doi.org/10.21949/9v8v-2z95",
    "Air Travel Consumer Report [Series]": "https://doi.org/10.21949/1530604",
    "Amendments": "https://doi.org/10.21949/x6ad-nt93",
    "Annual Reports of the Maritime Administration": "https://doi.org/10.21949/jp4q-2g37",
    "Boyd, Alan S. ": "https://doi.org/10.21949/1530067",
    "Boyd, Alan S.": "https://doi.org/10.21949/1530067",
    "Brinegar, Claude S.": "https://doi.org/10.21949/337m-q618",
    "Card, Andrew": "https://doi.org/10.21949/netv-sm71",
    "Civil Aeronautics Administration Reports": "https://doi.org/10.21949/cqtp-cp64",
    "Coleman, William T., Jr.": "https://doi.org/10.21949/zpyh-yn79",
    "Dole, Elizabeth Hanford": "https://doi.org/10.21949/dbhc-mv55",
    "Domestic Airline Fares Consumer Report": "https://doi.org/10.21949/kbe4-vy59",
    "Federal Aviation Regulations Amendments": "https://doi.org/10.21949/x6ad-nt93",
    "Federal Aviation Regulations Final Rule": "https://doi.org/10.21949/q598-f030",
    "FHWA R&T Now": "https://doi.org/10.21949/t5k5-mw25",
    "Final Rule": "https://doi.org/10.21949/q598-f030",
    "Fleet Composition of Rail Tank Cars Carrying Flammable Liquids": "https://doi.org/10.21949/1503662",
    "Goldschmidt, Neil": "https://doi.org/10.21949/d4sv-tn50",
    "Lewis, Andrew Lindsay, Jr.": "https://doi.org/10.21949/y3a2-6737",
    "Metrics of Success Series": "https://doi.org/10.21949/pepf-n503",
    "National Census of Ferry Operators (NCFO)": "https://doi.org/10.21949/5qbs-gt76",
    "National Transportation Atlas Database (NTAD)": "https://doi.org/10.21949/1524551",
    "OST-R Research Roundup": "https://doi.org/10.21949/ctgz-8g63",
    "Pena, Federico": "https://doi.org/10.21949/hwt7-nd45",
    "Pocket Guide to Transportation": "https://doi.org/10.21949/1503656",
    "Skinner, Samuel": "https://doi.org/10.21949/6qc0-gt15",
    "Slater, Rodney": "https://doi.org/10.21949/r2y9-nd59",
    "Special Federal Aviation Regulations": "https://doi.org/10.21949/b9d0-1n60",
    "Trapline": "https://doi.org/10.21949/sfde-je37",
    "Volpe, John A.": "https://doi.org/10.21949/1530983",
    "Vehicle Inventory and Use Survey (VIUS)": "https://doi.org/10.21949/1524559",
    "What Do Americans Think About Federal Tax Options to Support Transportation?": "https://doi.org/10.21949/1531029",
}
resource_type_lookup = {
    "Analytic Code": "Software",
    "Application": "Software",
    "Audio": "Sound",
    "Bibliography": "Text",
    "Book": "Book",
    "Booklet/Pamphlet": "Text",
    "Brief": "Text",
    "Collection": "Collection",
    "Data Management Plan": "OutputManagementPlan",
    "Dataset": "Dataset",
    "Dissertation": "Dissertation",
    "Event": "Event",
    "Example": "Other",
    "Geospatial Files": "Dataset",
    "Image": "Image",
    "InBook": "BookChapter",
    "InCollection": "BookChapter",
    "InProceedings": "ConferencePaper",
    "InteractiveResource": "InteractiveResource",
    "Journal": "Journal",
    "Journal Article": "JournalArticle",
    "Letter": "Text",
    "Magazine": "Text",
    "Manual": "Standard",
    "Manuscript": "Text",
    "Map": "Image",
    "Memorandum": "Text",
    "Message": "Text",
    "Model": "Model",
    "Multipart": "Collection",
    "Newsletters": "Text",
    "Newspaper": "Text",
    "Organization Info": "Other",
    "Other": "Other",
    "Personal Info": "Other",
    "Policy Statement": "Standard",
    "Presentations": "Audiovisual",
    "Press Release": "Text",
    "Proceedings": "ConferenceProceedings",
    "Research Paper": "Report",
    "Series": "Collection",
    "Simulation": "Model",
    "Software": "Software",
    "Speeches": "Other",
    "Statistical Report": "Report",
    "Tech Report": "Report",
    "Text": "Text",
    "Thesis": "Dissertation",
    "Video": "Audiovisual",
    "Web Document": "Text",
}
iana_mime_type_lookup = {
    "AVI": "video/x-msvideo",
    "CSV": "text/csv",
    "DOC": "application/msword",
    "HTML": "text/html",
    "JPEG": "image/jpeg",
    "MPEG": "video/mpeg",
    "PDF": "application/pdf",
    "PNG": "image/png",
    "PPT": "application/vnd.ms-powerpoint",
    "PPTX": "application/vnd.ms-powerpoint",
    "Raster": "image/pwg-raster",
    "RTF": "text/rtf",
    "Shapefiles": "application/x-shapefile",
    "SWF": "video/vnd.sealed.swf",
    "TIFF": "application/vnd.sealed.tiff",
    "TXT": "text/plain",
    "Vector": "application/geo+json",
    "WMA": "audio/x-ms-wma",
    "WMV": "video/x-ms-wmv",
    "XLS": "application/vnd.ms-excel",
    "XLSX": "application/vnd.ms-excel",
    "XML": "text/xml",
    "ZIP": "application/zip",
}
language_dict = {
    "Abkhazian": "ab",
    "Afar": "aa",
    "Afrikaans": "af",
    "Akan": "ak",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Aragonese": "an",
    "Armenian": "hy",
    "Assamese": "as",
    "Avaric": "av",
    "Avestan": "ae",
    "Aymara": "ay",
    "Azerbaijani": "az",
    "Bambara": "bm",
    "Bashkir": "ba",
    "Basque": "eu",
    "Belarusian": "be",
    "Bengali": "bn",
    "Bislama": "bi",
    "Bosnian": "bs",
    "Breton": "br",
    "Bulgarian": "bg",
    "Burmese": "my",
    "Catalan, Valencian": "ca",
    "Chamorro": "ch",
    "Chechen": "ce",
    "Chichewa, Chewa, Nyanja": "ny",
    "Chinese": "zh",
    "Church Slavonic, Old Slavonic, Old Church Slavonic": "cu",
    "Chuvash": "cv",
    "Cornish": "kw",
    "Corsican": "co",
    "Cree": "cr",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Divehi, Dhivehi, Maldivian": "dv",
    "Dutch, Flemish": "nl",
    "Dzongkha": "dz",
    "English": "en",
    "Esperanto": "eo",
    "Estonian": "et",
    "Ewe": "ee",
    "Faroese": "fo",
    "Fijian": "fj",
    "Finnish": "fi",
    "French": "fr",
    "Western Frisian": "fy",
    "Fulah": "ff",
    "Gaelic, Scottish Gaelic": "gd",
    "Galician": "gl",
    "Ganda": "lg",
    "Georgian": "ka",
    "German": "de",
    "Greek, Modern (1453–)": "el",
    "Kalaallisut, Greenlandic": "kl",
    "Guarani": "gn",
    "Gujarati": "gu",
    "Haitian, Haitian Creole": "ht",
    "Hausa": "ha",
    "Hebrew": "he",
    "Herero": "hz",
    "Hindi": "hi",
    "Hiri Motu": "ho",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Ido": "io",
    "Igbo": "ig",
    "Indonesian": "id",
    "Interlingua (International Auxiliary Language Association)": "ia",
    "Interlingue, Occidental": "ie",
    "Inuktitut": "iu",
    "Inupiaq": "ik",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jv",
    "Kannada": "kn",
    "Kanuri": "kr",
    "Kashmiri": "ks",
    "Kazakh": "kk",
    "Central Khmer": "km",
    "Kikuyu, Gikuyu": "ki",
    "Kinyarwanda": "rw",
    "Kirghiz, Kyrgyz": "ky",
    "Komi": "kv",
    "Kongo": "kg",
    "Korean": "ko",
    "Kuanyama, Kwanyama": "kj",
    "Kurdish": "ku",
    "Lao": "lo",
    "Latin": "la",
    "Latvian": "lv",
    "Limburgan, Limburger, Limburgish": "li",
    "Lingala": "ln",
    "Lithuanian": "lt",
    "Luba-Katanga": "lu",
    "Luxembourgish, Letzeburgesch": "lb",
    "Macedonian": "mk",
    "Malagasy": "mg",
    "Malay": "ms",
    "Malayalam": "ml",
    "Maltese": "mt",
    "Manx": "gv",
    "Maori": "mi",
    "Marathi": "mr",
    "Marshallese": "mh",
    "Mongolian": "mn",
    "Nauru": "na",
    "Navajo, Navaho": "nv",
    "North Ndebele": "nd",
    "South Ndebele": "nr",
    "Ndonga": "ng",
    "Nepali": "ne",
    "Norwegian": "no",
    "Norwegian Bokmål": "nb",
    "Norwegian Nynorsk": "nn",
    "Sichuan Yi, Nuosu": "ii",
    "Occitan": "oc",
    "Ojibwa": "oj",
    "Oriya": "or",
    "Oromo": "om",
    "Ossetian, Ossetic": "os",
    "Pali": "pi",
    "Pashto, Pushto": "ps",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Punjabi, Panjabi": "pa",
    "Quechua": "qu",
    "Romanian, Moldavian, Moldovan": "ro",
    "Romansh": "rm",
    "Rundi": "rn",
    "Russian": "ru",
    "Northern Sami": "se",
    "Samoan": "sm",
    "Sango": "sg",
    "Sanskrit": "sa",
    "Sardinian": "sc",
    "Serbian": "sr",
    "Shona": "sn",
    "Sindhi": "sd",
    "Sinhala, Sinhalese": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Somali": "so",
    "Southern Sotho": "st",
    "Spanish, Castilian": "es",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swati": "ss",
    "Swedish": "sv",
    "Tagalog": "tl",
    "Tahitian": "ty",
    "Tajik": "tg",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Thai": "th",
    "Tibetan": "bo",
    "Tigrinya": "ti",
    "Tonga (Tonga Islands)": "to",
    "Tsonga": "ts",
    "Tswana": "tn",
    "Turkish": "tr",
    "Turkmen": "tk",
    "Twi": "tw",
    "Uighur, Uyghur": "ug",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uzbek": "uz",
    "Venda": "ve",
    "Vietnamese": "vi",
    "Volapük": "vo",
    "Walloon": "wa",
    "Welsh": "cy",
    "Wolof": "wo",
    "Xhosa": "xh",
    "Yiddish": "yi",
    "Yoruba": "yo",
    "Zhuang, Chuang": "za",
    "Zulu": "zu",
}
confirmed_matches = {}