import scraper.main_scraper as main_scraper 
import database.db_update as db_updater
import database.db_connect as db_connect
import traceback
import os

########################################################################
# This program iterates through html files stored in the INPUT_FOLDER
# and passes the file reference to the main_scraper program.  Data that 
# is returned from the main_scraper is passed to the db_updater program
# to be updated to the database tables. Files that process successfully
# are moved to the OUTPUT_FOLDER.  Files that error are moved to the
# ERROR_FOLDER and any database updates are rolled back.
########################################################################

# file locations
INPUT_FOLDER = "scraper/InputFiles"
OUTPUT_FOLDER = "scraper/OutputFiles"
ERROR_FOLDER = "scraper/ErrorFiles"

def main():
    # Iterate through files in input folder
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".html")]

    connection = db_connect.connect_db()

    # Each file will be processed independently so any errors will not stop other files from being processed
    if len(files) > 0:
        for file_name in files:
            print(f"\nProcessing: {file_name}")

            try:
                full_path = os.path.join(INPUT_FOLDER, file_name)

                # Scrape pc data
                pc_data = main_scraper.run(full_path)

                # Save PC data to database
                with connection:
                    db_updater.save_pc_data(connection, pc_data)

                # Move successfully processed file
                move_file(INPUT_FOLDER, OUTPUT_FOLDER, file_name)
                print(f"Success: {file_name}")

            except Exception as e:
                # Rollback database updates for errored file
                connection.rollback()
                print(f"\n Failed: {file_name}")
                print("Error:", e)
                # Display the fill error stack trace
                traceback.print_exc()


                # Move errored file to error folder
                move_file(INPUT_FOLDER, ERROR_FOLDER, file_name)

                continue
    else:
        print("No files in input folder to process.")

    connection.close()

# Move file_name from input_folder to output_folder
def move_file(input_folder, output_folder, file_name):
    input_full_path = os.path.join(input_folder, file_name)
    output_full_path = os.path.join(output_folder, file_name)
    os.rename(input_full_path,output_full_path)

if __name__ == "__main__":
    main()
