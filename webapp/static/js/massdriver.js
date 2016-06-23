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
var startLat
var startLong
var endLat
var endLong
var add1 = false
var add2 = false


function initMap() {
	directionsDisplay = new google.maps.DirectionsRenderer;
  	directionsService = new google.maps.DirectionsService;
  	geocoder = new google.maps.Geocoder();
	var mapDiv = document.getElementById('map');
	map = new google.maps.Map(mapDiv)
	var southWest = new google.maps.LatLng(41.65, -73.5);
	var northEast = new google.maps.LatLng(42.88, -69.95);
	var bounds = new google.maps.LatLngBounds(southWest,northEast);
	map.fitBounds(bounds);
	
	directionsDisplay.setMap(map);

	// calculateAndDisplayRoute('Springfield, MA', 'Boston, MA', directionsService, directionsDisplay);

}

function calculateAndDisplayRoute(orig, dest, directionsService, directionsDisplay) {
  directionsService.route({
    origin: orig, 
    destination: dest,
    travelMode: google.maps.TravelMode.DRIVING
  }, function(response, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      directionsDisplay.setDirections(response);
    } else {
      window.alert('Directions request failed due to ' + status);
    }
  });
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
	var fromdest = document.getElementById('startPt').value;
	var todest = document.getElementById('endPt').value;
	calculateAndDisplayRoute(fromdest, todest, directionsService, directionsDisplay);
	geocodePointsOne(fromdest);
	geocodePointsTwo(todest);
}


function makeandplotpath (){
	if (add1==true && add2==true){
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
			plotPath(map, latlngs)
		}
	);
	}
}

function geocodePointsOne(address) {
	var returnMe = {};
	geocoder.geocode( {'address': address, componentRestrictions:{
		country: 'USA'}}, function(results, status) {
      	if (status == google.maps.GeocoderStatus.OK) {
      		console.log("OK");
				latlngs[0][0]=results[0].geometry.location.lng();
				latlngs[0][1]=results[0].geometry.location.lat();
				add1 = true;
				makeandplotpath()
      	} else {
      		console.log("Geocoding unsuccessful.");
     		}
	   }
   );
}

function geocodePointsTwo(address) {
	var returnMe = {};
	geocoder.geocode( {'address': address, componentRestrictions:{
		country: 'USA'}}, function(results, status) {
      	if (status == google.maps.GeocoderStatus.OK) {
      		console.log("OK");
				latlngs[1][0]=results[0].geometry.location.lng();
				latlngs[1][1]=results[0].geometry.location.lat();
				add2 = true;
				makeandplotpath()
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