import json
import xml.etree.ElementTree as ET

tree = ET.parse('../static/JMdict_e.xml')
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

# Convert dictionary to JSON file
jsonEntries = json.dumps(dictEntries, indent=2)

with open("../static/jmdict.json", "w") as outfile:
    outfile.write(jsonEntries)