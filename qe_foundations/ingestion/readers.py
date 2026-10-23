"""qe_foundations/ingestion/readers.py  -  TASK 4 (about 35 min)

One reader per format. Each returns a LIST OF RAW RECORDS and only deals with
FORMAT problems (is this valid CSV / JSON / XML? are the columns there?).
Business rules (is the status allowed? is the duration negative?) belong to
validation.py, NOT here.

Always open files through open_source() from contexts.py.
See README Task 4 for the exact contract of each reader.
"""

import csv
import json
import xml.etree.ElementTree as ET

from .contexts import open_source
from .exceptions import MalformedSourceError, MissingColumnsError
from .validation import REQUIRED_FIELDS


def read_csv_records(path):
    """CSV -> list of raw dicts, one per data row (use csv.DictReader)."""
    with open_source(path) as file:
        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames or []
        missing = [field for field in REQUIRED_FIELDS if field not in fieldnames]
        if missing:
            raise MissingColumnsError(path, missing)
        
        try:
            return [dict(row) for row in reader]
        except csv.Error as error:
            raise MalformedSourceError(path, f"CSV parsing error: {error}") from error


def read_json_records(path):
    """JSON -> list of raw records. Expected shape: {"suite": ..., "tests": [...]}."""
    with open_source(path) as file:
        try:
            content = json.load(file)
        except (json.JSONDecodeError, ValueError) as error:
            raise MalformedSourceError(path, f"Malformed JSON: {error}") from error
        
        if not isinstance(content, dict) or ("tests" not in content) or not isinstance(content["tests"], list):
            raise MalformedSourceError(path, "Expected JSON object containing a 'tests' list")   

    return content['tests']  

def read_xml_records(path):                                                                                                                                              
        """XML -> list of raw dicts, one per <testcase> element at ANY depth."""                                                                                             
        with open_source(path) as file:                                                                                                                                      
            try:                                                                                                                                                             
                tree = ET.parse(file)                                                                                                                                        
                root = tree.getroot()                                                                                                                                        
                result = []                                                                                                                                                  
                for case in root.iter("testcase"):                                                                                                                           
                    # Default all REQUIRED_FIELDS to None when absent                                                                                                        
                    record = {field: None for field in REQUIRED_FIELDS}                                                                                                      
                                                                                                                                                                             
                    # Read XML attributes                                                                                                                                 
                    record.update(case.attrib)                                                                                                                               
                                                                                                                                                                             
                    # Read child elements (if present)                                                                                                                    
                    for child in case:                                                                                                                                       
                        val = child.text.strip() if child.text and child.text.strip() else None                                                                              
                        record[child.tag] = val                                                                                                                              
                                                                                                                                                                             
                    result.append(record)                                                                                                                                    
                return result                                                                                                                                                
            except ET.ParseError as error:                                                                                                                                   
                raise MalformedSourceError(path, f"XML is not well-formed: {error}") from error 
