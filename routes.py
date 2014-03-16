from flask import Flask, render_template, request , Response
import musicbrainzngs
import json

app = Flask(__name__)
  
@app.route('/')
def home():
  return render_template('home.html')
  
@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/search')
def search():
	return render_template('search.html')

@app.route('/results')
def results():
	musicbrainzngs.set_useragent("iwa",1.0)
	musicbrainzngs.auth("stavros","123")
	result = musicbrainzngs.search_artists(artist = request.args.get('artist',''),tag = 'gay',strict = False,limit=None)
	return Response(json.dumps(result['artist-list']),mimetype='application/json')
		

sadfsd
 
if __name__ == '__main__':
  app.run(debug=True)
