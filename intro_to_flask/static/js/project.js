$('#search_artists').on('click',function(e){
	// Do a GET request on the '/show' URL, with the data payload 'Hello World'.
	var message = $('#artist').val();
	$.get('/artists' , data = {'artist' : message}, function(data){
		result = "";
		var artist;

		artistlist = data['artist-list'];
		result = "";
		for(var i=0; i<artistlist.length;i++){
			text = "<p><a onclick = 'getSongsFromLastFm(\"" + data['artist-list'][i]['id'] + "\")'>" + data['artist-list'][i]['name'] + "</a>";
			result = result + text;
		}

		$('#artist_results').html(result);
	});

});


function getSongsFromLastFm(id){
	$.get('/songs' , data = {'id' : id}, function(data){
		$('#artist_results').html(data);
	});
}