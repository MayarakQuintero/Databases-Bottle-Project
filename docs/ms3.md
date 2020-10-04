# Milestone 3 - Tweet Matcing

In this milestone you are extending the end points of your web service to support matching tweets against restaurants, either by the tweet mentioning a restaurant by name or if the tweet is geo-tagged (eg has lat/long) and is within a box ~500 meters.

See the documentation on the endpoints at http://people.cs.uchicago.edu/~aelmore/class/30235/docs/ to see what functionality you will need to implement.

The code has one instance of `#TODO MS3` that represent the functionality that you need to implement to complete the milestone. If the TODO is followed by a return or raise, you will need to replace the following line with the appropriate return value.  You can add new classes/files to help with abstracting functionality if you want. Remember to check these in!

Note the create and drop SQL files have changes that need to be reflected in your DB.

**Warning the Twitter data came from a crawl and is not filtered. I have not checked the Tweets for offensive language or content. If you want me to provide a sanitized version, we can look into trying to filter out certain content.**

## Step 1 Match Tweets
Implement the function
```
@app.post("/tweet")
def tweet():
```
This endpoint takes a tweet as a JSON object via a post request. This endpoint checks if the tweet matches any restaurants in the database, by name or location. If so, the endpoint stores the tweet key and restaurant id in the new ri_tweetmatch table. This record should also note how the match was made using the enum match type:
```
CREATE TYPE match_type AS ENUM ('geo', 'name', 'both');
```

 - To match by location, if the tweet has a lat and long value, then you see if the lat/long falls within ~500 meters of any restaurant in the database. Normally the distance calculation has some cost associated with it as the Earth is a sphere, but we will use the very simple and innacurate calculation of checking if the tweet's location falls within +/- 0.00225001 latitude and +/- 0.00302190 longitude of a restaurants location. Note, never use this method in the real world.
 - To match by name we are going to split the text of tweet into words by spaces, commas, hyphens, and periods. The name match should be case *insensitive* We will then consider all 1,2,3, and 4 gram words for candidate restaurant names. We have provided you with a function that will split the words and generate an N-gram for you in the function `ngrams(tweet, n)` . For example passing the tweet text `"Chowing at Dragon Bowl. Yum!"` to the ngram function with n as 1 gives: `['Chowing', 'at', 'Dragon', 'Bowl', 'Yum']` and n as 2 gives: `['Chowing at', 'at Dragon', 'Dragon Bowl', 'Bowl Yum']`. Here the 2gram 'Dragon Bowl' matches a restaurant name and so the key and restaurant ID should be added to the ri_tweetmatch table with the match as name.

This endpoint should return a list of restaurant IDs that matched the tweet eg `matches: [131,4131,100]` or an empty list if none were matched `matches: []`

### Test 1.1
Reset the database and run the chicago-100.json loader `python3 loader.py --file ../chicago-100.json`

Test with two single tweets using 
`python3 loader.py --file ../data/testTweet1.json -e tweet`
and 
`python3 loader.py --file ../data/testTweet2.json -e tweet`

You should see no match for testTweet1 a match for testTweet2.json of one restaurant (Dragon Bowl). 
You will need to check your database to see that the restID is correct.

### Test 1.2
Reset the database and run the chicago-100.json loader `python3 loader.py --file ../chicago-100.json`

`gunzip data/twitSmall.json.gz`

Then run `python3 loader.py --file ../data/twitSmall.json -e tweet`

Your output from the client should look like 
```
Using post url to load http://localhost:30235/tweet
Finished. Total: 99 Count of 200:99 Count of 201:0 Count of other <400:0
```
Then you should check the database to see if you have the following 3 matches: 

```
Restaurant Name: TweetKey: Type
Dragon Bowl : 2016-04-22_19:13:47-trippinpurpose : name  
Halal Guys : 2016-04-22_19:15:24-nikejustdoit93 : name
HAROLD'S CHICKEN SHACK #14: 2016-04-22_19:21:19-LullabeLaby : geo
```

### Test 1.3
Coming soon. This test will involve a larger Twitter dataset for you to check against Chicago-1k.json