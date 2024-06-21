import sys
import os
import json
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app import db, Word, app

load_dotenv()

tree = ET.parse('./public/JMdict_e.xml')
root = tree.getroot()

dictEntries = []

for child in root:
    # Create empty entry dictionary
    entry = {
        "id" : None, 
        "keb" : [],
        "reb" : [],
        "sense" : []
    }

    # Populate entry by parsing JMDict
    for element in child:
        if element.tag == 'ent_seq':
            entry['id'] = int(element.text)
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
    
    # Append entry to full dictionary(represented by list)
    dictEntries.append(entry)

dbEntries = []
for item in dictEntries:
    entry = Word(id=item['id'], keb=item['keb'], reb=item['reb'], sense=item['sense'])
    dbEntries.append(entry)

with app.app_context():
    try:
        db.session.bulk_save_objects(dbEntries)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error during bulk insert: {e}")
    finally:
        db.session.close()

# Convert dictionary to JSON file
# jsonEntries = json.dumps(dictEntries, indent=2)

# with open("../static/jmdict.json", "w") as outfile:
#    outfile.write(jsonEntries)
