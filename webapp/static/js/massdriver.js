var geoJSON = [];
var latlngs = [];
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

function getDirections(map){
	var fromdest = document.getElementById('startPt').value;
	var todest = document.getElementById('endPt').value;
	calculateAndDisplayRoute(fromdest, todest, directionsService, directionsDisplay);
	geocodePoints(fromdest);
	geocodePoints(todest);
}

function geocodePoints(address) {
	geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        alert("Geocoding successful!")
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
   });

}

function traverse(map){
// This function takes in locations and returns geojson path
	if (isline==1){
		flightPath.setMap(null)
		}
  var pathcoords = [
    {lat: 42.88, lng: -73.5+Math.random()},
    {lat: 41.7, lng: -72},
    {lat: 41.86, lng: -70},
    {lat: 41.55, lng: -71.3}
  ];
  flightPath = new google.maps.Polyline({
    path: pathcoords,
    geodesic: true,
    strokeColor: '#FF0000',
    strokeOpacity: 1.0,
    strokeWeight: 2
  });
	
  flightPath.setMap(map);
	isline=1

};