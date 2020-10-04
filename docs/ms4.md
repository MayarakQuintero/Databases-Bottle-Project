# Milestone 4 - Indexes and Performance Evaluation

In this milestone you are adding a new endpoint to add indexes to improve the lookup time of matching tweets to restaurants, adding a new endpoint to get tweet keys by inspection ID, and  are running a series of experiments to analyze how transactions, indexes, and bulk loading impact the performance of loading data and querying.  

See the documentation on the endpoints at http://people.cs.uchicago.edu/~aelmore/class/30235/docs/ to see what functionality you will need to implement.

The code has instances of `#TODO MS4` that represent the functionality that you need to implement to complete the milestone. If the TODO is followed by a return or raise, you will need to replace the following line with the appropriate return value.  You can add new classes/files to help with abstracting functionality if you want. Remember to check these in!


## Step 0 - Get Updated Datasets and dependencies
In your data directory run the following commands (or manually download and unzip)
```
wget http://people.cs.uchicago.edu/~aelmore/class/30235/twit1.json.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/twit2.json.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/twit5.json.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chi2k.csv.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chi2k.json.gz
gunzip *.gz
```
These are the datasets you will use for testing and development on this milestone.

### New client
**You will need to install hdrhistogram (eg pip3 install hdrhistogram) for this milestone.**

We have a new client.py program that will drive this (and future) milestones. 
To see the configuration parameters for client.py run `python3 client.py --help`

For example, to load the updated inspection dataset record by record and smaller new twitter dataset run:
`python3 client.py -i ../data/chi2k.json -t ../data/twit1.json`
If you wanted to load the udpated inspection dataset using the bulk method, creating the indexes (calling /buildix) after loading, and evaluating with the medium twitter dataset you would run:
`python3 client.py -i chi2k.csv --load bulk --index post -t ../data/twit5.json`

The updated client will give you latency numbers like:
INFO:root:Latency Perecentiles(ms) - 50th:160.00, 95th:179.00, 99th:243.00, 100th:463.00 - Count:2000
which tell you for an operation what was the percentile ms latency for those operations.

**Please run the updated create.sql file.**

## Step 1 Add and Reset Indexes
Implement the function
```
@app.get("/buildidx")
def build_indexes():
```
This endpoint alters the schema of your tables to add at least two indexes that should accelerate the matching of tweets to restaurants. These indexes should accelerate matching of tweets to restaurants by names and by lat/long. The alter table statements will be called before or after data loading, both for transactional loading and bulk loading.  Your create SQL files should not have any indexes added to them.

To test this function is working you will need to check in psql
`\d ri_restaurants` before and after calling the endpoint to verify that the indexes are added.

Then you should extend your `/reset` endpoint so that it drops the added indexes. Call /reset and use PSQL to verify that your indexes have been removed. 

## Step 2 Find Tweet Keys by Inspection ID
Implement the function
```
@app.get("/tweets/<inspection_id>")
def find_tweet_keys_by_inspection_id(inspection_id):
```

This endpoint takes an inspection ID and returns a list of tweet keys that match the restaurant associated with the inspection. The result should be returned as a json object, eg ` {"tkeys": [ "2017-05-05_16:24:17-palzarry", "2017-05-05_18:24:17-palzarry"] }`.

To test run the new client.py program with chi2k and twit1.json. You should see the following connections of tweets to restaurants (this list is a sample), and how they should match. The same keys are also present in twit2.json
```
2017-04-28_22:21:58-joeshark	TINY GIANTS EARLY LEARNING CENTER GEO
2017-05-04_12:45:07-KelliBlackwood	DJ'S GYROS NAME
2017-05-03_07:00:51-farhaadaarif	UNCLE REMUS NAME

```
Note that twit1 and twit5 are not overlapping datasets.

## Step 3 Evaluate and Write Up
With all endpoints working, you should run `sh client/experiment.sh` with your server running and connected to the database. This will run through a set of experiment runs that will evaluate how long does loading and matching tweets take under various configuration permutations, including: 
 - Loading inspections/restaurants with indexes created before loading, after loading, and no indexes at all
 - Loading inspections/restaurants with transactional loading of sizes 1,10,100,1000 and bulk loading.
 - Matching tweets with and without indexes.

 The results of the experiment.sh file are stored in `client/exp_results`, which is deleted every time the experiment script is run.  For this milestone you should analyze and evaluate the impact of your indexes on loading. A brief summary and analysis of your results should go in your ms4.txt file.

