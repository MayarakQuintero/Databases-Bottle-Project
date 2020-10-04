# Milestone 6 - Scaling Data Cleaning

In this milestone you are extending your cleaning from MS5 to handle larger datasets. In particular you will:
 - Enable blocking of the restaurant data to limit the candidate set of potential pairs.
 - Within a block/umbrella set, you will use at least one index to accelerate look ups for at least one attribute.
 - You must now create a new primary record for all matched/linked restaurants.
 - When looking for matches/restaurants to link, you will now consider matching a dirty restaurant against a cleaned restaurant. This can result in updating the primary restaurant entry.

## Step 0 - Get Updated Datasets and dependencies

We will create two new large datasets for you to test with. The links will be posted on Piazza. To start, work with dirty100 and 1k.

## Step 1 - Enable Blocking

You should modify your cleaning process to now use blocking. Here, when your process begins, you should create a grouping of your records into mutually exclusive "blocks", based on one or more of these attributes: name, address, city, state, and zip. After creating a block of records, when carrying out matching, you will only consider records that match within the same block. For example, I take 100 records and create 3 blocks: AA BB and CC. A record in BB will only be checked against other records in BB. I strongly encourage you to use temporary tables to create these blocks. 

Your process should determine what temporary tables need to be created, and copy records into these temp tables (ideally these temp records have less data/attributes than the records in the full ri_inspections table). Your cleaning process should then iterate through each of these blocks, and perform your matching within the blocks. The output of the cleaning process is the same as MS5. Please document in MS6.txt how you created your blocks.

**For testing, server.py now has a flag -s that will set app.scaling=True. In your cleaning function/endpoint. Check if this -s flag is set, and if so use the new cleaning approach for this MS. Otherwise use your cleaning approach from MS5. This will allow you to test your code's results. `python3 server.py -s`**

## Step 2 - Indexing within Blocks

For this step you will create an index within each of your blocks. This index should be used when looking for candidate records to match. There are several indexes you could create, but you only need one. It should be simple and it is ok if this reduces the candidate set of records you compare with. Please document in MS6.txt how you created your indexes.

## Step 3 - Create a new primary record

For this step, you are now required to create a new (composite) primary record when linking 2+ records. This means that your approach cannot simply select one of the records from the linked set. You must write some heuristic for generating the new primary record. There is not single right way to do this, so feel free to be creative. Please document in MS6.txt how you created your primary record.

## Step 4 - Extend cleaning to consider already cleaned records

For this step, when cleaning a dirty record, you will now consider linking this to an already cleaned record. This match may be the primary record OR it could be against a linked restaurant (it is up to you if you want to limit it to one or do both). In other words you can consider what clean records to match against.

When matching a dirty record to a cleaned set, you must check if the primary record should be updated to reflect the new record(s). For example, I create a record 14 to link records 1 and 3. I then match records 22 and 31 to 14, and update 14's address to reflect the new variations found in 22 and 31.
