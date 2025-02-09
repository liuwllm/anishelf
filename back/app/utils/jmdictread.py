import sys
import os
import json
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.config.settings import DATABASE_URL
from app.models.word import Word

load_dotenv()

tree = ET.parse('./public/JMdict_e.xml')
root = tree.getroot()

dictEntries = []

id = 0

for child in root:
    # Create empty entry dictionary
    entry = {
        "keb" : [],
        "reb" : [],
        "sense" : []
    }

    # Populate entry by parsing JMDict
    for element in child:
        if element.tag == 'ent_seq':
            continue
        elif element.tag == 'k_ele':
            for reading in element:
                if reading.tag == 'keb':
                    entry['keb'].append(reading.text)
        elif element.tag == 'r_ele':
            for reading in element:
                if reading.tag == 'reb':
                    entry['reb'].append(reading.text)
        elif element.tag == 'sense':
            # Multiple gloss form one sense (each gloss should be a synonym)
            sense = ""
            for definition in element:
                if definition.tag == 'gloss':
                    sense += definition.text 
                    sense += "; "
            sense = sense.removesuffix("; ")
            entry['sense'].append(sense)
    
    finalEntry = {
        "id" : None, 
        "keb" : None,
        "reb" : None,
        "sense" : entry['sense']
    }

    if len(entry['keb']) > 0:
        for keb in entry['keb']:
            for reb in entry['reb']:
                id += 1
                row = {
                    "id" : id,
                    "keb" : keb,
                    "reb" : reb,
                    "sense" : entry['sense']
                }
                dictEntries.append(row)
    else:
        for reb in entry['reb']:
            id += 1
            row = {
                "id" : id,
                "keb" : None,
                "reb" : reb,
                "sense" : entry['sense']
            }
            dictEntries.append(row)

dbEntries = []

for item in dictEntries:
    entry = Word(id=item['id'], keb=item['keb'], reb=item['reb'], sense=item['sense'])
    dbEntries.append(entry)

engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = sessionLocal()

try:
    session.bulk_save_objects(dbEntries)
    session.commit()
except Exception as e:
    session.rollback()
    print(f"Error during bulk insert: {e}")
finally:
    session.close()

# Convert dictionary to JSON file
# jsonEntries = json.dumps(dictEntries, indent=2)

# with open("../static/jmdict.json", "w") as outfile:
#    outfile.write(jsonEntries)
