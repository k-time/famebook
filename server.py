#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.

eugene wu 2015
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db1.cloudapp.net:5432/proj1part2
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db1.cloudapp.net:5432/proj1part2"
#
DATABASEURI = "postgresql://kj2310:216@w4111db1.cloudapp.net:5432/proj1part2"
#DATABASEURI = "sqlite:///test.db"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#

# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

#
# END SQLITE SETUP CODE
#

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


# DONE DURING REVIEW SESSION.


@app.route("/hello/", methods=["POST", "GET"])
def myfirstappfunction():
    print request.args
    print "\n"
    #print request.args["name"]
    print request.args["age"]

    d=dict(title="Your age: " + request.args["age"])
    if int(request.args["age"]) < 50:
        # Looks in templates folder for index.html. Then returns this page
	return render_template("index.html", **d) #use **d as second argument to pass in object with key value pairs
    else:
        return "you are old"
    return "hello world"


@app.route("/news/", methods=["POST", "GET"])
def get_news():

  # Maps a news_id to a list of celebrity names associated with that news
  news_dict = {}

  cursor = g.conn.execute("""
    SELECT n1.people_id, news_id, name 
    FROM notable_people_has n1 
    INNER JOIN notable_people_adder n2 
    ON (n1.people_id = n2.people_id)""")

  for result in cursor:
    news_id = result['news_id']
    name = result['name']

    if news_id not in news_dict:
      news_dict[news_id] = [name]
    else:
      news_dict.setdefault(news_id, []).append(name)

  # Aggregate the news rows

  cursor = g.conn.execute("""SELECT * FROM news ORDER BY datetime DESC""")
  news = []
  # Result is one row
  for result in cursor:
    celebrity_list = []
    news_id=result['news_id']
    if news_id in news_dict:
      celebrity_list = news_dict[news_id]

    news.append(dict(source=result['source'], content=result['content'], datetime=result['datetime'], celebs=celebrity_list))
  
  cursor.close()
  context = dict(data=news)
  return render_template("news.html", **context)



@app.route("/search/", methods=["POST", "GET"])
def search_function():

  name = '%' + request.args['name'] + '%'
  cursor = g.conn.execute("SELECT people_id, name FROM notable_people_adder WHERE name ILIKE %s ORDER BY name", name)
  search_results = []

  for result in cursor:
    search_results.append(dict(people_id=result['people_id'], name=result['name']))
  
  cursor.close()
  context = dict(data=search_results)
  return render_template("search.html", **context)


@app.route("/add/", methods=["POST", "GET"])
def add_person():
  days = range(1,32)
  years = range(1900,2016)
  years.reverse()
  context = dict(days=days, years=years)
  return render_template("add.html", **context)


@app.route("/submit/", methods=["POST", "GET"])
def submit_function():
  
  hasError = False
  errorMessages = []

  username=request.form['username']
  password=request.form['password']
  name = request.form['name']
  birthday=request.form['year'] + '-' + request.form['month'] + '-' + request.form['day']
  industry=request.form['industry']
  gender=request.form['gender']
  net_worth=request.form['net_worth']
  instagram_username=request.form['instagram_username']
  twitter_username=request.form['twitter_username']
  facebook_page_name=request.form['facebook_page_name']

  # Check if username exists. It should.

  user_id = -1
  username_exists = False
  cursor = g.conn.execute("SELECT username,user_id FROM users WHERE username=%s", username)
  
  for result in cursor:
    username_exists = True
    user_id = result['user_id']
    break
  cursor.close()

  if username_exists == False:
    hasError = True
    errorMessages.append('Username does not exist.')

  if username_exists == True:
    cursor = g.conn.execute("SELECT password FROM users WHERE username=%s", username)
    for result in cursor:
      if result['password'] != password:
        hasError = True
        errorMessages.append('Incorrect password.')

  # Check if attributes are not empty

  if not name:
    hasError = True
    errorMessages.append('Must enter a name.')

  # Check if net worth is a number

  try:
    float(net_worth)
  except ValueError:
    hasError = True
    errorMessages.append('Net worth is not a number.')

  # Check if name + birthday already exists

  cursor = g.conn.execute("SELECT * FROM notable_people_adder WHERE name=%s AND birthday=%s", name, birthday)
  for result in cursor:
    hasError = True
    errorMessages.append('Person already exists in database.')
    break
  cursor.close()

  # Return error page if error

  if hasError:
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)

  # Try sql query

  try:
    people_id = -1

    cursor=g.conn.execute("""
      SELECT MAX(people_id)
      FROM notable_people_adder
      """)

    for result in cursor:
      people_id=int(result['max'])
      break

    people_id=people_id + 1

    cursor=g.conn.execute("INSERT INTO notable_people_adder VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
      people_id, net_worth, instagram_username, twitter_username, facebook_page_name, user_id, name, gender, birthday, industry)
    cursor.close()

    return redirect("/person/?id=" + str(people_id))

  except Exception as e:
    cursor.close()
    errorMessages.append('Invalid inputs!')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)

@app.route("/rate/", methods=["POST", "GET"])
def rate_function():

  hasError = False
  errorMessages = []

  username=request.form['username']
  password=request.form['password']
  rating=request.form['rating']
  people_id=request.form['people_id']

  # Check if username exists. It should.

  user_id = -1
  username_exists = False
  cursor = g.conn.execute("SELECT username,user_id FROM users WHERE username=%s", username)
  
  for result in cursor:
    username_exists = True
    user_id = result['user_id']
    break
  cursor.close()

  if username_exists == False:
    hasError = True
    errorMessages.append('Username does not exist.')

  correct_password = False

  if username_exists == True:
    cursor = g.conn.execute("SELECT password FROM users WHERE username=%s", username)
    for result in cursor:
      if result['password'] != password:
        hasError = True
        errorMessages.append('Incorrect password.')
      else:
        correct_password = True
    cursor.close()

  # Check if they submitted in the past week
  if username_exists and correct_password:
    
    current_week = ""

    # Get current start of week
    cursor = g.conn.execute("SELECT date_trunc('week', current_date)")
    for result in cursor:
      current_week = result['date_trunc']
    cursor.close()

    try:
      cursor = g.conn.execute("INSERT INTO submits VALUES (%s, %s, %s, %s)", user_id, current_week, people_id, rating)
      cursor.close()
      return redirect("/person/?id=" + str(people_id))
    
    except Exception as e:
      cursor.close()
      hasError = True
      errorMessages.append('Already submitted rating this week! Try again Monday.')

  context=dict(errors=errorMessages)
  return render_template("error.html", **context)


@app.route("/adv/", methods=["POST", "GET"])
def adv():
  days = range(1,32)
  years = range(1900,2016)
  years.reverse()
  context = dict(days=days, years=years)
  return render_template("advsearch.html", **context)


@app.route("/advsearch/", methods=["POST", "GET"])
def advsearch():
  
  errorMessages = []

  comparison=request.form['comparison']
  birthday=request.form['year'] + '-' + request.form['month'] + '-' + request.form['day']
  industry=request.form['industry']
  gender=request.form['gender']
  net_worth_compare = request.form['net_worth_compare']
  net_worth=request.form['net_worth']

  sql_birthday = ""

  if comparison == "bornbefore":
    sql_birthday = "birthday < " + "'" + birthday + "'"
  else:
    sql_birthday = "birthday > " + "'" + birthday + "'"

  sql_industry = ""

  if industry == "any":
    sql_industry = ""
  else:
    sql_industry = "AND industry = " + "'" + industry + "'"

  sql_gender = ""

  if gender == "any":
    sql_gender = ""
  else:
    sql_gender = "AND gender = " + "'" + gender + "'"

  sql_net_worth = ""

  if not net_worth:
    net_worth = "-1000000000000"
    net_worth_compare = "greaterthan"

  # Check if net worth is a number
  try:
    float(net_worth)

  except ValueError:
    errorMessages.append('Net worth is not a number.')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)    

  sql_statement = ""

  if net_worth_compare == "greaterthan":
    # These are not user inputs, so no danger of SQL injection
    sql_statement = "SELECT people_id,name FROM notable_people_adder WHERE " + \
      sql_birthday + " " + sql_industry + " " + sql_gender + " AND net_worth > %s " + "ORDER BY name"

  else:
    # These are not user inputs, so no danger of SQL injection
    sql_statement = "SELECT people_id,name FROM notable_people_adder WHERE " + \
      sql_birthday + " " + sql_industry + " " + sql_gender + " AND net_worth < %s " + "ORDER BY name"


  # Need to protect against user input here
  cursor = g.conn.execute(sql_statement, net_worth);
  search_results = []

  for result in cursor:
    search_results.append(dict(people_id=result['people_id'], name=result['name']))
  
  cursor.close()
  context = dict(data=search_results)
  return render_template("search.html", **context)



@app.route("/register/", methods=["POST", "GET"])
def register():
  return render_template("register.html")


@app.route("/registeruser/", methods=["POST", "GET"])
def registeruser():

  errorMessages = []

  username=request.form['username']
  password=request.form['password']

  # Check if username already exists.

  username_exists = False
  cursor = g.conn.execute("SELECT username,user_id FROM users WHERE username=%s", username)
  
  for result in cursor:
    username_exists = True
    break
  cursor.close()

  if username_exists == True:
    errorMessages.append('Username already taken!')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)

  if " " in username:
    errorMessages.append('Whitespace not allowed in username!')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)

  if len(password) < 3:
    errorMessages.append('Password must be longer than 2 characters!')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)

  # If you've made it to this point, you have a valid username and password.

  user_id = -1

  cursor=g.conn.execute("""
    SELECT MAX(user_id)
    FROM users
    """)

  for result in cursor:
    user_id=int(result['max'])
    break

  user_id=user_id + 1
  cursor.close()

  # Insert into table
  cursor = g.conn.execute("INSERT INTO users VALUES (%s, %s, %s)", username, password, user_id)
  cursor.close()

  return render_template("success.html")


@app.route("/follow/", methods=["POST", "GET"])
def follow():
  name=request.form['name']
  people_id=request.form['people_id']
  context=dict(name=name,people_id=people_id)
  return render_template("followperson.html", **context)

@app.route("/followperson/", methods=["POST", "GET"])
def follow_person():

  errorMessages = []

  username=request.form['username']
  password=request.form['password']
  people_id=request.form['people_id']

  # Check if username exists. It should.

  user_id = -1
  username_exists = False
  cursor = g.conn.execute("SELECT username,user_id FROM users WHERE username=%s", username)
  
  for result in cursor:
    username_exists = True
    user_id = result['user_id']
    break
  cursor.close()

  if username_exists == False:
    errorMessages.append('Username does not exist.')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)


  cursor = g.conn.execute("SELECT password FROM users WHERE username=%s", username)
  for result in cursor:
    if result['password'] != password:
      errorMessages.append('Incorrect password.')
      context=dict(errors=errorMessages)
      return render_template("error.html", **context)
  cursor.close()

  # If you are at this point, then you have a valid username and password.

  # Insert into table

  try:
    cursor = g.conn.execute("INSERT INTO user_follows VALUES (%s, %s)", user_id, people_id)
    cursor.close()
    return render_template("success.html")

  except Exception as e:
    cursor.close()
    errorMessages.append('You are already following this person!')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)


@app.route("/newslogin/", methods=["POST", "GET"])
def newslogin():
  return render_template("newslogin.html")


@app.route("/viewfeed/", methods=["POST", "GET"])
def viewfeed():

  errorMessages = []

  username=request.form['username']
  password=request.form['password']

  # Check if username exists. It should.

  user_id = -1
  username_exists = False
  cursor = g.conn.execute("SELECT username,user_id FROM users WHERE username=%s", username)
  
  for result in cursor:
    username_exists = True
    user_id = result['user_id']
    break
  cursor.close()

  if username_exists == False:
    errorMessages.append('Username does not exist.')
    context=dict(errors=errorMessages)
    return render_template("error.html", **context)


  cursor = g.conn.execute("SELECT password FROM users WHERE username=%s", username)
  for result in cursor:
    if result['password'] != password:
      errorMessages.append('Incorrect password.')
      context=dict(errors=errorMessages)
      return render_template("error.html", **context)
  cursor.close()

  # If you are at this point, then you have a valid username and password.

  # Maps a news_id to a list of celebrity names associated with that news
  news_dict = {}

  cursor = g.conn.execute("""
    SELECT n1.people_id, news_id, name 
    FROM notable_people_has n1 
    INNER JOIN notable_people_adder n2 
    ON (n1.people_id = n2.people_id)""")

  for result in cursor:
    news_id = result['news_id']
    name = result['name']

    if news_id not in news_dict:
      news_dict[news_id] = [name]
    else:
      news_dict.setdefault(news_id, []).append(name)

  # Aggregate the news rows

  sql_statement = "SELECT * from news INNER JOIN ( \
    SELECT p.news_id FROM notable_people_has p INNER JOIN (SELECT u.people_id FROM user_follows u WHERE u.user_id=" + str(user_id) + \
    ") AS foo ON p.people_id=foo.people_id) AS boo ON news.news_id=boo.news_id ORDER BY datetime DESC"

  # No chance for sql injection because no user input
  cursor = g.conn.execute(sql_statement)
  news = []
  # Result is one row
  for result in cursor:
    celebrity_list = []
    news_id=result['news_id']
    if news_id in news_dict:
      celebrity_list = news_dict[news_id]

    news.append(dict(source=result['source'], content=result['content'], datetime=result['datetime'], celebs=celebrity_list))
  
  cursor.close()


  sql_statement = "SELECT n.name,n.people_id FROM user_follows u INNER JOIN notable_people_adder n ON \
    u.people_id=n.people_id WHERE u.user_id=" + str(user_id)

  # No chance for sql injection because no user input
  cursor = g.conn.execute(sql_statement)
  people = []
  for result in cursor:
    name = result['name']
    people_id = result['people_id']
    people.append(dict(name=name,people_id=people_id))

  cursor.close()

  context = dict(data=news,username=username,people=people)
  return render_template("usernews.html", **context)


@app.route("/person/", methods=["POST", "GET"])
def get_person():

  target_id = int(request.args['id'])
  people_id = target_id
  context = dict()

  cursor = g.conn.execute("SELECT AVG(foo.rating_level) FROM (SELECT rating_level FROM submits WHERE \
    rating_week=(SELECT date_trunc('week', current_date)) AND people_id=%s) AS foo", people_id)
  
  average_rating = "(no ratings!)";
  for result in cursor:
    average_rating = result['avg'];
  average_rating = str(average_rating)

  if average_rating == "None":
    average_rating = "(no ratings!)"
  elif len(average_rating) >= 4:
    average_rating = average_rating[0:4]
  cursor.close()

  num_ratings = ""
  cursor = g.conn.execute("SELECT COUNT(foo.rating_level) FROM (SELECT rating_level FROM submits WHERE \
    rating_week=(SELECT date_trunc('week', current_date)) AND people_id=%s) AS foo", people_id)  
  for result in cursor:
    num_ratings = result['count']
  cursor.close()

  current_week = ""
  cursor = g.conn.execute("SELECT date_trunc('week', current_date)")
  for result in cursor:
    current_week = result['date_trunc']
    current_week = str(current_week)
    if len(current_week) >= 10:
      current_week = current_week[0:10]
  cursor.close()


  cursor = g.conn.execute("SELECT * FROM news n INNER JOIN notable_people_has p ON \
    n.news_id=p.news_id WHERE p.people_id=%s ORDER BY datetime DESC", people_id)
  news = []
  # Result is one row
  for result in cursor:
    news.append(dict(source=result['source'], content=result['content'], datetime=result['datetime']))
  cursor.close()
  
  num_followers = ""
  cursor = g.conn.execute("SELECT COUNT(foo.people_id) FROM (SELECT people_id \
    FROM user_follows WHERE people_id=%s) AS foo", people_id)
  for result in cursor:
    num_followers = result['count']
  cursor.close()

  cursor = g.conn.execute("SELECT * FROM notable_people_adder WHERE people_id=%s", target_id)

  # There should only be one result
  for result in cursor:
    pronoun = ""
    pronoun2 = ""
    if result['gender'] == 'M':
      pronoun = "He"
      pronoun2 = "His"
    else:
      pronoun = "She"
      pronoun2 = "Her"

    context = dict(
      num_followers=num_followers,
      data=news,
      current_week=current_week,
      num_ratings=num_ratings,
      average_rating=average_rating,
      birthday=result['birthday'],
      industry=result['industry'],
      pronoun=pronoun,
      pronoun2=pronoun2,
      people_id=result['people_id'], 
      net_worth=result['net_worth'],
      instagram_username=result['instagram_username'],
      twitter_username=result['twitter_username'],
      facebook_page_name=result['facebook_page_name'],
      user_id=result['user_id'],
      name=result['name'])
    break
  
  return render_template("person.html", **context)


@app.route("/leaderboard/", methods=["POST", "GET"])
def get_leaderboard():
  leaderboard=[]
  cursor = g.conn.execute("""
  SELECT * 
  FROM notable_people_adder n, weekly_leaderboard_ranks w 
  WHERE n.people_id=w.people_id AND w.week= (SELECT MAX(w2.week) 
                            FROM weekly_leaderboard_ranks w2)
  ORDER BY w.position ASC""")

  for result in cursor:
    week = result['week']
    name = result['name']
    position = result['position']
    people_id = result['people_id']
    leaderboard.append(dict(week = result['week'], name = result['name'], position = result['position'],people_id=result['people_id']))
  
  cursor.close()
  context = dict(data=leaderboard)
  return render_template("leaderboard.html", **context)


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a POST or GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
# 
@app.route('/', methods=["POST", "GET"])
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()


  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict( data = names )


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another/
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another/', methods=["POST", "GET"])
def another():
  return render_template("anotherfile.html")

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
