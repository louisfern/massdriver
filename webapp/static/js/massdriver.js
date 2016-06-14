var geoJSON = [];
var latlngs = [];
var bounds = [[42.34, -71.113], [42.44, -71.09]];
var LineStringOpt = {color : 'green', opacity : 0.5, weight : 8};
var paths = [];
var markers = [];
var accessToken = '';
var message = '';

function Load() {
    // Initialize MapBox map<script>
    L.mapbox.accessToken = accessToken;
    map = L.mapbox.map('map', '').setView([42.373, -71.103], 13);
};


function ShowLoading(showLoading) {
    if (showLoading) {
        $('#loading').css('visibility', 'visible');
    } else {
        $('#loading').css('visibility', 'hidden');
    };
};


// The Following Section Finds Your Route
function FindAndRoute(startPt, endPt, runDis){
   ShowLoading(true);
   message = '';
   $('#addmessage').html(message);
   $.getJSON('/findRoute', {'s': startPt,'e': endPt,'d':runDis}, function(findJSON){
          // Maybe reset on bad query
          ShowLoading(false);
          //console.log(findJSON);
          //console.log(jQuery.isEmptyObject(findJSON));
          if (!jQuery.isEmptyObject(findJSON)) {
          //if (findJSON!={}) {
             console.log('Path Found');
             message = findJSON['message'];
             $('#addmessage').html(message);

             // Add geoMarkers to feature llayer
             geoJSON.push(findJSON['path']);
             map.featureLayer.setGeoJSON(geoJSON);

             //Pan and zoom
             map.fitBounds(findJSON['bounds']);
          }else{
             //console.log('Path NOT Found');
             message = 'Path not found! Please check your address, and make sure they are within the blue boundary of Cambridge and Boston.';
             //console.log(message);
             $('#addmessage').html(message);
          }
   });
};

function PathSearch() {
    // Grab address box valuePathTestMashUp
    var startPt = $('#startPt').val();
    console.log('Inside PathSearch');
    console.log(startPt);
    var endPt = $('#endPt').val();
    console.log(endPt);
    var runDis = $('#runDist').val();
    console.log(runDis);
    // Reset map ...
    ResetMap();
    // If it is not empty ...
    if (endPt == 'default = start') {
        // ... and find and route
        document.getElementById("endPt").value=document.getElementById("startPt").value;
        FindAndRoute(startPt, startPt, runDis);//FIXME: no runLoop fun implemented yet
    }else{
        console.log('prepare to run find and route');
        FindAndRoute(startPt, endPt, runDis);
    }

};


function traverse(){
// This function takes in locations and returns geojson path
    var path = [[-73.5, 42.88],
			   [-72.0, 41.70],
			   [-70.0, 41.86],
			   [-71.3, 41.55]]
    map.addSource("route", {
		"type": "geojson",
		"data": {
				"type": "Feature",
				"properties": {},
				"geometry": {
					"type": "LineString",
					"coordinates": path
				}
		}
	});
	map.addLayer({
		"id": "route",
		"type": "line",
		"source": "route",
		"layout": {
				"line-join": "round",
				"line-cap": "round"
		},
		"paint": {
				"line-color": "#888",
				"line-width": 8
		}
	});

};