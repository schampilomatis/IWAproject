from SPARQLWrapper import SPARQLWrapper, JSON
from RDFhandler import data_by_email
import uuid

def addEvent( email , artistid):


	data = data_by_email(email)
	userid = data[2]
	location = data[1]
	eventid = uuid.uuid1()

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	
	q = """
	INSERT DATA
	{ <http://example.com/"""+ eventid +"""> a <http://example.com/SuggestedEvent>.
	<http://example.com/"""+ userid +""">  <http://example/createdEvent> '""" + password+"""'.
	<http://example.com/"""+ eventid +"""> <http://example/aboutArtist> <http://musicbrainz.org/artist/""" +artistid+""">.
	<http://example.com/"""+ eventid +"""> <http://example/eventlocation> \""""+location+"""\".

	 }"""
	sparql.setQuery(q)
	
	sparql.method = 'POST'
	sparql.query()


def getEvents(artistid):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?eventid ?location WHERE {
	?eventid a <http://example/SuggestedEvent> ;
	       <http://example/aboutArtist> <http://musicbrainz.org/artist/""" +artistid+""">.
			<http://example/eventlocation> ?location.
	}"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	return results['results']['bindings']