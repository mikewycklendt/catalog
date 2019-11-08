from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash, g
from sqlalchemy import create_engine, asc, desc, DateTime
import datetime
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import time
from functools import update_wrapper

app = Flask(__name__)

CLIENT_ID = json.loads(
  open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogApp.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/home')
def showHome():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).join(Category,
                Category.id == Item.cat_id).order_by(desc(
                    Item.date_added)).limit(10)
    # if 'username' not in login_session:
    #  return render_template('publicrestaurants.html',
    #  restaurants=restaurants)
    # else:
    return render_template('home.html', categories=categories, items=items)


@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).filter_by(
                cat_id=category_id).order_by(desc(Item.date_added)).all()
    category = session.query(Category).filter_by(id=category_id).one()
    count = session.query(Item).filter_by(cat_id=category_id).count()
    return render_template('category.html', items=items,
            category=category, categories=categories, count=count)


@app.route('/item/<int:item_id>/')
def showItem(item_id):
    item = session.query(Item).join(Category,
               Category.id == Item.cat_id).filter(Item.id == item_id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicitem.html', item=item, creator=creator)
    else:
        return render_template('item.html', item=item, creator=creator)


@app.route('/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return """<script>function myfunction()
                {alert('You are not authorized to delete this restaurant.
                  Please create your own restaurant in order to delete.');}
                      </script><body onload='myfunction()''>"""
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('%s Successfully Deleted' % itemToDelete.title)
        session.commit()
        return redirect(url_for('showCategory',
                                category_id=itemToDelete.cat_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


@app.route('/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if editedItem.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert('You are not
                    authorized to edit this restaurant. Please create your
                        own restaurant in order to edit.');}</script>
                            <body onload='myFunction()''>"""
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.cat_id = request.form['category']

        flash('Item Successfully Edited %s' % editedItem.title)
        return redirect(url_for('showItem', item_id=editedItem.id))
    else:
        return render_template('editItem.html', item=editedItem,
                                categories=categories)


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    # if 'username' not in login_session:
    #  return redirect('/login')sud
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        flash('%s Category Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        return render_template('newCategory.html')


@app.route('/item/new/', methods=['GET', 'POST'])
@app.route('/item/new/<int:categoryid>/', methods=['GET', 'POST'])
def newItem(categoryid=1):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if request.method == 'POST':
        newItem = Item(title=request.form['title'],
                        cat_id=request.form['category'],
                        description=request.form['description'],
                        user_id=login_session['user_id'])
        session.add(newItem)
        flash('%s Item Successfully Added' % newItem.title)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        return render_template('newItem.html', categories=categories,
                                categoryid=categoryid)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
        response = make_response(json.dumps(
                            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("""Token's user ID doesn't
                                            match given user ID."""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("""Token's client ID does not
                                            match app's."""), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user
                                            is already connected.'''),
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
    output += ''' " style = "width: 300px; height: 300px;border-radius:
                150px;-webkit-border-radius: 150px;-moz-border-radius:
                    150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


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


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('''Current user not
                                            connected.'''), 401)
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
        response = make_response(json.dumps('''Failed to revoke token for given
                                            user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/items/JSON')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    return jsonify(users=[i.serialize for i in users])


@app.route('/JSON')
def categoriesItemsJSON():
    all = session.query(Category).options(joinedload(Category.item)).all()
    return jsonify(all=[dict(a.serialize,
        item=[i.serialize for i in a.item]) for a in all])


@app.route('/JSON/item/<int:item_id>')
def itemJSON(item_id):
    item = session.query(Item).filter_by(Item.id == item_id).one()
    return jsonify(item=[i.serialize for i in item])


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def createUser(login_session):
    newUser = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.run()
