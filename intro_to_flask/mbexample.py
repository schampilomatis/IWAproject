import pylast
def songs(id):
 
  

  API_KEY = '4bea9a7cfe15b09d2ada827592605ee0'
  API_SECRET = '13b346b26064a3537796608d27802711'

  username = "nicksar11"
  password_hash = pylast.md5("cavcle501")
  network = pylast.LastFMNetwork(api_key=API_KEY,api_secret=API_SECRET,username=username,password_hash=password_hash)

  fetchedArtist = network.get_artist_by_mbid(id)
  tracks = fetchedArtist.get_top_tracks()

  result = ""
  for track in tracks:
    result = result + "<p>" +track[0].get_name()+"</p>"

  return result

