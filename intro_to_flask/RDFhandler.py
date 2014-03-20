from SPARQLWrapper import SPARQLWrapper, JSON
import uuid
from werkzeug import generate_password_hash, check_password_hash
sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
sparql.setQuery("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
INSERT DATA
{ <http://example/book3> a "sdlfs" . }  
""")
sparql.method = 'POST'
#sparql.setReturnFormat(JSON)
#results = sparql.query().convert()
sparql.query()
#for result in results["results"]["bindings"]:
#	print(result["A"]["value"])



def addUser( userid ,username , email , password , location , oauthtoken ,authtype,lng,lat):

	if userid == None:
	   	userid = str(uuid.uuid1())
	
	password = generate_password_hash(password)
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	if location == None:
		locSparqlString = ""
	else:
		locSparqlString = """<http://example/hasLocation> '"""+location+"""';
		<http://example/hasLng>  '"""+lng+"""';
		<http://example/hasLat>  '"""+lat+"""';"""
	q = """
	INSERT DATA
	{ <http://example.com/"""+ userid +""">     a             <http://example/User> ;
					  <http://example/hasPassword> '""" + password+"""';
					  <http://example/hasName> '""" + username+"""';
					  <http://example/hasEmail>	'"""+email+"""';
					  """ + locSparqlString + """
					  <http://example/hasOauthtoken> '"""+oauthtoken+"""';
					  <http://example/hasAuthType> <http://example/"""+ authtype +""">
	 }"""

	print q
	sparql.setQuery(q)
	
	sparql.method = 'POST'
	sparql.query()
	

def checkEmail(email) :

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """
	ASK
	{
	?user <http://example/hasEmail> '"""+email+"""'.
	}"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()

	return results["boolean"]



def authenticate(email,password):
	
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """
	SELECT ?password WHERE
	{
	?user <http://example/hasEmail> '"""+email+"""';
	      <http://example/hasPassword> ?password.
	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	
	resu = results['results']['bindings'][0]['password']['value']
	return check_password_hash(resu,password)


def userType(email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?userType WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '"""+email+"""';
	       <http://example/hasAuthType> ?userType.
	}"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	return results['results']['bindings'][0]['userType']['value'][15:]




def data_by_email(email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?username ?location ?userid WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '""" + email + """';	       
	       <http://example/hasName> ?username.
	       OPTIONAL{?userid <http://example/hasLocation> ?location.}
	       
	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	data = []
	print results
	data.append(results['results']['bindings'][0]['username']['value'])
	try :
		data.append(results['results']['bindings'][0]['location']['value'])
	
	except:
		data.append("Undefined")

	data.append(results['results']['bindings'][0]['userid']['value'])

	return data


def update_location(location, email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	q = """
	DELETE {?userid <http://example/hasLocation> ?location }
	INSERT {?userid <http://example/hasLocation> '""" + location+"""' } 
	WHERE{
	?userid <http://example/hasEmail>	'"""+email+"""' .
			OPTIONAL{
				?userid <http://example/hasLocation> ?location.
			}
	        
	}"""
	
	sparql.setQuery(q)
	sparql.method = 'POST'
	sparql.query()


def RDFlike( artistid, likeType , email):

	userid = getid_by_email(email)

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	q = """
	INSERT DATA
	{ <"""+userid+"""> <http://example/likes"""+likeType+"""> <http://musicbrainz.org/artist/""" +artistid+""">.
	}"""

	sparql.setQuery(q)
	
	sparql.method = 'POST'
	sparql.query()