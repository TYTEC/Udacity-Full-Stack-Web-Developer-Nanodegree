# Improt Flask class from Flask libary
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask import make_response
import json

from flask_images import Images
import os
from werkzeug.utils import secure_filename
from werkzeug import url_decode

# import CRUD Operations
from database_setup import Base, Category, Dish, User
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

# Imports necessary for login
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2


# Create instance of the class
# With the name of the running application as argument (application object)
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'i'
app.secret_key = 'super_secret_key'
images = Images(app)

# Create client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"



# Create session and connect to DB
engine = create_engine('sqlite:///japanesefood.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



# Create anti-forgery state token
# It wll be stored in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html',  STATE=state)


# Add GConnect function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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
    return redirect(url_for('categories'))

# DISCONNECT - Revoke a current user's token and reset their login_session


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
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

        

@app.route('/uploads/<filename>', methods=["GET"])
def download_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# API endpoints for all users
@app.route('/users.json')
def userJSON():
  users = session.query(User).all()
  return jsonify(User = [u.serialize for u in users])


# add API endpoints for all categories and items
@app.route('/catalog/json')
def catalogJSON():
  categories = session.query(Category).all()
  items = session.query(Dish).all()
  return jsonify(Categories = [c.serialize for c in categories], Items = [i.serialize for i in items])

# add API endpoints for all categories
@app.route('/categories/json')
def categoriesJSON():
  categories = session.query(Category).all()
  return jsonify(Categories = [c.serialize for c in categories])

# API endpoints for all items from a specific category
@app.route('/<category_name>/items/json')
def itemsJSON(category_name):
  category = session.query(Category).filter_by(name=category_name).one()
  items = session.query(Dish).filter_by(category=category).all()
  return jsonify(Items = [i.serialize for i in items])

@app.route('/<category_name>/<item_name>/json')
def itemJSON(category_name, item_name):
  category = session.query(Category).filter_by(name=category_name).one()
  item = session.query(Dish).filter_by(category=category).one()
  return jsonify(Item = [i.serialize for i in item])

# Show home page (this is the front page for the application)
@app.route('/')
def home():
    return render_template('home.html')
# Show about page
@app.route('/about')
def about():
    return render_template('about.html')


# Show contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Show catalog page with all the category items
@app.route('/catalog')
def categories():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Dish).order_by(asc(Dish.name))
    for i in items:
      i.image = i.image.replace("/static/", '')
      print(i.image)
    return render_template('catalog.html', categories=categories, items=items) 
   

# Show all items in the category

@app.route('/catalog/<category_name>/items')
def allCategoryItems(category_name):
  categories = session.query(Category).order_by(asc(Category.name))
  selectedCategory = session.query(Category).filter_by(name=category_name).one()
  items = session.query(Dish).filter_by(category_id=selectedCategory.id).order_by(asc(Dish.name))
  return render_template('catalog.html', categories=categories, selectedCategory=selectedCategory, items=items)



# Show detailed info on selected dish
@app.route('/catalog/<category_name>/<item_name>')
def showItem(category_name, item_name):
  category = session.query(Category).filter_by(name=category_name).one()
  item = session.query(Dish).filter_by(name=item_name, category=category).one()
  return render_template('showItem.html', item=item)

# Add new category
@app.route('/catalog/addcategory', methods=['GET','POST'])
def addCategory():
  if request.method == 'POST':
    addCategory = Category(name=request.form['name'])
    session.add(addCategory)
    session.commit()
    flash("You've successfully added new category!")
    return redirect(url_for('categories'))
  else:
    return render_template('addCategory.html', )



# Add a new item



# Delete category
@app.route('/catalog/deletecategory', methods=['GET','POST'])
def deleteCategory():
  categories = session.query(Category).order_by(asc(Category.name))
  # Delete category from the database 
  if request.method == 'POST':
    session.delete(categoryToDelete)
    session.commit()
    return redirect(url_for('categories'))
  return render_template('deleteCategory.html', category=categoryToDelete)



# Create routing to the include_del_cat.html code snippet

@app.route('/include', methods=['GET','POST'])
def include_del_cat():

  return render_template('include_del_cat.html')



# Edit category
#@app.route('/catalog/<category_name>/edit', methods=['GET','POST'])
#def editCategory(category_name):
 #   findCategory = session.quert(Category).filter_by(name=category_name).one()
 #   if request.method == 'POST':
  #      findCategory.name = request.form['name']
   #     session.delete(categoryToDelete)
    #    session.commit()
     #   return redirect(url_for('home'))
    #else:
     #   return render_template('editCategory.html')


# Add new item to a category

@app.route('/catalog/additem', methods=['GET','POST'])
def addItem():
  categories = session.query(Category).order_by(asc(Category.name))
  if request.method == 'POST':
    itemName = request.form['name']
    itemDescription = request.form['description']
    itemCategory = session.query(Category).filter_by(name=request.form['category']).one()
    itemImage = request.form['image']
    if itemName != '':
      print("item name %s" % itemName)
      addingItem = Dish(name=itemName, description=itemDescription, image=itemImage, category=itemCategory,
                        user_id=itemCategory.user_id)
      session.add(addingItem)
      session.commit()
      return redirect(url_for('categories'))
    else:
      return render_template('addItem.html', categories=categories)
  else:
    return render_template('addItem.html', categories=categories)


# Delete  item to a category

# Edit  item to a category

# Add routing to error 404 and 505 pages

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500



# Execute only if file is run by python interpreter
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.secret_key = 'super_secret_key'
	# Reload server when code changes
  app.debug = True
  threaded=True
	# Run local server with the application
	# Listen on all public addresses
  app.run(host='0.0.0.0', port=5000)
