# Milestone 1 - Basic Loading / Reading Endpoint

In this milestone you are setting up the basic end points of your web service that will receive POST requests to store data and GET requests to read data.

See the documentation on the endpoints at http://addison.cs.uchicago.edu:8080/docs/index.html to see what functionality you will need to implement.

The code in server/ has many instances of `#TODO MS1` that represent various pieces of functionality that you need to implement to complete the milestone. If the TODO is followed by a return or raise, you will need to replace the following line with the appropriate return value. These can be found in server.py (the main web/app service) and db.py (the data access object/layer that will interface with the DBMS). You can add new classes/files to help with abstracting functionality if you want. Remember to check these in!

## Step 1 Configure DB
Configure your server.conf file to contain your database connection information. With this set up, you should be able to run the server (from server/) `python3 server.py` and then visit (or curl) http://localhost:30235/hello If you see Hello, World! You have completed step 1. If you get an exception when running the server you likely have not properly configured your database conf file, or the server code cannot access the DB host (e.g. you might need to run a proxy first).

You will then need to run the drop and create scripts against your DB (`psql -h <hostname> -U <username> -f <filename.sql> <username>`)

Please see the documentation on the API and schema at http://addison.cs.uchicago.edu:8080/docs/index.html


## Step 2: Save Inspections
Implement the function
```
@app.post("/inspections")
def load_inspection():
```
This function will take a JSON as input (`request.json`) which you will need to parse / convert into a Python object. 

### Test 2.1
You should be able to test this with from the data dir (assuming default host and port): 
```
curl -H "Content-Type: application/json" --data @testInsp1.json http://localhost:30235/inspections
```
or  from the client dir:
```
python3 loader.py --file ../data/testInsp1.json --single
```

Your output should include `{"restaurant_id": 1}`. Your ID may be different if you have records or have previously loaded restaurant records.

### Test 2.2
After running the step in Test 2.1, run from the data dir (assuming default host and port): 
```
curl -H "Content-Type: application/json" --data @testInsp2.json http://localhost:30235/inspections
```
or  from the client dir:
```
python3 loader.py --file ../data/testInsp2.json  --single
```

Your output should include `{"restaurant_id": 1}`. Your ID may be different if you have records or have previously loaded restaurant records.

### Test 2.3
In a new terminal, while the server is running, run from the client directory `python3 loader.py --file ../data/reallySmall.json`

You should then unzip chicago-100.json.gz and chicago-1k.json.gz (gunzip <filename>) and test those with the above command but with the right filename. Both files are in data/ and the unzipped versions should **not** be checked in.

## Step 3: Read Restaurant by ID
Implement the function
```
@app.get("/restaurants/<restaurant_id:int>")
def find_restaurant(restaurant_id):
```
### Test 3.1
After running Test 2.1 or 2.2 test with
```
curl http://localhost:30235/restaurants/1
```
or go to http://localhost:30235/restaurants/1 in your favorite browser.


If you had a fresh (empty) DB before running 2.1 you should an output like
```
{"restaurant": {"id": 1, "name": "TORTOISE CLUB", "facility_type": "Restaurant", "address": "350 N STATE ST ", "city": "CHICAGO", "state": "IL", "zip": "60654", "clean": false, "latitude": 41.8888959276944, "longitude": -87.6282000827626}, "inspections": [{"id": "2359211", "risk": "Risk 1 (High)", "inspection_type": "Canvass", "results": "Pass", "violations": "", "date": "01/23/2020"}, {"id": "2356959", "risk": "Risk 1 (High)", "inspection_type": "Canvass", "results": "No Entry", "violations": "", "date": "01/17/2020"}]}
```


## Step 4: Read by Inspection
Implement the function
```
@app.get("/restaurants/by-inspection/<inspection_id>")
def find_restaurant_by_inspection_id(inspection_id):
```

### Test 4.1
After running Test 2.1 and 2.2 test with
```
curl http://localhost:30235/restaurants/by-inspection/2356959
```
or go to http://localhost:30235/restaurants/by-inspection/2356959 in your favorite browser.

If you had a fresh (empty) DB before running 2.1 you should an output like
```
{"id": 1, "name": "TORTOISE CLUB", "facility_type": "Restaurant", "address": "350 N STATE ST ", "city": "CHICAGO", "state": "IL", "zip": "60654", "clean": false, "latitude": 41.8888959276944, "longitude": -87.6282000827626}
```

### Test 4.2
After 4.1 test
```
curl -i http://localhost:30235/restaurants/by-inspection/111
```

and verify that your output is :

```
HTTP/1.0 404 Not Found
Date: Mon, 11 May 2020 22:57:19 GMT
Server: WSGIServer/0.2 CPython/3.8.2
Content-Length: 0
Content-Type: text/html; charset=UTF-8
```



## Fin and Write Up
If you worked with a partner you must add a write up ms1.txt in the project directory that specifies how you divided the work.
With this your MS1 should be good to go! Feel free to do additional testing. More client evaluation components will come in a future MS.

