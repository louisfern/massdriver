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


function initMap() {
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
	var totaltime = 0;	
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
			} else {
      		window.alert('Directions request failed due to ' + status);
			}
		}
	);
}


function directionsWithWaypoints(orig, dest, directionsService, directionsDisplay, waypoints){
	// This function takes in waypoints I create and gets directions with them.
	var totaltime=0;	
	waypointsConverted = convertToWaypoints(waypoints);
	directionsService.route({
   	origin: orig, 
   	destination: dest,
   	travelMode: google.maps.TravelMode.DRIVING,
		waypoints:waypointsConverted
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
	var totaltime = 0;
	route = response.routes[routenumber];
	for (var i = 0; i < route.legs.length; i++) {
		totaltime += route.legs[i].duration.text;
	}
	return totaltime;
}

function convertToWaypoints(points){
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
    if (showLoading) {
        $('#loading').css('visibility', 'visible');
    } else {
        $('#loading').css('visibility', 'hidden');
    };
};

function validDirections(response){
	console.log("Directions succeeded.")
}


function getDirections(map){
	fromdest = document.getElementById('startPt').value;
	todest = document.getElementById('endPt').value;
	calculateAndDisplayRoute(fromdest, todest, directionsService, directionsDisplay);
	geocodePoints(fromdest, 0);
	geocodePoints(todest, 1);
	
}


function makeandplotpath (){
	if (add[0]==true && add[1]==true){
		add[0]=false; 
		add[1]=false;
	$.getJSON("/getdirections",{
		lat1: latlngs[0][1],
		lat2: latlngs[1][1],
		lng1: latlngs[0][0],
		lng2: latlngs[1][0],
		weight: "acc_risk",
		success: validDirections
		}, function(data){ 
			console.log("Path returned.");
			latlngs = generateLatLong(data);
			plotPath(map, latlngs);
			directionsWithWaypoints(fromdest, todest, directionsService, directionsDisplay, latlngs);
		}
	);
	}
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

