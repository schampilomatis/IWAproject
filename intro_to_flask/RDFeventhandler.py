from SPARQLWrapper import SPARQLWrapper, JSON
from RDFhandler import data_by_email
import uuid

def addEvent(email, artistid):


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


def request_events(mbid):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ 
	SELECT DISTINCT ?eventid ?location (COUNT(?eventid) AS ?votes)
	WHERE {
	?eventid a <http://example/Event> ;
	        <http://example/hasArtistId> <http://www.musicbrainz.org/artist/""" +mbid+""">;
			<http://example/hasCity> ?location;
			<http://example/hasSource> "manually";
			<http://example/hasbeenVoted> ?user;

	}GROUP BY ?eventid ?location """
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	return results['results']['bindings']


def event_vote(eventid,email):
	data = data_by_email(email)
	userid = data[2]
	print eventid , userid

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	
	q = """
	INSERT DATA
	{ <http://example/"""+ eventid +""">  <http://example/hasbeenVoted> <"""+userid+""">.
	 }"""
	sparql.setQuery(q)
	
	sparql.method = 'POST'
	sparql.query()
	return True

def dbid_from_mbid(mbid):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	
	q = """
	
    SELECT ?artistid
    WHERE { 
    	
      ?artistid <http://www.w3.org/2002/07/owl#sameAs> <http://zitgist.com/music/artist/"""+mbid+"""> .
      
    }
	"""
	sparql.setQuery(q)
	
	sparql.setReturnFormat(JSON)
	sparql.method = 'GET'
	results = sparql.query().convert()
	try:
	  resu = results['results']['bindings'][0]['artistid']['value']
	except:
	  resu = ""

	return resu



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



def getartistinfo(mbid,artistname):

	dbid = dbid_from_mbid(mbid)

	if (dbid!=""):
	  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	
	  q =	"""
	  prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
      SELECT ?info 
 
      WHERE { 
    	
      <"""+dbid+"""> rdfs:comment ?info.
     	
      FILTER(langMatches(lang(?info), "EN")).
      
      }
	  """

	  sparql.setQuery(q)
	  print q
	  sparql.setReturnFormat(JSON)
	  results = sparql.query().convert()
	  try:
	   	return results['results']['bindings'][0]['info']['value']
	  except:
		return "No Info found"

	else:
	  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	  sparql.setQuery("""
	  prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
      SELECT ?artist ?info 
      WHERE { 
    	{
      ?artist rdf:type dbpedia-owl:Artist.
      ?artist rdfs:label ?name.
      ?artist rdfs:comment ?info.
     	}UNION{
      ?artist rdf:type dbpedia-owl:Band.
      ?artist rdfs:label ?name.
      ?artist rdfs:comment ?info.
     	}
      FILTER(langMatches(lang(?info), "EN")).
      FILTER regex(?name, '"""+artistname+"""')
      }
	  """)


	  sparql.setReturnFormat(JSON)
	  results = sparql.query().convert()
	  try:
		return results['results']['bindings'][0]['info']['value']
	  except:
		return "No Info found"



def getinterestingEvents(email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT DISTINCT ?eventid ?artist ?location ?lat ?lng (COUNT(?eventid) AS ?votes) WHERE {
	?eventid a <http://example/SuggestedEvent> ;
	       <http://example/aboutArtist> ?artist;
			<http://example/eventlocation> ?location;
			<http://example/hasLat>   ?lat;
			<http://example/hasLng>   ?lng.
	?userid <http://example/hasEmail>  '"""+email+"""';
			<http://example/likesArtist>  ?artist.

	?user   <http://example/Votes> ?eventid.



	}GROUP BY ?eventid ?artist ?location ?lat ?lng"""

	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()

	return results['results']['bindings']




'''

def getartistinfo(artistname):
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setQuery("""
	prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    SELECT ?artist ?info 
    WHERE { 
    	{
      ?artist rdf:type dbpedia-owl:Artist.
      ?artist rdfs:label ?name.
      ?artist rdfs:comment ?info.
     	}UNION{
      ?artist rdf:type dbpedia-owl:Band.
      ?artist rdfs:label ?name.
      ?artist rdfs:comment ?info.
     	}
      FILTER(langMatches(lang(?info), "EN")).
      FILTER regex(?name, '"""+artistname+"""')
    }
	""")


	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	try:
		return results['results']['bindings'][0]['info']['value']
	except:
		return "No Info found"

'''