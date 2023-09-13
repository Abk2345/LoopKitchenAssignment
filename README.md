# RestaurantTimeManager
This App develops a tool to manage a chain of restaurants by calculation of their uptime, downtime within intervals and also provides tools to figure out best and worst restaurants conforming to their work-time

# Set up details
1. Download data folder from (since it's size > 100mb) could not be uploaded on github: https://drive.google.com/drive/folders/1GhTtbLxWN_UvqBTpaeIqBvavHN3tTXNU?usp=sharing
2. Download this repo from github
3. Add Data folder to the downloaded repo
4. Install virtual environment for python using cmd: python3 -m venv server
5. Run venv cmd: source server/bin/activate
6. Install all the libraries from the requirements.txt file cmd:  pip3 install -r requirements.txt
7. Setup the database and api's
    1. Make a database on postgreSQL named LoopKitchenStores
    2. Putting the url in Server.py to connect to this database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://abk45@localhost:5432/LoopKitchenStores'
    3. Uncommenting db.create_all() in main function of Server.py and run the file using command: python3 Server.py -> this will build the tables as well as api's for the table
    4. run all the insert functions to insert all the data from csv to your database by running that function separtely from main function inside Server.py file

8. Running the application
    1. Run the file calculateUptime which involves all the calculation of required data in report and contains two api's, trigger_report to make report in the database table and                 get_report to retreive any particular report
    2. Running the file will run the server: python3 calculateUptime.py
  
# Please star if you loved the project!
