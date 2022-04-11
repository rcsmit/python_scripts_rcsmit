<?php

    // shows friends on map. Uses https://github.com/jawj/OverlappingMarkerSpiderfier
    
    // Simple password protection
    if (!isset($_COOKIE['password']) || $_COOKIE['password'] !== 'MYPASS') {
        header('Location: login.php');
        exit;
    }
?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset=" ISO-8859-1">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>X</title>

    <link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800&subset=latin,cyrillic-ext' rel='stylesheet' type='text/css'>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    
    <style type="text/css">
            #map {
                width:  100%;
                height: 700px;
            }
        </style>
        <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=__APIKEY___"></script>
        
<script src="https://cdnjs.cloudflare.com/ajax/libs/OverlappingMarkerSpiderfier/1.0.3/oms.min.js"></script>

<?php

$servername = 'SERVER.net';
$username = 'USER';
$password = 'PASSWORD';
$database = 'DATABASE';

$mysqli = new mysqli($servername, $username, $password, $database);


/* check connection */
if ($mysqli->connect_errno) {
    printf("Connect failed: %s\n", $mysqli->connect_error);
    exit();
}

$query = "SELECT * FROM facebookfriends";

$points = array();
$result = $mysqli->query($query);

if(!$result){
     die('There was an error running the query [' . $con->error . ']');
} else {
    while ($row = mysqli_fetch_assoc($result))
	    $points[] = array('lat' => $row['latitude'], 'lng' => $row['longitude'], 'name' => $row['name'], 'place' => $row['place'], 'facebook_id' => $row['facebook_id']);
    }
}

?>


<script type="text/javascript">
     var points = <?php echo json_encode($points) ; ?>;
     $(document).ready(function(){
        google.maps.event.addDomListener(window, 'load', init);

             function init() {
				 
				     // https://github.com/jawj/OverlappingMarkerSpiderfier
				 
                 var mapOptions = {                                    
                     zoom: 6,
                     center: new google.maps.LatLng(51.9851034,5.8987296,16),
                     styles: [  {featureType:"administrative",elementType:"all",stylers:[{visibility:"on"},{saturation:-100},{lightness:20}]},  {featureType:"road",elementType:"all",stylers:[{visibility:"on"},{saturation:-100},{lightness:40}]},    {featureType:"water",elementType:"all",stylers:[{visibility:"on"},{saturation:-10},{lightness:30}]},    {featureType:"landscape.man_made",elementType:"all",stylers:[{visibility:"simplified"},{saturation:-60},{lightness:10}]},   {featureType:"landscape.natural",elementType:"all",stylers:[{visibility:"simplified"},{saturation:-60},{lightness:60}]},    {featureType:"poi",elementType:"all",stylers:[{visibility:"off"},{saturation:-100},{lightness:60}]},    {featureType:"transit",elementType:"all",stylers:[{visibility:"off"},{saturation:-100},{lightness:60}]}]
                 };
                 var mapElement = document.getElementById('map');
                 var map = new google.maps.Map(mapElement, mapOptions);

				 var iw = new google.maps.InfoWindow();
				 
					var oms = new OverlappingMarkerSpiderfier(map, {
					  markersWontMove: true,
					  markersWontHide: true,
					});
				  
				     oms.addListener('format', function(marker, status) {
			var iconURL = 	status == OverlappingMarkerSpiderfier.markerStatus.SPIDERFIED ? 'marker-highlight.svg' :
							status == OverlappingMarkerSpiderfier.markerStatus.SPIDERFIABLE ? 'marker-plus.svg' :
							status == OverlappingMarkerSpiderfier.markerStatus.UNSPIDERFIABLE ? 'marker.svg' : 
					null;
        var iconSize = new google.maps.Size(12, 16);
        marker.setIcon({
          url: iconURL,
          size: iconSize,
          scaledSize: iconSize  // makes SVG icons work in IE
        });
      });
			 	  
				 
                  for (var i=0,l=points.length;i<l;i++) {
                      var latLng = new google.maps.LatLng(points[i].lat, points[i].lng); 
							(function() {  // make a closure over the marker and marker data
								var naamxx = points[i].name ;
								var plaats = points[i].place ;
								//console.log (naamxx)
								var naamx = naamxx.replace(/ /g,"_");
								 var foto  = "img/" + naamx + ".jpg";
								//foto = "test.jpg";
								var link = "https://www.facebook.com/profile.php?id=" + points[i].facebook_id;
								var naam  = points[i].name;  
								var markerData = "<img src='" +foto + "'><br><a href='" + link + "' target='_blank'>" + naam + "<br><i>" + plaats+ "</i></a>";
								
								var marker = new google.maps.Marker({ position: latLng,
									//icon: {
									//	path: google.maps.SymbolPath.CIRCLE,
					 				//	scale: 3,
									//	fillColor: "#f00",
									//	strokeColor: "#000",
									//	fillOpacity: 0.8,
									//	strokeWeight: 0.8
									//},
									title:points[i].name

								});  
															// markerData works here as a LatLngLiteral
								google.maps.event.addListener(marker, 'spider_click', function(e) {  // 'spider_click', not plain 'click'
									iw.setContent(markerData);
									iw.open(map, marker);
							});
							
							oms.addMarker(marker);  // adds the marker to the spiderfier _and_ the map
						  })();
						}
				 
				 
				 
				} // /init
             }  // /doc ready function               
      );


</script>

</head>


 <body>
    <div class="container-fluid">
      <div id="map"></div>
    </div>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    
  </body>
</html>
