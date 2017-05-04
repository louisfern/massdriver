var geoJSON = [];
var latlngs = [[-1, -1], [-1, -1]];
var bounds = [[42.34, -71.113], [42.44, -71.09]];
var LineStringOpt = {color : 'green', opacity : 0.5, weight : 8};
var paths = [];
var markers = [];
var accessToken = '';
var message = '';
var map
var flightPath
var isline = 0
var directionsDisplay
var directionsService
var geocoder
var add = [false, false]
var fromdest
var todest
var weight


function initMap() {
	// Sets up the map
	directionsDisplay = new google.maps.DirectionsRenderer;
  	directionsService = new google.maps.DirectionsService;
  	geocoder = new google.maps.Geocoder();
	var mapDiv = document.getElementById('map');
	map = new google.maps.Map(mapDiv)
	var southWest = new google.maps.LatLng(41.65, -73.5);
	var northEast = new google.maps.LatLng(42.68, -69.95);
	var bounds = new google.maps.LatLngBounds(southWest,northEast);
	map.fitBounds(bounds);
	
	directionsDisplay.setMap(map);
}

function calculateAndDisplayRoute(orig, dest, directionsService, directionsDisplay) {
	// Uses Google API to find directions and route, and then displays them
	var totaltime = 0;	
	var weight2 = 0;
	directionsService.route({
		origin: orig, 
		destination: dest,
		travelMode: google.maps.TravelMode.DRIVING
  		}, 
  		function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				directionsDisplay.setDirections(response);
				totaltime = calcTotalTime(response, 0);
				var fieldNameElement = document.getElementById("googleTime");
				fieldNameElement.textContent = "Google driving time: " + totaltime;
				var lnglats = googleWaypointsToArray(response);
				weight2 = getWeight(lnglats, false);
				var fieldNameElement = document.getElementById("googleRate");
				fieldNameElement.textContent = "Total risk: " + weight2;
			} else {
      		window.alert('Directions request failed due to ' + status);
			}
		}
	);
}

function googleWaypointsToArray(dirResponse){
// This function takes in a response to Google's directions API and returns a lng, lat array.
	var points = dirResponse.routes[0].overview_path;
	var newpoints = [];
	for (var i = 0; i<points.length; i++){
		newpoints.push([points[i].lng(), points[i].lat()]);
	}
	return newpoints;
}


function directionsWithWaypoints(orig, dest, directionsService, directionsDisplay, waypoints){
	// This function takes in waypoints I create and gets directions with them. This is used to 
	// calculate transit time.
	var totaltime=0;	
	var weight = 0;
	waypointsConverted = convertToWaypoints(waypoints);
	directionsService.route({
   	origin: orig, 
   	destination: dest,
   	travelMode: google.maps.TravelMode.DRIVING,
		waypoints:waypointsConverted,
		optimizeWaypoints: true
		}, 
		function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
      		totaltime = calcTotalTime(response, 0);
				var fieldNameElement = document.getElementById("myTime");
				fieldNameElement.textContent = "Lowest accident rate time: " + totaltime;
      	} else {
      		window.alert('Directions request failed due to ' + status);
    		}
  		}
  	);
}

function calcTotalTime(response, routenumber){
	// This sums up the time on a route.
	var totaltime = 0;
	route = response.routes[routenumber];
	for (var i = 0; i < route.legs.length; i++) {
		totaltime += route.legs[i].duration.text;
	}
	return totaltime;
}

function convertToWaypoints(points){
	// This converts between a points array and Google's lat/lng.
	var newpoints = [];
	var shortpoints = [];
	for (var i=0; i<points.length; i++) {
		newpoints.push({
			location: new google.maps.LatLng(points[i].lat, points[i].lng),
			stopover: false
		});
	}
	maxpoints = 8;
	skip = Math.floor(newpoints.length/maxpoints);
	for (var i=0; i<maxpoints; i+=1){
		shortpoints.push(newpoints[i*skip]);
	}	
	
	return shortpoints;
}


function ShowLoading(showLoading) {
	// Loading screen, not in use
    if (showLoading) {
        $('#loading').css('visibility', 'visible');
    } else {
        $('#loading').css('visibility', 'hidden');
    };
};

function validDirections(response){
	console.log("Directions succeeded.")
}

function validWeights(response){
	console.log('weights successfully reported.')
}


function getDirections(map){
	// This does the Google directions elements, then geocodes the start and finish
	// so that my code can use them. This launches makeandplotpath
	fromdest = document.getElementById('startPt').value;
	todest = document.getElementById('endPt').value;
	calculateAndDisplayRoute(fromdest, todest, directionsService, directionsDisplay);
	geocodePoints(fromdest, 0);
	geocodePoints(todest, 1);
	
}

function makeandplotpath (){
	// This uses my algorithm to get directions between two previously geocoded points. 
	var coords = [];
	var weight = 0;
	if (add[0]==true && add[1]==true){
		add[0]=false; 
		add[1]=false;
	$.getJSON("/getdirections",{
		lat1: latlngs[0][1],
		lat2: latlngs[1][1],
		lng1: latlngs[0][0],
		lng2: latlngs[1][0],
		weight: "assignedle",
		success: validDirections
		}, function(data){ 
			console.log("Path returned.");
			latlngs = generateLatLong(data);
			plotPath(map, latlngs);
			directionsWithWaypoints(fromdest, todest, directionsService, directionsDisplay, latlngs);
			coords = latlngToArray(latlngs);
			weight = getWeight(coords, true);
			var fieldNameElement = document.getElementById("myRate");
			fieldNameElement.textContent = "Total risk: " + weight;
		}
	);
	}
}



function getWeight(coords, onPath){
	if (onPath==true){
	$.getJSON("/getWeightOnPath",{
		wordlist:JSON.stringify(coords)
		}, function(data){ 
			console.log("On-path weights returned.");
			console.log(data.result);
			weight = data.result;
			}
		);
	} else{
		$.getJSON("/getWeightOffPath",{
		wordlist:JSON.stringify(coords)
		}, function(data){ 
			console.log("Off-path weights returned.");
			console.log(data.results);			
			weight = data.result;
		}
		);
	};
	return weight;
}

function latlngToArray(latlng){
	var arr = [];
	for (var i = 0; i<latlng.length; i++){
		arr.push([latlng[i].lng,latlng[i].lat]);
	}
	return arr;
}


function geocodePoints(address, locnum) {
	var returnMe = {};
	var re = new RegExp(', MA'); // This is to ensure locations are in MA
	geocoder.geocode( {
		'address': address, 
		componentRestrictions:{
			country: 'US'
			}
		}, 
		function(results, status) {
      	if (status == google.maps.GeocoderStatus.OK) {
				if (re.exec(results[0].formatted_address) != null ) {     		
      		console.log("Found location OK.");
				latlngs[locnum][0]=results[0].geometry.location.lng();
				latlngs[locnum][1]=results[0].geometry.location.lat();
				add[locnum] = true;
				makeandplotpath()
				} else{
					console.log("Geocoded response not in MA.");
					window.alert('Geocoded response not in MA.');	
				} 
      	} else {
      		console.log("Geocoding unsuccessful.");
     		}
	   }
   );
}

function generateLatLong(arr){
	var paths = [];
	for (i = 0; i < arr.length; i++) {  
		paths.push({lat:arr[i][1], lng:arr[i][0]})
   }
return paths;
}

function plotPath(map, inpath){
// This function takes in a path and plots it on the given map
	if (isline==1){
		flightPath.setMap(null);
	}
	flightPath = new google.maps.Polyline({
		path: inpath,
		geodesic: true,
		strokeColor: '#FF0000',
		strokeOpacity: 0.9,
		strokeWeight: 4}
	);
	
	flightPath.setMap(map);
	isline = 1;

}