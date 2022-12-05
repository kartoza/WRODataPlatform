"use-strict"

ckan.module("wro_spatial",function($){
    return{
        initialize:function(){
            $.proxyAll(this,/_on/); 
            this.el.on('click', this._onClick)
            window.localStorage.setItem('geo_bounds', '');  // avoiding a bug with chrome : https://stackoverflow.com/a/58177957/7765766
            window.addEventListener("storage",this._onStorageChange);
        },
        _onClick:function(e){
            let window_origin = location.origin
            mapWindow =  window.open(`${window_origin}/map/`);
        },
        _onStorageChange:function(e){
            $('#field-spatial').val(window.localStorage.getItem("geo_bounds"));
            mapWindow.close()
        }
    }
    
})

// ckan.module('geo_data_preview', function($){
//     return{
//         initialize:function(){
//             $.proxyAll(this,/_on/);
//             let map_div_holder = document.getElementById("map")
//             map_div_holder.style.width="100%"; map_div_holder.style.height="600px";
//             let spatial_data = this.options.spatial_data
//             var geojson_layer
//             // the marker option
//             var markerOptions = {
//                 radius: 4,
//                 fillColor: 'brown',//'#0099FF',
//                 color: "#fff",
//                 weight: 3,
//                 opacity: 0.8,
//                 fillOpacity: 0.8
//             };

//             spatial_data.forEach((element, idx) => {
//                 let element_coords = element.coordinates
//                 if(idx == 0){
//                     var map = L.map('map').setView(element_coords, 5);
//                     L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
//                    //var geo_tiff_layer = L.leafletGeotiff('https://storage.cloud.google.com/wrc_wro_rasters/NASA_POWER_climatology/profile_soil_moisture_annual.tif?authuser=0').addTo(map);
//                     // let geo_tiff_bounds = [[-35.0048, 17.5299,],[-21.500010, 34.000014]]

//                     // L.imageOverlay("http://localhost/nasa_test.png", geo_tiff_bounds, {
//                     //     opacity: 0.8,
//                     //     interactive: true
//                     // }).addTo(map);
//                     //GeoTIFF.fromUrl("http://localhost/test.tif").then(tiff => { console.log(tiff)});
//                     // (async function() {
//                     //     const tiff = await GeoTIFF.fromUrl('http://localhost/test.tif/');
//                     //     const image = await tiff.getImage();
//                     //     console.log(image)
//                     //   })()
//                     let _this = this
//                     geojson_layer = L.geoJson(null,{
//                         pointToLayer: function (feature, latlng) {
//                             return L.circleMarker(latlng, markerOptions);
//                         },
//                         onEachFeature:function(feature, layer){
//                             layer.bindPopup(_this.markupGeojson(feature.properties))
//                         }
//                     }).addTo(map);
//                 }
//                 let props = element["properties"]
//                 let adjusted_coords = [element_coords[1], element_coords[0]]
                
//                 let feat = {
//                     "type": "Feature",
//                     "properties": props,
//                     "geometry": {
//                         "type": "Point",
//                         "coordinates": adjusted_coords
//                     }
//                 }
//                 geojson_layer.addData(feat)
//             });      
                
//         },
//         markupGeojson:function(props){
//             // adding properties popups
//             let markup = `
//             <table class="table table-striped">
//                 <thead class="thead-dark">
//                     <tr>
//                         <th scope="col">Property</th>
//                         <th scope="col">Value</th>
//                     </tr>
//                 </thead>
//                 <tbody>
//         `
//     for (const prop in props){
//         markup+= `<tr>
//                   <td>${prop}</td>
//                   <td>${props[prop]}</td>
//                   </tr>  
//                     `                            }
        
//         markup+= `
//                 </tbody>
//                 </table>
//                 `
//         return markup
//         }
//     }
// })


ckan.module('geo_data_preview', function($){
    return {
        initialize:function(){

            if (!maplibregl.supported()) {
                alert('Your browser does not support MapLibre GL');
                }
                let spatial_data = this.options.spatial_data
                console.log(spatial_data)
                var map = new maplibregl.Map({
                container: 'map',
                style: 'https://api.maptiler.com/maps/streets/style.json?key=8aPiHLLmhOYnR05s747T', // stylesheet location
                center: [16.25, -27.75], // starting position [lng, lat]
                zoom: 3, // starting zoom
                fadeDuration: 800,
                });
        
            map.addControl(new maplibregl.NavigationControl(),'top-left')
        
            var scale = new maplibregl.ScaleControl({
                maxWidth: 80,
                unit: 'metric'
                });
                map.addControl(scale,'bottom-left')
        
            map.on("load", ()=>{
                map.addSource("bigquery-values", {
                    "type":"geojson",
                    "data": spatial_data
                })
        
                map.addLayer({
                    "id":"bigquery-heat-layer",
                    "type":"heatmap",
                    "source":"bigquery-values",
                    'paint': {
                        // Increase the heatmap weight based on frequency and property magnitude
                        'heatmap-weight': [
                        'interpolate',
                        ['linear'],
                        ['get', 'Clear_sky_surface_PAR_total_Annual'],100,0,130,1],
                        // Increase the heatmap color weight weight by zoom level
                        // heatmap-intensity is a multiplier on top of heatmap-weight
                        'heatmap-intensity': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],0,0,9,8],
                        // Color ramp for heatmap.  Domain is 0 (low) to 1 (high).
                        // Begin color ramp at 0-stop with a 0-transparancy color
                        // to create a blur-like effect.
                        'heatmap-color': [
                        'interpolate',
                        ['linear'],
                        ['heatmap-density'],
                        0, 'rgba(33,102,172,0)',
                        0.2, 'rgb(103,169,207)',
                        0.4, 'rgb(209,229,240)',
                        0.6, 'rgb(253,219,199)',
                        0.8, 'rgb(239,138,98)',
                        1, 'rgb(178,24,43)'
                        ],
                        // Adjust the heatmap radius by zoom level
                        'heatmap-radius': [
                        'interpolate',
                        ['linear'],
                    ['zoom'],0,2,9,20],
                        // Transition from heatmap to circle layer by zoom level
                        'heatmap-opacity': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],7,1,9,0]
                        }
                })
        
                map.addLayer(
                    {
                    'id': 'bigquery-points',
                    'type': 'circle',
                    'source': 'bigquery-values',
                    'minzoom': 7,
                    'paint': {
                    'circle-radius': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    7, ['interpolate', ['linear'], ['get', 'Clear_sky_surface_PAR_total_Annual'], 100, 1, 130, 4],
                    16,['interpolate', ['linear'], ['get', 'mag'], 100, 5, 130, 50]
                    ],
                    // Color circle by earthquake magnitude
                    'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['get', 'Clear_sky_surface_PAR_total_Annual'],
                    1, 'rgba(33,102,172,0)',
                    2, 'rgb(103,169,207)',
                    3, 'rgb(209,229,240)',
                    4, 'rgb(253,219,199)',
                    5, 'rgb(239,138,98)',
                    6, 'rgb(178,24,43)'
                    ],
                    'circle-stroke-color': 'white',
                    'circle-stroke-width': 1,
                    // Transition from heatmap to circle layer by zoom level
                    'circle-opacity': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],7,0,8,1]
                    }
                    },
                    );
        
            })



        },
    }
})

    