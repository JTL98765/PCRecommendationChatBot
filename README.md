– Install Instructions
1)	Python is required to run this application.  This application was developed using  Python 3.12.10

2)	Download the project repository from Github:
https://github.com/JTL98765/PCRecommendationChatBot

3)	Install RASA as per the below instructions (including virtual environment creation):
https://rasa.com/docs/pro/installation/python/
(Note: you should not run the last step that creates a new template)

4)	Install PostgreSQL as per the below instruction:
https://www.postgresql.org/download/

5)	In PostgreSQL create a PC Database using the below command:

CREATE DATABASE "PC Database";

If the database name does not match the above you will have to update the database name in the database/database.ini file in the project folder:

[postgresql]
host=localhost
database=PC Database
user=[ADD USERNAME]
password=[ADD PASSWORD]

6)	Update database/database.ini file with your PostgreSQL username and password credentials

7)	In PostgreSQL (e.g. using pgAdmin or psql) run the SQL that is stored in SQL/ pc_recommendations_create_db.sql in the project folder.  This will create the PC recommendation tables.

8)	Install all required Python packages using the requirements.txt file in project folder as shown below:

pip install -r requirements.txt

9)	The chatbot solution requires an OpenAI API Key.  For security reasons, I have not included my key in the project.  A key can be generated from the below site:
https://platform.openai.com/api-keys
Once you have a key you should add it to you environment variables as OPENAI_API_KEY
Note: There is a cost to running requests against the OpenAI API using the generated key so funds need to be applied to your account. However, please note that after extensive testing, I have used less than £1 of OpenAI API credit.

10)	Ensure the venv is active before running the application by running the following command: 

.\.venv\Scripts\Activate.ps1

11)	Run resetData.py in the project folder to reset all test data.

12)	Run main.py in the project folder to load all test data to the database.

13)	To ensure the RASA model is trained before running the chatbot type the following command:

rasa train

14)	Once the train step has completed run the following command to start the RASA chatbot backend:
rasa run --enable-api --cors "*" --connector socketio
15)	Once up and running open the pc_chatbot.html page that is in the project folder in a web browser.

16)	The chatbot should start working.
