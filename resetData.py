import os
import database.db_connect as db_connect

# Utility to move test data back to input folders and clear database tables

INPUT_FOLDER = "scraper/OutputFiles"
OUTPUT_FOLDER = "scraper/InputFiles"

def run():
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".html")]
    for file_name in files:
        move_file(INPUT_FOLDER, OUTPUT_FOLDER, file_name)
    purge_database()

def move_file(input_folder, output_folder, file_name):
    input_full_path = os.path.join(input_folder, file_name)
    output_full_path = os.path.join(output_folder, file_name)
    os.rename(input_full_path,output_full_path)

def purge_database():
    connection = db_connect.connect_db()
    sql = """
    TRUNCATE TABLE listing, model, graphics, processor, laptop RESTART IDENTITY CASCADE;
    """
    with connection.cursor() as cur:
        cur.execute(sql)

    connection.commit()

if __name__ == "__main__":
    run()