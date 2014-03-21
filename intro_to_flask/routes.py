from intro_to_flask import app
from flask import Flask, render_template, request, flash, session, redirect, url_for,jsonify
from forms import ContactForm, SignupForm, SigninForm, SearchForm
from flask.ext.mail import Message, Mail
from models import db, User
from flask.ext.wtf import Form
from flask_oauth import OAuth
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
import json
import urllib2
from urllib2 import Request, urlopen, URLError
from RDFhandler import addUser, checkEmail , userType, data_by_email, update_location ,latlng_by_email
import musicbrainzngs
import pylast

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
  return render_template('index.html')


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

      addUser(None,form.username.data,form.email.data.lower(),form.password.data,form.location.data,"","Normal", form.lng.data , form.lat.data)

      session['email'] = form.email.data.lower()
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signup.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def profile():

  if 'email' not in session:
    return redirect(url_for('signin'))

  data = data_by_email(session['email'])
  print data
  return render_template('profile.html', username=data[0], location=data[1] )


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



@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500


@app.route('/changeLocation', methods=['GET', 'POST'])
def changeLocation():

  location=request.args.get("location")
  lat=request.args.get("lat")
  lng=request.args.get("lng")
  print session['email']
  update_location(location,lat,lng, session['email'])
  return "ok"

@app.route('/getLatLng', methods=['GET', 'POST'])
def getLatLng():
  data =  latlng_by_email(session['email'])
  
  result = {"lat": data[0] , "lng" : data[1] }
  return json.dumps(result)





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
     
    if checkEmail(me.data['email'])== False :
      url = "http://graph.facebook.com/"+ me.data['location']['id']
      result = urllib2.urlopen(url).read()
      result = json.loads(result)

      addUser(me.data['id'],me.data['username'], me.data['email'], 'abcde',me.data['location']['name'],resp['access_token'],"facebook",str(result['location']['longitude']),str(result['location']['latitude']))
      session['email'] = me.data['email'] 
      return redirect(url_for('profile'))      
    else:
      if userType(me.data['email']) == "facebook":
        session['email'] = me.data['email']
        return redirect(url_for('profile'))
      else:
        form = SigninForm()
        form.email.errors = ["Wrong Account Type"]
        return render_template('signin.html', form=form)
      


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

    res = json.load(res)
    if checkEmail(res['email'])== False :

      addUser(res['id'],res['name'],res['email'],"123",None, access_token , "google",None, None)
      session['email'] = res['email']

      return  redirect(url_for('profile'))    
    else:
      if userType(res['email']) == "google":
        session['email'] = res['email']

        return  redirect(url_for('profile'))
      else:
        form = SigninForm()
        form.email.errors = ["Wrong Account Type"]
        return render_template('signin.html', form=form)

@google.tokengetter
def get_access_token():
    return session.get('access_token')



##############-------------------------------------------------------------------------


@app.route('/artists', methods=['GET', 'POST'])
def artists():
  q = request.args.get('artist')
  musicbrainzngs.set_useragent("test",1,None)
  artists = musicbrainzngs.search_artists(q)

  return jsonify(artists)


@app.route('/songs',methods=['GET', 'POST'])
def songs():
  id = request.args.get('id')


  API_KEY = '4bea9a7cfe15b09d2ada827592605ee0'
  API_SECRET = '13b346b26064a3537796608d27802711'

  username = "nicksar11"
  password_hash = pylast.md5("cavcle501")
  network = pylast.LastFMNetwork(api_key=API_KEY,api_secret=API_SECRET,username=username,password_hash=password_hash)

  fetchedArtist = network.get_artist_by_mbid(id)
  tracks = fetchedArtist.get_top_tracks()

  result = ""
  for track in tracks:
    result = result + "<div class='row'><a Onclick=\'getvideo(\""+str(track[0]).decode('utf-8')+"\")\'>"+track[0].get_name()+"</a> <button onclick='likeSong(\""+track[0].get_id()+"\")' class='btn-xs pull-right btn btn-primary' >LIKE</button></div>"
  return result

@app.route('/like')
def like():
  if 'email' not in session:
    return "Not logged in"

  ArtistId = request.args.get('id')
  likeType = request.args.get('likeType')
  RDFlike(ArtistId, likeType ,session['email'])
  return "Ok"




@app.route('/browseArtists')
def browseArtists():
  return render_template('browseArtists.html')

@app.route('/test')
def test():
  return render_template('test.html')