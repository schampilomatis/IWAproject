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



def addUser( userid ,username , email , password , location , oauthtoken ,authtype):

	if userid == None:
		userid = str(uuid.uuid1())

	
	password = generate_password_hash(password)
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	if location == None:
		locSparqlString = ""
	else:
		locSparqlString = "<http://example/hasLocation> '"+location+"';"
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



def user_by_email(email):

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?userid  ?password WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '""" + email + """';
	       <http://example/hasPassword> ?password.
	}
	"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()


	return results['results']['bindings'][0]['password']['value']


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

	

def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
   
def check_password(self, password):
    return check_password_hash(self.pwdhash, password)