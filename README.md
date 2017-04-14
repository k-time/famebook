![Famebook](https://s3.amazonaws.com/kxiao/marilyn.png)

## Overview
Famebook is a demo news and social media aggregator where users can view generated profiles of famous people 
and see their recent activity in the world.

**Demo website: http://www.columbia.edu/~ksx2101/fame/**

The database currently isn't running because my university Azure account expired, but I will get 
it up on a new server.

## Features
* Users can create accounts, follow their favorite celebrities, politicians, sports figures, etc., and have a 
feed of relevant news articles, social media posts, videos, etc. about them. 
* Users can generate profiles for famous people not already on Famebook and add them to their feeds.
* Users can rate each famous person and view their overall ratings over time to assess public opinion. 
* There is a daily leaderboard of rising people who had the largest impact, or jump in followers, 
for that day.

Famebook is useful because many people do not have Facebook/Twitter/Instagram accounts but often 
want to see what certain famous people have been up to lately.

## Web App
The stack is **Linux, Apache, PostgreSQL, Python,** and the **Flask web framework**.

* Run `python server.py` to start the webserver on the default port.
* Run `python server.py 0.0.0.0 8000`, for example, to start it on a custom port.
* Run [*setup.sql*](setup.sql) to initialize the database.

<br><br/>
![Famebook](/static/top.png)
