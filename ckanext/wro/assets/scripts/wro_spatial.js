"use-strict"

ckan.module("wro_spatial",function($){
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            this.el.on('click', this._onClick)
            window.localStorage.setItem('geo_bounds', '');  // avoiding a bug with chrome : https://stackoverflow.com/a/58177957/7765766
            // preload dataset extent if available
            if (this.options.dataset_extent) {
                window.localStorage.setItem('geo_bounds', JSON.stringify(this.options.dataset_extent));
            }

            window.addEventListener("storage",this._onStorageChange);
        },
        _onClick:function(e){
            let window_origin = location.origin
            console.log("is this clicked?")
            mapWindow =  window.open(`${window_origin}/map/`);
        },
        _onStorageChange:function(e){
            $('#field-spatial').val(window.localStorage.getItem("geo_bounds"));
            mapWindow.close()
        }
    }
    
})

ckan.module('geo_data_preview', function($){
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            let map_div_holder = document.getElementById("map")
            map_div_holder.style.width="100%"; map_div_holder.style.height="600px";
            let spatial_data = this.options.spatial_data
            var geojson_layer
            // the marker option
            var markerOptions = {
                radius: 4,
                fillColor: 'brown',//'#0099FF',
                color: "#fff",
                weight: 3,
                opacity: 0.8,
                fillOpacity: 0.8
            };

            spatial_data.forEach((element, idx) => {
                let element_coords = element.coordinates
                if(idx == 0){
                    var map = L.map('map').setView(element_coords, 5);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                    let _this = this
                    geojson_layer = L.geoJson(null,{
                        pointToLayer: function (feature, latlng) {
                            return L.circleMarker(latlng, markerOptions);
                        },
                        onEachFeature:function(feature, layer){
                            layer.bindPopup(_this.markupGeojson(feature.properties))
                        }
                    }).addTo(map);
                }
                let props = element["properties"]
                let adjusted_coords = [element_coords[1], element_coords[0]]
                
                let feat = {
                    "type": "Feature",
                    "properties": props,
                    "geometry": {
                        "type": "Point",
                        "coordinates": adjusted_coords
                    }
                }
                geojson_layer.addData(feat)
            });      
                
        },
        markupGeojson:function(props){
            // adding properties popups
            let markup = `
            <table class="table table-striped">
                <thead class="thead-dark">
                    <tr>
                        <th scope="col">Property</th>
                        <th scope="col">Value</th>
                    </tr>
                </thead>
                <tbody>
        `
    for (const prop in props){
        markup+= `<tr>
                  <td>${prop}</td>
                  <td>${props[prop]}</td>
                  </tr>  
                    `                            }
        
        markup+= `
                </tbody>
                </table>
                `
        return markup
        }
    }
});

    