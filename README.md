# Project 1: Item Catalog

## Description

This project is a website for sports items sorted by category.  It uses a database that has three tables: Item, Category and User.

In order to run this program you need to have a virtual machine installed.  I use vagrant and virtualbox which are free for download.  Once you have installed vagrant and virtualbox log, unzip the file into the vagrant directory.  Login to the server with vagrant ssh, navigate to vagrant/catalog and then run database_setup.py to create the database.  This project also uses redis server to limit the amount of posts the user can make in a short period of time.  Open a seperate instance of the vagrant server, install redis server from redislabs.com and on the vagrant machine and run it by typing redis-server into the command line.  Once you have done all this, run application.py to start the website and view it at http://localhost:8000/.

Next, navigate to http://localhost:8000/category/new/ and create the following categories:

1. Baseball
2. Basketball
3. Foosball
4. Frisbee
5. Hockey
6. Rock Climbing
7. Skating
8. Snowboarding
9. Soccer

This is the list I got from the project description page in the udacity course.  Curiously, udacity chose to omit the sport of american football, the most popular sport in the country.


You also need to create an account with google for the Login API.  Once you have done this, copy paste your client id into the start function on login.html and several lines below after:

```
<meta name="google-signin-client_id" content=
```

Then open client_secrets.json and copy paste the client id and client secret google provides you with in their respepctive fields.

This project runs off two python files, application.py and database_setup.py.  application.py builds the site and database_setup.py builds the database.  The site also uses CSS for much of the page design that comes from bootstrap and styles.css located in the static directory.  The pages for the sites are located in the templates folder and referenced by application.py to create the HTML for the website.

## Home

```
@app.route('/')
@app.route('/home')
def showHome():
  categories = session.query(Category).order_by(asc(Category.name)).all()
  items = session.query(Item).join(Category, Category.id == Item.cat_id).order_by(desc(Item.date_added)).limit(10)
  #if 'username' not in login_session:
  #  return render_template('publicrestaurants.html', restaurants=restaurants)
  #else:
  return render_template('home.html', categories = categories, items = items)
```

The home page is fairly simple.  It makes two queries from the database--one from the Category database to create the list of tables and one from the Item database to create a list of the ten most recent items ordered from newest to oldest.  It stores the queries in 'categories' and 'items' and home.html uses the information stored in those objects.

In home.html there is an if statement:

```
	{%if 'username' not in session %}
		{% else %}
		<div class="row">
			<br><a href="{{url_for('newItem')}}"><button class="btn add" id="add">Add Item</button></a>
		</div>	
	{% endif %}
```

This looks to see if the user is logged in and if there is a username found in the session it displays a button that allows them to add an item to the database.

Every page includes header.html.  In header.html, the catalog app banner is created and there is an if statement:

```
{%if 'username' not in session %}
	<a href="{{url_for('showLogin')}}"><button class="btn login" id="login">Login</button></a>
{% else %}
	<a href="{{url_for('disconnect')}}"><button class="btn login" id="login">Logout</button> </a>
{% endif %}
```

If a username is found in the session, a login button is shown that directs the user to the login page.  If no username is in the session, a logout button is shown that directs the user to the disconnect route.


## Category Page

```
@app.route('/category/<int:category_id>/')
def showCategory(category_id):
  categories = session.query(Category).order_by(asc(Category.name)).all()
  items = session.query(Item).filter_by(cat_id = category_id).order_by(desc(Item.date_added)).all()
  category = session.query(Category).filter_by(id = category_id).one()
  count = session.query(Item).filter_by(cat_id = category_id).count()
  return render_template('category.html', items = items, category = category, categories = categories, count = count)
```

Once a user clicks a category they are taken to http://localhost:800/category/(category_id).  This page is made up of four queries.  

The first query creates the list of categories shown on the right.  

The second query shows the list of items in the chosen category ordered by newest to oldest.  

The third is to get the name of the chosen category.  

The fourth is to get the number of items for the chosen category.



category.html has the same if statement as home.html to check to see if a username is found in the session:

```
		{%if 'username' not in session %}
		{% else %}
			<br>
			<div class="row">
				<a href="{{url_for('newItem', categoryid = category.id)}}">
					<button class="btn add" id="add">Add Item</button>
				</a>
			</div>
		{% endif %}
```

The difference with this if statement is that it passes the category id into the url so when the user clicks to add a new item the category for the item they want to add is automatically selected on the new item page.


## Item page

The item page makes two queries

```
@app.route('/item/<int:item_id>/')
def showItem(item_id):
  item = session.query(Item).join(Category, Category.id == Item.cat_id).filter(Item.id == item_id).one()
  creator = getUserInfo(item.user_id)
  if 'username' not in login_session or creator.id != login_session['user_id']:
  	return render_template('publicitem.html', item = item, creator =  creator)
  else:
  	return render_template('item.html', item = item, creator = creator)
```

The first query queries the Item database and filters it by the item id from the URL.  

The second query uses the getUserInfo function to retrieve the user information of the user who added the item to the database.  

```
def getUserInfo(user_id):
  user = session.query(User).filter_by(id = user_id).one()
  return user
```

This function queries the User database and filters it by the id of the user found in the login session and returns the user information and stores it in the creator object.  Then on the item.html page the user's image and name is displayed to the right of the Item name.

There is also an if statement that checks to see if the user who is logged in is the same user who created the item.  If it is, it displays item.html which has buttons to edit or delete the item.  If it isn't, it displays publicitem.html that does not allow the user to edit or delete the item.

## Delete Item page

This is the page that allows a user to delete an item that they created.

```
@app.route('/item/<int:item_id>/delete/', methods = ['GET','POST'])
def deleteItem(item_id):
  if 'username' not in login_session:
    return redirect('/login')
  itemToDelete = session.query(Item).filter_by(id = item_id).one()
  if itemToDelete.user_id != login_session['user_id']:
    return "<script>function myfunction() {alert('You are not authorized to delete this restaurant.  Please create your own restaurant in order to delete.');}</script><body onload='myfunction()''>" 
  if request.method == 'POST':
    session.delete(itemToDelete)
    flash('%s Successfully Deleted' % itemToDelete.title)
    session.commit()
    return redirect(url_for('showCategory', category_id = itemToDelete.cat_id))
  else:
    return render_template('deleteItem.html', item = itemToDelete)
 ```

 This page uses three if statements.  

 The first if statement checks to see if the user is logged in.  If they aren't, it redirects them to the login page.  

 Before the second if statement is a query that queries the Item database and filters it for the item that the user wants to delete by using the item id stored in the url.  

 The second if statement checks to see if the user who is logged in is the same user who created the item.  If it is not, it tells the user that they are not authorized to delete the item.  

 The third if statement checks to see if the user has clicked the delete item button and if they have it deletes the item from the database and sends a flash message that is shown on the category page for the category the item had been placed in.  The else part of the if statement displays the delete item page if the user has not clicked the delete item button yet.

## Edit Item page

This page allows a user to edit an item stored in the database.\

```
@app.route('/item/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(item_id):
  if 'username' not in login_session:
    return redirect('/login')
  editedItem = session.query(Item).filter_by(id = item_id).one()
  categories = session.query(Category).order_by(asc(Category.name)).all()
  if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
  if request.method == 'POST':
      if request.form['title']:
        editedItem.title = request.form['title']
      if request.form['description']:
      	editedItem.description = request.form['description']
      if request.form['category']:
      	editedItem.cat_id = request.form['category']
        
      flash('Item Successfully Edited %s' % editedItem.title)
      return redirect(url_for('showItem', item_id = editedItem.id))
  else:
    return render_template('editItem.html', item = editedItem, categories = categories)
```

This page uses six if statements.  

The first if statement checks to see if the user is logged in.  If they are not, it redirects them to the login page.  

Before the second if statement there are two queries.  The first queries the Item database and filters it by the item id for the item chosen to be edited chosen by the item id found in the url.  The second queries the Category database to display all the categories the user can select from the dropdown menu on the form.  

The second if statement checks to see if the user who is logged in is the user who created the item.  If it isn't, it sends a message to the user that they are not authorized to edit the item.

The third if statement contains three if statements and checks to see if the user has clicked the edit item button.  The first checks to see if the user edited the title, if it is it stores the name in the editedItem object.  The second checks to see if the description was edited.  If it was it stores the description in the editedItem object.  The third checks to see if the category was edited, if it was it stores the category in the editedItem object.  Then there is a flash message that tells the user they successfully edited the item on the item page for the item they edited.  The else part of this statements displays the edit item page if the user has not clicked the edit item button yet.

## New Category page

This page is not accessible through the website.  It is used by you to create the list of categories for the website.

```
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
  #if 'username' not in login_session:
  #  return redirect('/login')
  if request.method == 'POST':
      newCategory = Category(name = request.form['name'])
      session.add(newCategory)
      flash('%s Category Successfully Created' % newCategory.name)
      session.commit()
      return redirect(url_for('showHome'))
  else:
      return render_template('newCategory.html')
 ```

## New Item page

This is the page where the user can add an item to the database.

```
@app.route('/item/new/', methods=['GET','POST'])
@app.route('/item/new/<int:categoryid>/', methods=['GET','POST'])
@ratelimit(limit=30, per=60 * 1)
def newItem(categoryid=1):
  if 'username' not in login_session:
    return redirect('/login')
  categories = session.query(Category).order_by(asc(Category.name)).all()
  if request.method == 'POST':
      newItem = Item(title = request.form['title'], cat_id = request.form['category'], description = request.form['description'], user_id = login_session['user_id'])
      session.add(newItem)
      flash('%s Item Successfully Added' % newItem.title)
      session.commit()
      return redirect(url_for('showHome'))
  else:
      return render_template('newItem.html', categories = categories, categoryid = categoryid)
```

This page has two potential urls.  The first is used if the user clicks the add item button on the home page.  The second is used if the user clicked the add item button on the category page and if they did, the category id for the category page the user was on is passed to the url.

This page also limits the rate of items the can be added to the database to prevent a malicious bot from flooding the database with POST requests.

This page is created through a newitem functio that constains two if statements. If the categoryid variable is not found in the url the selected category defaults to the category with the id of 1.

The first if statement in the newItem function checks to see if the user is logged in.  If they are not, it redirects them to the login page.

Before the second if statement is a query that queries the Category database and orders it alphebetically by category name in ascending order.

The second if statemnt checks to see if the user has clicked the add item button.  If they have it stores the content from the title, category and description elements from the form in newItem.html and adds them to the newItem object.  Then the newItem object is added to the session.  Then there is a flash message that tells the user they have successfully added a new item to the database.  Then the item is commited to the database and the user is redirected to the homepage.  The else part of this statement displays the newItem.html page if the user has not clicked the add item button yet.  It passes the categories object that is called in newItem.html and the categoryid variable that defines which category is selected in the category drop down menu.

## Login process

The login process is made up of three elements.  Two routes and a function.

1. Login page

This route displays the page where the user can login.

```
@app.route('/login')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
  login_session['state'] = state
  return render_template('login.html', STATE=state)
```

This page is created through a function named showLogin.  It creates a variable called state that is a string of 32 random letters and digits.  Then it stores the state in login_session.  After that it displays the login.html page and passes the state variable into the name STATE.

the gconnect route is where the google api script directs the user once they have logged in.  The google script stores the STATE variable created in the showLogin function above.

```
@app.route('/gconnect', methods=['POST'])
def gconnect():
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  code = request.data
  try:
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'
    return response
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  if result['issued_to'] != CLIENT_ID:
    response = make_response(json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match app's."
    response.headers['Content-Type'] = 'application/json'
    return response
  
  stored_access_token = login_session.get('access_token')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_access_token is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('Current user is already connected.'),
                                 200)
    response.headers['Content-Type'] = 'application/json'
    return response

    # Store the access token in the session for later use.
  login_session['provider'] = 'google'
  login_session['access_token'] = credentials.access_token
  login_session['gplus_id'] = gplus_id

    # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)

  data = answer.json()

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash("you are now logged in as %s" % login_session['username'])
  print "done!"
  return output
  ```

First, it checks to see if the state passed in the google script matches the state that was created in the showLogin function and stored in login_session.  If the states do not match it sends a 401 error message.

Then the data from the request is passed into the code object.

Then the oauth module is called and does it's thing from the client_secrets.json file.  It creates a credentials object through Google's API. If there is a problem it returns a 401 error.

Then the access token is stored in the access_token variable found from the credentials object.

The url for google's API is created in a url string variable that includes the access token from the access_token variable.

Then the httplib module is called.  After that a GET request is sent to google's API using the url variable that was just created.

If the GET result fails it returns a 500 error.

Then a variable gplus_id is created retrieving the id from the credentials object.

If gplus_id does not match the id stored in the result object, a 401 error is returned.

If CLIENT_ID does not match what was stored in the result object, a 401 error is returned.

Then, a variable named stored_access_token is created taken from the login_session. A variable named stored_gplus_id is also created from login_session.

Then there is an if statement that uses the two above variables to check to see if the user is already logged in.  If they are, it sends a 200 response saying the user is already connected.

Then provider, access_token and gplus_id are added to login_session.

After that, a string variable called userinfo_url is created with the google API url. The parameter access_token is set from the credentials object and then a request is sent to google's API and the response is stored in a json object named answer that contains the user's information that the google API has returned.

Then an object named data is created from the answer json object.  the user's username, picture and email are added to the login_session from the data object.

After that, a variable named user_id is created from the getUserID function that passes the email stored in login_session:

```
def getUserID(email):
  try:
    user = session.query(User).filter_by(email = email).one()
    return user.id
  except:
    return None
```

First, the function queries the User table from the database and tries to filter it by the email passed into the function.  If it cannot (because there is no user in the database with that email) the function returns None.

If the getUserID function returned None the user_id variable is created with the createUser function that passes everything from login_session into it:

```
def createUser(login_session):
  newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email = login_session['email']).one()
  return user.id
```

A newUser object is created for the User table from the database and the name, email and picture columns are populated by the information stored in login_session.  the newUser object is added to the session and then committed.

An object named user is created by querying the User table from the database and filtering it by the user's email from the email field in the table and the email stored in login_session.

Then the function returns the user's id.

After one of the above two functions has been ran and returned the user's id, the user id is added to login_session.

Once all of the above has been run, some html showing the user's information is shown and a flash is created that tells the user they are logged in as their username.  Google's script in login.html displays this for several seconds before redirecting the user to the home page that tells them they are logged in and the login button on the homepage is changed to the logout button.

## Logout process

The logout process is handled by two routes.  The first is /disconnect and is what the logout button is directed to:

```
@app.route('/disconnect')
def disconnect():
  if 'username' in login_session:
    gdisconnect()

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']


    flash("You have successfully logged out.")
    return redirect(url_for('showHome'))
  else:
    flash("You were not logged in to begin with!")
    return redirect(url_for('showHome'))
```

The route is handled through a function named disconnect.

The first thing the function does is, through an if statement, check to see if there is a username in login_session.  If there is, it directs to the gdisconnect route.

After the gdisconnect function from the /gdisconnect route is complete, the user's username, email, picture, user_id and provider are deleted from login_session.

A flash message telling the user that they are logged out is created and the user is redirected to the homepage where the flash message tells them they are logged out.

If a username is not found in login_session, a flash is created that directs the user to the home page and tells them that they were not logged in.

The gdisconnect function is found in the /gdisconnect route:

```
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return "you have been logged out"
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
 ```

 The first thing the gdisconnect function does is create a variable named access_token that is retrieved from login_session.  If no access token is found from login_session, a 401 response stating that the user is not connected is returned.

 Three lines are then printed to the console, stating the access token and the username.

 Then a string variable called url is created that adds the access token to google's API url.

 After that, the httplib2 module is called.

 A GET request is sent to google's API using the url variable and the results from the request are stored in an object called result and the result is printed to the console.

 If the GET request returns a 200 response the access token and gplus id are removed from login_session.  Then a response stating that the user has disconnected is returned.

 If the GET request did not return a 200 response, a 400 error response is returned stating that the application has failed to revoke the token for the user.

## JSON routes

There are three json routes that show the contents of the database:

```
@app.route('/items/JSON')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(items= [i.serialize for i in items])
```

This route can be viewed at http://localhost:8000/items/JSON.  It queries the Item table from the database and stores them all into an items object.  The items object is serialized in a json formed and returned to the browser, showing all the items from the database.

```
@app.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    return jsonify(users= [i.serialize for i in users])
```

This route can be viewed at http://localhost:8000/users/JSON.  It queries the User table from the database and stores them in an object called users.  Then the users object is serialized in a json format and returned to the browser, showing all users from the database.

```
@app.route('/JSON')
def categoriesItemsJSON():
	all = session.query(Category).options(joinedload(Category.item)).all()
	return jsonify(all = [dict(a.serialize, item=[i.serialize for i in a.item]) for a in all])
```

This route can be viewed at http://localhost:8000/JSON.  It queries the Category table from the database and joins the item table from the database to it and stores it in a variable called all.  Then the all object is serialized and the items are serialized within it so it displays each category from the tables with the items for each category nested within each category.