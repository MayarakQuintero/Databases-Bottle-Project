# Milestone 5 - Data Cleaning

In this milestone you are adding a new endpoint to clean the dataset by linking restaurants that you believe are the same, despite some variation in their information. 
See the documentation on the endpoints at http://people.cs.uchicago.edu/~aelmore/class/30235/docs/ to see what functionality you will need to implement.

The code has instances of `#TODO MS5` that represent the functionality that you need to implement to complete the milestone. If the TODO is followed by a return or raise, you will need to replace the following line with the appropriate return value.  You can add new classes/files to help with abstracting functionality if you want. Remember to check these in!


## Step 0 - Get Updated Datasets and dependencies
In your data directory run the following commands (or manually download and unzip)
```
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chiDirty10.json.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chiDirty10.csv.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chiDirty100.json.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chiDirty100.csv.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chiDirty1k.json.gz
wget http://people.cs.uchicago.edu/~aelmore/class/30235/chiDirty1k.csv.gz
gunzip *.gz
```
These are the datasets you will use for testing and development on this milestone.
WARNING on some of the CSV entries the zip codes end in .0. We are working to fix this and will push updated CSV files.

The dependencies you are allowed to use for this milestone now include

textdistance https://pypi.org/project/textdistance/ 

strsimpy https://pypi.org/project/strsimpy/

## Step 1 - Clean your data
Implement the function

```
@app.get("/clean")
def build_indexes():
```

This endpoint should trigger a cleaning process that attempts to link restaurants that are the same, meaning that they should be assigned the same restaurant ID, despite being duplicate entries with spelling variations/typos/missing data. In this process, you should iterate through all restaurants in the ri_restaurant table whose `clean` attribute is false. For this restaurant, you want to compare against every other record in the table to see if you can find 1 or more restaurants that match this record.

For this record matching process you can **ONLY** consider using the attributes: name, address, city, state, and zip. In comparing two records, you should calculate their similarity by building a simple linear model that uses 1 or more string similarity functions between at least 2 listed attributes. (In other words, you should run 1 or more string similarity functions on at least 2 of the attributes listed above, and use a linear combination of these scores to calculate a similarity score for these two records.) See the library links for available functions. Describe your model (i.e. the functions you are using and how you are combining their output scores) in the ms5.txt write up.

When finding a match for a given record, you should find all other records that your model says is a match and link this set of records together. For this set of linked records, you must determine an authoritative (primary) restaurant record to represent the entire set. This could be an existing record, a modified existing record (e.g. you change the address of a record and use it as the primary), or you could create a composite new record (e.g. you take the name from one record and the address from another record) and select this composite as the primary. You should have a simple heuristic for how you select the master record and include it in the ms5.txt write up.  

For a given record, once you have found matches and selected a primary record, you need to:
 - Insert entries into the new ri_linked table. There should be one entry for each restaurant in the linked set, with each pointing to the same primary record.
 - Update the ri_inspections for all linked records to point to the selected primary record.
 - Mark the set of selected records as `clean`, including the primary record. 

This cleaning process should iterate through all non-clean (dirty) records in the ri_restaurant table, and when considering candidate records for the linking, you should only evaluate/consider dirty records.  If a record has no candidate matches, mark the record as clean. Therefore, if this process is called twice in a row, the second time should do nothing as there are no dirty records left. *Note* that depending on how you iterate through records on this process, some records found by an initial query may be no longer dirty by the time you iterate to them. Think about how this could happen.

## Step 2 - Get all restaurants by Inspection
Implement the (new) function

```
@app.get("/restaurants/all-by-inspection/<inspection_id>")
def find_all_restaurants_by_inspection_id(inspection_id):
```

Note this function looks similar to an older function, but is new and slightly different. This endpoint, when given an inspection_id, will return 
both the primary restaurant for the inspection, and a list of all linked restaurants.

This will look like:
```
{ 
    "primary" : { <primary rest JSON>},
    "linked" : [ {<rest JSON> }, {<rest JSON>}   ]

}
```

### Step 3 - Testing
To start developing the cleaning process, we have provided a small dirtied dataset with 10 records. 3 of which should belong to a single primary record, another 2 that should belong to another primary restaurant. The remaining entries should be left as clean. A manual inspection of the CSV should help you identify what these records are.

To invoke this process run
```
python3 client/client.py -i data/chiDirty10.json --clean --halt
```

After you believe this process is working for chiDirty10, move onto chiDirty100 and chiDirty1k. Details on checking these ones for correctness are coming soon.
