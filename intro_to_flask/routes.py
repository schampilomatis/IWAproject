from intro_to_flask import app
from flask import Flask, render_template, request, flash, session, redirect, url_for
from forms import ContactForm, SignupForm, SigninForm
from flask.ext.mail import Message, Mail
from models import db, User
from
from flask_oauth import OAuth
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
import json
from urllib2 import Request, urlopen, URLError



#--------------------------------------------------------------------------------------------------

FACEBOOK_APP_ID = '1425475621033434'
FACEBOOK_APP_SECRET = '5fa7fbad4a2edcc639524fd71f34fa09'

GOOGLE_CLIENT_ID = '485739322209-764j5vj22o5uc869bjpuuaqer03d08oq.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'f3F0UksoCqiO1tuTrGYC1oLV'
REDIRECT_URI = '/authorized'


#---------------------------------------------------------------------------------------------------

oauth = OAuth()
mail = Mail()


@app.route('/')
def home():
  return render_template('home.html')


#--------------------------------------------------------------

@app.route('/about')
def about():
  return render_template('about.html')

#---------------------------------------------------------------

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:

    	msg = Message(form.subject.data, sender='marla.yk@gmail.com', recipients=['marla.yk@gmail.com'])
    	msg.body = """
    	From: %s <%s>
    	%s
    	""" % (form.name.data, form.email.data, form.message.data)
    	mail.send(msg)

    	return render_template('contact.html', success=True)
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)





@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()

  if 'email' in session:
    return redirect(url_for('profile'))
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      newuser = User(form.username.data, form.email.data, form.password.data, form.location.data, None)
      db.session.add(newuser)
      db.session.commit()  

      session['email'] = newuser.email
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signup.html', form=form)


@app.route('/profile')
def profile():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
 
  user = User.query.filter_by(email = session['email']).first()
 
  if user is None:
    return redirect(url_for('signin'))
  else:
    return render_template('profile.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()

  if 'email' in session:
    return redirect(url_for('profile'))
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))
                 
  elif request.method == 'GET':
    return render_template('signin.html', form=form)



@app.route('/signout')
def signout():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
     
  session.pop('email', None)
  return redirect(url_for('home'))



#------------------------------------------------------
#--------    FACEBOOK   -------------------------------
#------------------------------------------------------


facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email, user_location'}
)


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    user = User.query.filter_by(email = me.data['email']).first()
    if user is None:

      newuser = User(me.data['username'],me.data['email'], me.data['id'], me.data['location']['name'],resp['access_token'])
      db.session.add(newuser)
      db.session.commit() 

    else:
      session['email'] = me.data['email']
      return redirect(url_for('profile'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


#------------------------------------------------------
#--------    GOOGLE   -------------------------------
#------------------------------------------------------

google = oauth.remote_app('google',
        base_url='https://www.google.com/accounts/',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        request_token_url=None,
        request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_method='POST',
        access_token_params={'grant_type': 'authorization_code'},
        consumer_key=GOOGLE_CLIENT_ID,
        consumer_secret=GOOGLE_CLIENT_SECRET)


@app.route('/glogin')
def glogin():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)



@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token
    

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('glogin'))
    
    return res.read()   
   # session['email'] = json.load(res)['email']
   # return redirect(url_for('profile'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')