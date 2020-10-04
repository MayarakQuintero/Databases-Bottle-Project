# Authors 

Diego Díaz 
Mayarak Quintero 

# Instructor 

Aaron J. Elmore

# FoodInspection Web Service Project

This project is a series of homeworks (e.g. milestones) that will work towards building a web service that will take input JSON data as a POST request and store the data an database. In addition, the web service will handle GET requests to return information that is generated by querying the database. 

We will provide a skeleton implementation of the server that you will extend to get your web service working. This will have the initial web service endpoints (e.g. URLS to handle the POST/GET requests). We will also provide a client that will generate the requests based on data from local files. You should not modify the client (or if you do, do NOT commit any changes).  You are free to add additional Python classes/files to handle certain aspects of your application, such as a models for holding state based on the DB and/or data access objects that provide the functions to interact with the database. Alternatively you can inline all of this functionality into the server.py file, but this will likely become unwieldy.

## Milestones
The milestones roughly cover:

 - MS1: Building the basic data loading functionality that takes a food inspection JSON POST to save (or find) a restaurant and save the inspection details, that is linked to the restaurant record. Some basic read/GET endpoints will be added that provide details on a restaurant and inspections.
 - MS2: Adding bulk loading that specifies the name of a CSV file to be bulk loaded into the DB (same data as MS1, but in a different format). 
 - MS3: Integrating a Twitter dataset and matching tweets to restaurant by lat/long or name.
 - MS4: Adding indexes to improve matching and lookups.
 - MS5: Cleaning the dataset to eliminate duplicate restaurant entries with typos or variations in the details.
 - MS6: Improving the cleaning to handle a larger dataset.

For some milestones there will be a placeholder for where you need to add code, and will appear in the code as 
```
#TODO MS1
```
This may include a return or exception that you should remove once your code is complete.  For certain components there will be no milestone TODO and it is up to you on where to add the code. 

For particular milestones see docs/MSx.md where X is the milestone number.

## Python packages
For this project we will specify exactly what python packages/module you are allowed to use. Any additional package that is not specified or approved will result in a **50% point penalty for each milestone** the module is used on. Use your favorite installer (pip3)  To start we will use:
 - bottle
 - pyscopg2-binary (or just pyscopg2) 

## Running the code

### DB initialization
We have provided you with a base schema that your restaurants and inspections must align to.  Run this using psql against your database before starting your server. To reset your database simply run drop and create. If you add additional tables add them to both files.


### Server
To run the server simply run `python3 server.py` in the server directory. There are a series of configuration parameters that can be passed to the server, to see them run `python3 server.py --help`. The server by default will run on localhost and port 30235. After running the server you should be able to visit http://localhost:30235/hello and see a message "Hello, World!" to verify that your web service is running.  Alternatively, you can test using command line tool curl, eg `curl http://localhost:30235/hello`, if curl is installed. Note that you will need to get your database connection information working to start, which involves creating a server.conf file that follows the format in server.conf.example. You will likely need to have your SSH proxy running first to connect to the DB.

### Client
While the server is running you run the client application in another terminal. To run the client that loads inspection data use something like `python3.py loader.py --file ../data/reallySmall.json`.  


