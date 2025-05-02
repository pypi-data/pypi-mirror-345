'''
File: settings.py
Author: Adam Pah, Scott Daniel
Description: Settings file
'''

import sys
from pathlib import Path

PARENT = Path(__file__).resolve().parents[1]
sys.path.append(str(PARENT))



# Basics
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DATA = (PARENT if 'site-packages' in str(PARENT) else (PROJECT_ROOT / 'code')) / 'scales_nlp_support' / 'core_data'
DATAPATH = PROJECT_ROOT / 'data'
PACER_PATH = DATAPATH / 'pacer'
ANNO_PATH = DATAPATH / 'annotation'
UNIQUE_FILES_TABLE = DATAPATH / 'unique_docket_filepaths_table.csv'
ALL_PACER_UCIDS = PACER_PATH / 'case_lists' / 'all.csv'
DATA_EXPLORER_UCIDS = PACER_PATH / 'case_lists' / 'satyrn.csv'

# Scraper
MEM_DF = PROJECT_ROOT / 'code' / 'downloader' / 'member_cases.csv'
LOG_DIR = PROJECT_ROOT / 'code' / 'downloader' / 'logs'

# Parser
MEMBER_LEAD_LINKS = ANNO_PATH / 'member_lead_links.jsonl'
ROLE_MAPPINGS = ANNO_PATH / 'role_mappings.json'

# Entities
DIR_SEL = ANNO_PATH / 'judge_disambiguation' / 'SEL_Annotations'
JEL_JSONL = ANNO_PATH / 'judge_disambiguation' / 'JEL.jsonl'
COUNSEL_DIS_DIR = ANNO_PATH / 'counsel_disambiguation' / 'Counsel_Disambiguations'
COUNSEL_DIS_CLUSTS = ANNO_PATH / 'counsel_disambiguation' / 'Counsel_Clusters.jsonl'
FIRM_DIS_DIR = ANNO_PATH / 'firm_disambiguation' / 'Firm_Disambiguations'
FIRM_DIS_CLUSTS = ANNO_PATH / 'firm_disambiguation' / 'Firm_Clusters.jsonl'
PARTY_DIS_DIR = ANNO_PATH / 'party_disambiguation' / 'Party_Disambiguations'
PARTY_DIS_CLUSTS = ANNO_PATH / 'party_disambiguation' / 'Party_Clusters.jsonl'

# Ontology
ONTOLOGY_DIR = ANNO_PATH / 'ontology' / 'mongo'
ONTOLOGY_LABELS = ONTOLOGY_DIR / 'labels.csv'



# Auxiliary CSVs (core data)
STATEY2CODE = CORE_DATA / 'statey2code.json'
NATURE_SUIT = CORE_DATA / 'nature_suit.csv'
JUDGEFILE = CORE_DATA / 'judge_demographics.csv'
COURTFILE = CORE_DATA / 'district_courts.csv'
DISTRICT_COURTS_94 = CORE_DATA / 'district_courts_94.csv'
BAMAG_JUDGES = CORE_DATA / 'brmag_judges.csv'
BAMAG_POSITIONS = CORE_DATA / 'brmag_positions.csv'

# Auxiliary CSVs (other)
EDGAR = ANNO_PATH / 'edgar_ciks.csv'
AMLAW_100 = ANNO_PATH / 'amlaw_top_100.csv'
HYBRID_FIRMS = ANNO_PATH / 'hybrid_firm_list.csv'
CENSUS_CITIES = ANNO_PATH / 'census_SUB-EST2020_ALL.csv'
JUDGEFILES_DIR = ANNO_PATH / 'fjc_article_iii_biographical_directory'
FLAGS_DF = ANNO_PATH / 'case_flags.csv'
RECAP_ID_DF = ANNO_PATH / 'recap_id2ucid.csv'
EXCLUDE_CASES = DATAPATH / 'exclude.csv'

# Misc folders
BUNDLES = DATAPATH / 'bundles'
RECAP_PATH =  DATAPATH / 'recap'
FJC =  DATAPATH / 'fjc'
IDB = FJC / 'idb'
SENTENCING_COMMISSION = DATAPATH / 'sentencing-commission'
STYLE = PROJECT_ROOT / 'code' / 'scales_nlp_support' / 'style'

# Helper functions
use_datastore =	lambda path: Path(str(path).replace(str(CORE_DATA), str(ANNO_PATH)+'/core_data'))

# Constants
CTYPES = {'cv':'civil', 'cr':'criminal'}
ENTITY_PATH_MAP = {'judges': DIR_SEL, 'counsels': COUNSEL_DIS_DIR, 'firms': FIRM_DIS_DIR, 'parties': PARTY_DIS_DIR}

# Dev settings
SETTINGS_DEV = Path(__file__).parent / 'settings_dev.py'
if SETTINGS_DEV.exists():
    from scales_nlp_support.settings_dev import *
