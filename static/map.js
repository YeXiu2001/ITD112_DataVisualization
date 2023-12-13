//declare layers
var standard = L.tileLayer.provider('OpenStreetMap.Mapnik');
var sat = L.tileLayer.provider('Esri.WorldImagery');

const myGeoapify = "29e03bd651df4e70b56db34c0ebd5253";

//basemaps
var basemaps = {
    'Standard Map': standard,
    'Satellite Image': sat,
}

//Main map
var map = L.map('map', {
    center:[13.325485, 121.26709], //lat, long
    zoom: 5,
    layers: [standard]
});

// Fetch actual data from Flask route
fetch('/get_heatmap_data')
    .then(response => response.json())
    .then(data => {
        // Calculate normalized intensity based on "cases"
        var maxCases = 3382;
        var minCases = 0;
        var averageCases = 35;

        var normalizedData = data.map(point => {
            var normalizedIntensity = (point[2] - minCases) / (maxCases - minCases);
            // You can further adjust the intensity as needed
            var scaledIntensity = normalizedIntensity * 0.5; // Scale between 0 and 0.5, for example

            return [point[0], point[1], scaledIntensity];
        });

        // Create Heatmap layer using actual data
        var heatmapLayer = L.heatLayer(normalizedData, {
            radius: 40,
            minOpacity: 0.6,
            gradient: {0.1: 'blue', 0.2: 'lime', 0.3: 'red'}
        });

        //declare overlays
        //initialize overlays
        var overlays = {
             'Heatmap': heatmapLayer
        }

        //map layers/ control layer of basemaps and overlays
        var maplayers = L.control.layers(basemaps, overlays).addTo(map);

        // Add the heatmap layer to the map by default
        map.addLayer(heatmapLayer);

        //search Control plugin https://github.com/perliedman/leaflet-control-geocoder
        L.Control.geocoder().addTo(map);
        //leaflet-locate plugin https://github.com/domoritz/leaflet-locatecontrol
        L.control.locate().addTo(map);
    })
    .catch(error => console.error('Error fetching heatmap data:', error));
