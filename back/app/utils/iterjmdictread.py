import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.config.settings import DATABASE_URL
from app.models.word import Word

load_dotenv()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BATCH_SIZE = 50
id_counter = 0
batch = []

def process_entry(elem):
    global id_counter
    keb_list = []
    reb_list = []
    senses = []

    for child in elem:
        if child.tag == 'k_ele':
            for sub in child:
                if sub.tag == 'keb':
                    keb_list.append(sub.text)
        elif child.tag == 'r_ele':
            for sub in child:
                if sub.tag == 'reb':
                    reb_list.append(sub.text)
        elif child.tag == 'sense':
            sense = ""
            for defn in child:
                if defn.tag == 'gloss' and defn.text:
                    sense += defn.text + "; "
            senses.append(sense.removesuffix("; "))

    entries = []
    if keb_list:
        for keb in keb_list:
            for reb in reb_list:
                id_counter += 1
                entries.append(Word(id=id_counter, keb=keb, reb=reb, sense=senses))
    else:
        for reb in reb_list:
            id_counter += 1
            entries.append(Word(id=id_counter, keb=None, reb=reb, sense=senses))

    return entries

print("Starting XML stream parse and batch DB insert...")

context = ET.iterparse('./public/JMdict_e.xml', events=('end',))
for event, elem in context:
    if elem.tag == 'entry':
        new_entries = process_entry(elem)
        batch.extend(new_entries)
        elem.clear()  # free memory

        if len(batch) >= BATCH_SIZE:
            session = SessionLocal()
            try:
                session.bulk_save_objects(batch)
                session.commit()
                print(f"Inserted batch of {len(batch)}")
            except Exception as e:
                session.rollback()
                print(f"Error inserting batch: {e}")
            finally:
                session.close()
                batch.clear()

# Final leftovers
if batch:
    session = SessionLocal()
    try:
        session.bulk_save_objects(batch)
        session.commit()
        print(f"Inserted final batch of {len(batch)}")
    except Exception as e:
        session.rollback()
        print(f"Error inserting final batch: {e}")
    finally:
        session.close()

print("All entries processed and inserted.")
