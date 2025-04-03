import json
import logging
from ckan.plugins import toolkit
import ckan.lib.dictization as ckan_dictization
# def convert_raw_input_to_geojson(input_text:str)->dict:
#     return json.dumps({ "type": "Point", "coordinates": [16, 32]})

logger = logging.getLogger(__name__)

def convert_raw_input_to_geojson(input_text:str, context:dict)->dict:
    """
        the user should input
        a text of comma-seprated values, we need to convert
        that to geojson so ckanext-spatial could handle it.

        args
        ----
        input_text - str: a comma seperated values of either a point
        or bounding box, input from ckanext-scheming form

        returns
        -------
        dict: the goejson constructed from the input text values. 
    """
    geojson = None
    #try:
    if input_text == "": # empty input, set default bounding to south africa
        input_text = "-22.1265, 16.4699, -34.8212, 32.8931"  
    logger.debug("======, 'inside convert_raw_input_to_geojson', input_text", input_text)
    
    # the converter is called mutiple times during dataset creation, this if statement 
    # is used to handle an error when the value is missing with the call to this converter
    # after resrouce upload form sumitted.
    if input_text == toolkit.missing:
        package_id = context["package"].id
        package = toolkit.get_action("package_show")(context,{"id":package_id})
        extra_spatial = _get_extra_spatial_value(package)
        if extra_spatial:
            return _convert_str_to_geojson(extra_spatial)
        else:
            default_geojson = {"type": "Polygon", "coordinates": [[[16.4699, -22.1265], [32.8931, -22.1265], [32.8931, -34.8212], [16.4699, -34.8212], [16.4699, -22.1265]]]}
            return json.dumps(default_geojson)
    
    return _convert_str_to_geojson(input_text)


def _convert_str_to_geojson(input_text:str):
    """
    takes an input str as 
    "-22.1265, 16.4699, -34.8212, 32.8931"  
    and converts it to geojson bounding box
    """
    try:
        values = input_text.split(",")
    
        if len(values)==2: # a point
            geojson = { "type": "Point", "coordinates": [float(values[1]), float(values[0])]}
            return json.dumps(geojson)
        elif len(values)==4:
            """ goejson has the coords as long, lat and exterior ring going coutner clockwise
                while holes are clock wise(right hand role). 
                see the spect https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1
                see https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6
            """
            values = [float(i) for i in values]
            c1 = [values[1],values[0]]
            c2 = [values[3],values[0]]
            c3 = [values[3],values[2]]
            c4 = [values[1],values[2]] 
            
            geojson = {"type": "Polygon", "coordinates": [[ c1, c2, c3, c4, c1 ]]}
            return json.dumps(geojson)
        else:
            coords = values[1:]
            coords = ",".join(coords)
            values = values[0] + "," + coords
            values = eval(values)

    except:
        raise toolkit.Invalid(f"your input is \"{input_text}\" \n \
            Geographic location should be either a point or \
            a bounding box, e.g. -22.1265, 16.4699, -34.8212, 32.8931 \
            please check your input")

def convert_empty_resource_info_to_false(info_value):
    """
    when creating resources,
    the supplementa_bigquery
    will have empty value if
    not checked, this doesn't
    appear to be false in the
    form view
    """
    if info_value=="" or info_value == False:
        return "False"
    
def _get_extra_spatial_value(data_dict:dict)->str:
    """
    spatial field sometimes 
    don't appear in the 
    data dict, we added
    a key,value pair
    named extra_spatial
    to preserve the value
    """
    extras = data_dict.get("extras")
    for item in extras:
        if item.get("key") == "extra_spatial":
            return item.get("value")