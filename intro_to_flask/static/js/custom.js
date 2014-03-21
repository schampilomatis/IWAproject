var player;

 function getartists(){
	// Do a GET request on the '/show' URL, with the data payload 'Hello World'.
	var message = $('#artist').val();
	$.get('/artists' , data = {'artist' : message}, function(data){
		result = "";
		var artist;

		artistlist = data['artist-list'];
		result = "";
		for(var i=0; i<artistlist.length;i++){
			text = "<p><a class='closedropdown' onclick = 'getSongsFromLastFm(\"" + data['artist-list'][i]['id'] + "\",\"" + data['artist-list'][i]['name'] + "\")'>" + data['artist-list'][i]['name'] + "</a></p>";
			result = result + text;
		}

		$('#artist-list').html(result);
		

	});

}


function likeArtist(id){
	$.get('/like' , data = {'id' : id, 'likeType' : 'Artist'})
}


function likeSong(id){
	$.get('/like' , data = {'id' : id, 'likeType' : 'Song'})
}


function getSongsFromLastFm(id , name){
	document.getElementById("artist").value =name;
	artistid = id;
	$.get('/songs' , data = {'id' : artistid}, function(data){
		$('#song-list').html(data);
	});

}

function onYouTubeIframeAPIReady() {
	player = new YT.Player('player', {
      	height: '300',
        width: '500',

    });
}

function getvideo(name){
	$.ajax({
    url: "http://gdata.youtube.com/feeds/api/videos?q=" + escape(name) + "&alt=json&max-results=1&format=5",
    dataType: "jsonp",
    success: function (data) {
    		var id = data.feed.entry[0].id.$t.split('/').reverse()[0];
    		player.loadVideoById(id, 0, "small")
    	}
	});
}

function UpdateContainer(){

	var loadUrl = 'test';
    $("#BodyContent").load(loadUrl); 	    
}


function UpdateContainer2(){

	var loadUrl = 'browseArtists';
    $("#BodyContent").load(loadUrl); 	    
}

	
function initialize(){
	var lat, lng;
	$.get('/getLatLng' , function(data){
 			lat = JSON.parse(data)["lat"];
 			lng = JSON.parse(data)["lng"];
 			mapinitialize(lat,lng);
	});
	
}


function mapinitialize(lat,lng) {
	var mapOptions = {
		center: new google.maps.LatLng(lat, lng),
        zoom: 3
        };
        map = new google.maps.Map(document.getElementById('map-canvas'),
        	mapOptions);
}



      
function setAllMap(map) {
	for (var i = 0; i < markers.length; i++) {
   		markers[i].setMap(map);
    }
}
     // Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
  	setAllMap(null);
} 
      
function deleteMarkers() {
  	clearMarkers();
 	markers = [];
}

function addInfoWindow(marker, message) {
	var info = message;
	google.maps.event.addListener(marker, 'mouseover', function () {
    if (infoWindow){
    	infoWindow.close();
    }
                infoWindow = new google.maps.InfoWindow({
                content: message
            	});
                infoWindow.open(map, marker);
            });
        }

function addElement(element,ul,type){
			var li = $('<li></li>');
			li.addClass('list-group-item');
			var a = $('<a></a>');
			a.html(element);

			if(element!="no events found..."){
				if (type=="artist"){
					li.append("<button style='float: right;'  class='btn btn-primary' onclick='submitted(\""+element+"\")'>Show!</button>");
					}
				else if (type=="event"){
					li.append("<button style='float: right;'  class='btn btn-primary'>Show</button>");
					}
				}
			li.append(a);
			ul.append(li);
}


function addMarker(latitude,longitude,i,color){
				var marker = new google.maps.Marker({
        		position: new google.maps.LatLng (latitude, longitude),
        		map: map,
        		title: 'test',
    			});
    			switch(color)
				{
				case "green":
    			marker.setIcon('/static/img/green-dot.png');
    			break;
    			case "red":
    			marker.setIcon('/static/img/red-dot.png');
    			break;
    			}	

    		return marker;
}

function fetchArtist() {
	var artist = $('#artist').val();

	$.get('/artists', data = {'artist':artist} , function(data){
		var artistlist = data['artist-list'];
		var ul = $('<ul></ul>');
		ul.addClass('list-group');

		for (var i =0 ; i<artistlist.length;i++){
			addElement(data['artist-list'][i]['name'],ul,"artist");
			
		}
		$('#artist_suggestion').html(ul);
	}
		)
}


function submitted(artist){

	var lld_eventful_url = 'http://api.eventful.com/json/events/search?app_key=gKwVVMz88t773B4Q&keywords='+artist+'&date=Future&callback=?';
	var lld_lastf_url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&artist='+artist+'&api_key=4bea9a7cfe15b09d2ada827592605ee0&format=json';
	var data = {'q': artist , 'limit': 100}
	var ul = $('<ul></ul>');
		ul.addClass('list-group');
	deleteMarkers();
	$.getJSON(lld_eventful_url, data=data, function(json){
		
	if (json.total_items == "0"){
			addElement("no eventful events found...",ul);
		}  else {

		for (var i in json.events.event) {
			var r = json.events.event[i];
			
			var message =  'title: '+ r.title + '\n' + 'start time: ' + r.start_time + '\n' + 'city: ' + r.city_name ;


			marker = addMarker (r.latitude, r.longitude,i,"green");
			addInfoWindow(marker, message);
    		markers.push(marker);
    		bounds.extend(markers[i].position);
			addElement(r.city_name,ul,"event");
			
		}
	}
		
});


$.getJSON(lld_lastf_url, data=data, function(json){
		
		
		if (!json.events.hasOwnProperty('event')){
			addElement("no lastfm events found...",ul);
		}  else {

		for (var i in json.events.event) {
			var r = json.events.event[i];
			
			var message = 'title: '+ r.title + '\n' + 'start time: ' + r.startDate + '\n' + 'city: ' + r.venue.location.city ;
			console.log(message);
			evLat = r['venue']['location']['geo:point']['geo:lat'];
			evLong = r['venue']['location']['geo:point']['geo:long'];
			

			marker = addMarker (evLat,evLong,i,"red");
			addInfoWindow(marker, message);
    		markers.push(marker);
    		bounds.extend(markers[i].position);
			addElement(r.venue.location.city,ul,"event");
			
		}
	}
		
		
	});
	map.fitBounds(bounds);
	$('#artist_suggestion').html(ul);

}

function changeLocation(){
	var location = $('#location').val();
	var lat = $('#lat').val();
	var lng = $('#lng').val();
	console.log(lat);
	$.get('/changeLocation', data = {'location':location, 'lat':lat , 'lng':lng}, function(data){
	});
	initialize();
	$('#loc').html(location);

}