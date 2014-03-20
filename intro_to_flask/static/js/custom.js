function getartists(){
	// Do a GET request on the '/show' URL, with the data payload 'Hello World'.
	var message = $('#artist').val();
	
		$.get('/artists' , data = {'artist' : message}, function(data){
		result = "";
		var artist;

		artistlist = data['artist-list'];
		result = "";
		for(var i=0; i<artistlist.length;i++){
			text = "<li class='list-group-item'><a onclick = 'getSongsFromLastFm(\"" + data['artist-list'][i]['id'] + "\")'>" + data['artist-list'][i]['name'] + "</a></li>";
			result = result + text;
		}
		$('#artist_list').html(result);
	});
}


function getSongsFromLastFm(id){
	$.get('/songs' , data = {'id' : id}, function(data){
		$('#artist_list').html(data);
	});
}

function changeLocation(){
	var location = $('#location').val();

	$.get('/changeLocation', data = {'location':location}, function(data){
	});
	
	$('#loc').html(location);
}

function UpdateContainer(){

	var loadUrl = "/templates/test.html";
    $("#BodyContent").load(loadUrl); 	    
}

