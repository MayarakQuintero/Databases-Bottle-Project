# Milestone 2 - Bulk and Transactional Loading

In this milestone you are extending the end points of your web service to support a bulk loading of inspection records via a CSV and changing the 
prior loading to support transactions..

See the documentation on the endpoints at http://addison.cs.uchicago.edu:8080/docs/index.html to see what functionality you will need to implement.

The code in server/ has many instances of `#TODO MS2` that represent various pieces of functionality that you need to implement to complete the milestone. If the TODO is followed by a return or raise, you will need to replace the following line with the appropriate return value. These can be found in server.py (the main web/app service) and db.py (the data access object/layer that will interface with the DBMS). You can add new classes/files to help with abstracting functionality if you want. Remember to check these in!


**Note** the method in which we are designing endpoints in this project is not best/common practice. We are using get requests to simplify testing. Typically GET requests are for read-only requests, with DELETE, POST, and PUT used for modifications. See https://restfulapi.net/http-methods/ for a common pattern.

## Step 1 Count Inspection Records
Implement the function
```
@app.get("/count")
def count_insp():
```
This endpoint simply counts the number of records in the ri_inspections table and returns a simple json object {"count" : N } where N is the number of records in the table.

### Test 1.1
If there are records in the ri_inspections table simply count them using psql and check the result. Otherwise test inserting new records using steps from MS1 and check the count.
`curl -i http://localhost:30235/count`

## Step 2 Reset DB
Implement the function
```
@app.get("/reset")
def reset_db():
```
This endpoint will reset the database by truncating all tables in the database (https://www.postgresql.org/docs/10/sql-truncate.html).

### Test 2.1
Run `curl -i http://localhost:30235/reset`  and verify via PSQL and /count that your database does delete records.
Rerun load steps from MS1 afterward to ensure your load still works.



## Step 3 Bulk Loading
Implement the function
```
@app.get("/bulkload/<file_name:path>")
def bulk_load(file_name):
```
This endpoint will use the copy_from command in psycopg2 to bulk load the data.

### Test 3.1
Run `curl -i http://localhost:30235/bulkload/noFile.csv` to verify that a 404 is returned for no file found.

### Test 3.2
Reset the database `curl -i http://localhost:30235/reset` and run `curl -i http://localhost:30235/bulkload/reallySmall.csv` (or use the browser).
The run count to ensure there is 9 inspection records.

## Step 4 Transactional Loading
Implement the function
```
@app.get("/txn/<txnsize:int>")
def set_transaction_size(txnsize):
```
This endpoint should set the transaction size, such that `<txnsize>` inspection post requests are batched into a single transaction commit. 
Note this may result in more than `<txnsize>` inserts to the DB, as single post may result in two inserts (rest and inspection). Here, we are 
counting the number of times `/inspections` is called. It is advisable that when the txnsize is changed you log the new value and the prior value 
to ensure that you are correctly storing the value. Please read the documentation on this endpoint.

### Test 4.1
Reset the database and set the txnsize =2. 
`curl -i http://localhost:30235/reset`
`curl -i http://localhost:30235/txn/2`
Open a psql connection to the DB.

From MS1 run test 2.1 and in PSQL check that the insert is not visible (count on inspection table).
From MS2 run test 2.2 (which should result in a commit) and in PSQL check that both inspection records are visible.
This test will need to be run in PSQL as the count function would execute in the same transaction if it is using the same connection.


## Step 5 Abort/ Rollback
Implement the function
```
@app.get("/abort")
def abort_txn():
```
This endpoint will reset/rollback any active transaction. 

### Test 5.1
Reset the database and set the txnsize =2. 
`curl -i http://localhost:30235/reset`
`curl -i http://localhost:30235/txn/2`
Open a psql connection to the DB.

From MS1 run test 2.1 and in PSQL check that the insert is not visible (count on inspection table).
Rollback the current txn with `curl -i http://localhost:30235/abort`
From MS2 run test 2.2 (which should *not* result in a commit) and in PSQL check that *neither* inspection records are visible.
Rollback the current txn with `curl -i http://localhost:30235/abort`
This test will need to be run in PSQL as the count function would execute in the same transaction if it is using the same connection.

## Step 6 Reset DB with rollback
Extend the function `def reset_db()` to call abort/rollback before executing the reset.

### Test 6.1
Reset the database and set the txnsize =2. 
`curl -i http://localhost:30235/reset`
`curl -i http://localhost:30235/txn/2`
Open a psql connection to the DB.

From MS1 run test 2.1 and in PSQL check that the insert is not visible (count on inspection table).
Reset the DB: `curl -i http://localhost:30235/reset` 
Check that the DB is empty.
From MS1 run test 2.1 and 2.2 and ensure that both records are committed and visible in the DB (via PSQL).

