import sys
from google.cloud import storage
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import zipfile
import logging
import io
import geopandas
import pandas as pd
import json
import os
import time
from datetime import datetime

import apache_beam as beam

import requests
from requests import get, post
from requests.exceptions import Timeout


class Default:
    # Projects
    #PROJECT_ID = 'wrc-wro'
    PROJECT_ID = 'thermal-glazing-350010'  # FOR TESTING

    # Buckets
    BUCKET_TRIGGER = 'wro-trigger-test'
    BUCKET_DONE = 'wro-done'
    BUCKET_FAILED = 'wro-failed'
    BUCKET_TEMP = 'wrc_wro_temp2'

    # Regions (e.g. us, us-east1, etc.)
    REGION = 'us-east1'
    ZONE = 'us-east1-b'

    # Compute engines
    COMPUTE_ENGINE = 'nasaweatherdata'

    # BigQuery
    BIQGUERY_DATASET = 'hydro_test'  # TESTING

    BIQGUERY_DATASET_DAILY = 'weather_daily'
    BIQGUERY_DATASET_MONTHLY = 'weather_monthly'
    BIQGUERY_DATASET_CLIMATOLOGY = 'weather_climatology'
    BIQGUERY_DATASET_TEMP = 'weather_temp'  # Only used for temporary storage
    LIST_BQ_DATASETS = [
        BIQGUERY_DATASET_DAILY,
        BIQGUERY_DATASET_MONTHLY,
        BIQGUERY_DATASET_CLIMATOLOGY
    ]

    # Request parameters
    NASA_POWER_URL = 'https://power.larc.nasa.gov/api/temporal'
    NASA_POWER_FORMAT = 'CSV'
    # AG: Agroclimatology, RE: Renewable energy, or SB: Sustainable buildings
    NASA_POWER_COMMUNITY = ['RE', 'SB', 'AG']
    DEFAULT_TIMEOUT = 60  # Timeout in seconds for requests
    DEFAULT_SLEEP = 30  # Sleep time in seconds for when a request fails
    MAX_REQUESTS = 10  # Number of attempts a request will be done if it fails
    SKIP_LEADING_ROWS = 10  # Rows to skip at the start of the received request content (e.g. headers)
    SKIP_TRAILING_ROWS = 1  # Rows to skip at the e of the reveived request content (e.g. headers)

    # Temporal types
    DAILY = 'daily'
    MONTHLY = 'monthly'
    CLIMATOLOGY = 'climatology'
    # NASA_POWER_TEMPORAL_AVE = [DAILY, MONTHLY, CLIMATOLOGY]
    NASA_POWER_TEMPORAL_AVE = [DAILY]

    LAT_FIELD = 'LAT'
    LON_FIELD = 'LON'

    # Grid tiles used for each request
    SA_GRID_EXTENTS = [
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "16.057872772",  # left
            "lon_max": "19.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "16.057872772",  # left
            "lon_max": "19.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "16.057872772",  # left
            "lon_max": "19.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-24.623123169",  # bottom
            "lat_max": "-21.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-24.623123169",  # bottom
            "lat_max": "-21.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-24.623123169",  # bottom
            "lat_max": "-21.623123169",  # top
            "lon_min": "31.057872772",  # left
            "lon_max": "34.057872771999996"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "31.057872772",  # left
            "lon_max": "34.057872771999996"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "31.057872772",  # left
            "lon_max": "34.057872771999996"  # right
        }
    ]

    # Prefixes used for temporal types
    MONTHLY_PREFIX = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
        'Monthly_ave'
    ]
    CLIMATOLOGY_PREFIX = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
        'Annual'
    ]


class Definitions:
    # Solar fluxes and related
    SKY_SURFACE_SW_IRRADIANCE = {
        'key': 'ALLSKY_SFC_SW_DWN',
        'name': 'Sky_surface_shortwave_irradiance',
        'description': 'All sky surface shortwave downward irradiance'
    }
    SKY_SURFACE_SW_IRRADIANCE_GMT = {
        'key': 'ALLSKY_SFC_SW_DWN_HR',
        'name': 'Sky_surface_shortwave_irradiance_GMT',
        'description': 'All sky surface shortwave downward irradiance at GMT times'
    }
    CLEAR_SKY_SURFACE_SW_IRRADIANCE = {
        'key': 'CLRSKY_SFC_SW_DWN',
        'name': 'Clear_sky_surface_shortwave_irradiance',
        'description': 'Clear sky surface shortwave'
    }
    SKY_INSOLATION_CLEARNESS_INDEX = {
        'key': 'ALLSKY_KT',
        'name': 'Sky_insolation_clearness_index',
        'description': 'All sky insolation clearness index'
    }
    CLEAR_SKY_INSOLATION_CLEARNESS_INDEX = {
        'key': 'CLRSKY_KT',
        'name': 'Clear_sky_insolation_clearness_index',
        'description': 'Clear sky insolation clearness index'
    }
    SKY_SURFACE_LW_IRRADIANCE = {
        'key': 'ALLSKY_SFC_LW_DWN',
        'name': 'Sky_surface_longwave',
        'description': 'All sky surface longwave downward irradiance (thermal infrared)'
    }
    SKY_SURFACE_PS_ACTIVE_RADIATION = {
        'key': 'ALLSKY_SFC_PAR_TOT',
        'name': 'Sky_surface_PAR_total',
        'description': 'All sky surface photosynthetically active radiation (PAR) total'
    }
    CLEAR_SKY_SURFACE_PS_ACTIVE_RADIATION = {
        'key': 'CLRSKY_SFC_PAR_TOT',
        'name': 'Clear_sky_surface_PAR_total',
        'description': 'Clear sky surface photosynthetically active radiation (PAR) total'
    }
    SKY_SURFACE_UVA_IRRADIANCE = {
        'key': 'ALLSKY_SFC_UVA',
        'name': 'Sky_surface_UVA',
        'description': 'All sky surface UVA irradiance'
    }
    SKY_SURFACE_UVB_IRRADIANCE = {
        'key': 'ALLSKY_SFC_UVB',
        'name': 'Sky_surface_UVB',
        'description': 'All sky surface UVB irradiance'
    }
    SKY_SURFACE_UV_INDEX = {
        'key': 'ALLSKY_SFC_UV_INDEX',
        'name': 'Sky_surface_UV_index',
        'description': 'All sky surface UV index'
    }
    SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE = {
        'key': 'ALLSKY_SFC_SW_DNI',
        'name': 'Sky_surface_shortwave_direct_normal_irradiance',
        'description': 'All sky surface shortwave downward direct normal irradiance'
    }
    SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE_MAX = {
        'key': 'ALLSKY_SFC_SW_DNI_MAX',
        'name': 'Sky_surface_shortwave_direct_normal_irradiance_max',
        'description': 'All sky surface shortwave direct normal irradiance maximum'
    }
    SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE_MIN = {
        'key': 'ALLSKY_SFC_SW_DNI_MIN',
        'name': 'Sky_surface_shortwave_direct_normal_irradiance_min',
        'description': 'All sky surface shortwave direct normal irradiance minimum'
    }
    SKY_SURFACE_SW_DIFFUSE_IRRADIANCE = {
        'key': 'ALLSKY_SFC_SW_DIFF',
        'name': 'Sky_surface_shortwave_diffuse_irradiance',
        'description': 'All sky surface shortwave diffuse irradiance'
    }
    SKY_SURFACE_SW_DIFFUSE_IRRADIANCE_MAX = {
        'key': 'ALLSKY_SFC_SW_DIFF_MAX',
        'name': 'Sky_surface_shortwave_diffuse_irradiance_max',
        'description': 'All sky surface shortwave diffuse irradiance maximum'
    }
    SKY_SURFACE_SW_DIFFUSE_IRRADIANCE_MIN = {
        'key': 'ALLSKY_SFC_SW_DIFF_MIN',
        'name': 'Sky_surface_shortwave_diffuse_irradiance_min',
        'description': 'All sky surface shortwave diffuse irradiance minimum'
    }
    SKY_SURFACE_ALBEDO = {
        'key': 'ALLSKY_SRF_ALB',
        'name': 'Sky_surface_albedo',
        'description': 'All sky surface albedo'
    }
    TOA_SW_IRRADIANCE = {
        'key': 'TOA_SW_DWN',
        'name': 'TOA_shortwave_irradiance',
        'description': 'Top-of-atmosphere shortwave downward irradiance'
    }
    CLOUD_AMOUNT = {
        'key': 'CLOUD_AMT',
        'name': 'Cloud_amount',
        'description': 'Cloud amount'
    }
    CLOUD_AMOUNT_GMT = {
        'key': 'CLOUD_AMT_HR',
        'name': '',
        'description': 'Cloud amount at GMT times'
    }

    # Parameters for solar cooking
    WINDSPEED_2M = {
        'key': 'WS2M',
        'name': 'Windspeed_02m',
        'description': 'Windspeed at 2 meters'
    }
    MIDDAY_INSOLATION_INCIDENT = {
        'key': 'MIDDAY_INSOL',
        'name': 'Midday_insolation',
        'description': 'Midday insolation incident'
    }

    # Temperature/Precipitation
    TEMP = {
        'key': 'T2M',
        'name': 'Temperature',
        'description': 'Temperature at 2 meters'
    }
    DEW_FROST = {
        'key': 'T2MDEW',
        'name': 'Frost',
        'description': 'Dew/frost point at 2 meters'
    }
    WET_TEMP = {
        'key': 'T2MWET',
        'name': 'Wet_temperature',
        'description': 'Wet bulb temperature at 2 meters'
    }
    EARTH_SKIN_TEMP = {
        'key': 'TS',
        'name': 'Earth_skin_temperature',
        'description': 'Earth skin temperature'
    }
    EARTH_SKIN_TEMP_MAX = {
        'key': 'TS_MAX',
        'name': 'Earth_skin_temperature_max',
        'description': 'Earth skin temperature maximum'
    }
    EARTH_SKIN_TEMP_MIN = {
        'key': 'TS_MIN',
        'name': 'Earth_skin_temperature_min',
        'description': 'Earth skin temperature minimum'
    }
    TEMP_RANGE = {
        'key': 'T2M_RANGE',
        'name': 'Temperature_range',
        'description': 'Temperature at 2 meters range'
    }
    TEMP_MAX = {
        'key': 'T2M_MAX',
        'name': 'Temperature_max',
        'description': 'Temperature at 2 meters maximum'
    }
    TEMP_MIN = {
        'key': 'T2M_MIN',
        'name': 'Temperature_min',
        'description': 'Temperature at 2 meters minimum'
    }
    SPECIFIC_HUMIDITY = {
        'key': 'QV2M',
        'name': 'Specific_humidity',
        'description': 'Specific humidity at 2 meters'
    }
    RELATIVE_HUMIDITY = {
        'key': 'RH2M',
        'name': 'Relative_humidity',
        'description': 'Relative humidity at meters'
    }
    PRECIPITATION = {
        'key': 'PRECTOTCORR',
        'name': 'Precipitation_ave',
        'description': 'Average precipitation'
    }
    PRECIPITATION_SUM = {
        'key': 'PRECTOTCORR_SUM',
        'name': 'Precipitation_ave_sum',
        'description': 'Precipitation sum average'
    }

    # Wind/Pressure
    SURFACE_PRESSURE = {
        'key': 'PS',
        'name': 'Surface_pressure',
        'description': 'Surface pressure'
    }
    WINDSPEED_10M = {
        'key': 'WS10M',
        'name': 'Windspeed_10m',
        'description': 'Wind speed at 10 meters'
    }
    WINDSPEED_10M_MAX = {
        'key': 'WS10M_MAX',
        'name': 'Windspeed_max_10m',
        'description': 'Wind speed at 10 meters maximum'
    }
    WINDSPEED_10M_MIN = {
        'key': 'WS10M_MIN',
        'name': 'Windspeed_min_10m',
        'description': 'Wind speed at 10 meters minimum'
    }
    WINDSPEED_10M_RANGE = {
        'key': 'WS10M_RANGE',
        'name': 'Windspeed_range_10m',
        'description': 'Wind speed at 10 meters range'
    }
    WIND_DIRECTION_10M = {
        'key': 'WD10M',
        'name': 'Wind_direction_10m',
        'description': 'Wind direction at 10 meters'
    }
    WINDSPEED_50M = {
        'key': 'WS50M',
        'name': 'Windspeed_50m',
        'description': 'Wind speed at 50 meters'
    }
    WINDSPEED_50M_MAX = {
        'key': 'WS50M_MAX',
        'name': 'Windspeed_max_50m',
        'description': 'Wind speed at 50 meters maximum'
    }
    WINDSPEED_50M_MIN = {
        'key': 'WS50M_MIN',
        'name': 'Windspeed_min_50m',
        'description': 'Wind speed at 50 meters minimum'
    }
    WINDSPEED_50M_RANGE = {
        'key': 'WS50M_RANGE',
        'name': 'Windspeed_range_50m',
        'description': 'Wind speed at 50 meters range'
    }
    WIND_DIRECTION_50M = {
        'key': 'WD50M',
        'name': 'Wind_direction_50m',
        'description': 'Wind direction at 50 meters'
    }

    # DOE/ASHRAE climate building
    COOLING_DEGREE_DAYS_ABOVE_ZERO = {
        'key': 'CDD0',
        'name': 'Cooling_degree_days_above_00',
        'description': 'Cooling degree days above 0 celcius'
    }
    COOLING_DEGREE_DAYS_ABOVE_10 = {
        'key': 'CDD10',
        'name': 'Cooling_degree_days_above_10',
        'description': 'Cooling degree days above 10 celcius'
    }
    COOLING_DEGREE_DAYS_ABOVE_18 = {
        'key': 'CDD18_3',
        'name': 'Cooling_degree_days_above_18_3',
        'description': 'Cooling degree days above 18.3 celcius'
    }
    HEATING_DEGREE_DAYS_BELOW_ZERO = {
        'key': 'HDD0',
        'name': 'Heating_degree_days_below_00',
        'description': 'Heating degree days below 0 celcius'
    }
    HEATING_DEGREE_DAYS_BELOW_10 = {
        'key': 'HDD10',
        'name': 'Heating_degree_days_below_10',
        'description': 'Heating degree days below 10 celcius'
    }
    HEATING_DEGREE_DAYS_BELOW_18 = {
        'key': 'HDD18_3',
        'name': 'Heating_degree_days_below_18_3',
        'description': 'Heating degree days below 18.3 celcius'
    }

    # Soil properties
    SURFACE_SOIL_WETNESS = {
        'key': 'GWETTOP',
        'name': 'Surface_soil_wetness',
        'description': 'Surface soil wetness (surface to 5 cm below)'
    }
    ROOT_SOIL_WETNESS = {
        'key': 'GWETROOT',
        'name': 'Root_soil_wetness',
        'description': 'Root zone soil wetness (surface to 100 cm below)'
    }
    PROFILE_SOIL_MOISTURE = {
        'key': 'GWETPROF',
        'name': 'Profile_soil_moisture',
        'description': 'Profile soil moisture (surface to bedrock)'
    }

    # Dataset lists
    LIST_NASA_POWER_DATASETS_RE_DAILY = [
        # SKY_SURFACE_SW_IRRADIANCE,  # include done 2
        # CLEAR_SKY_SURFACE_SW_IRRADIANCE,
        # SKY_INSOLATION_CLEARNESS_INDEX,
        # SKY_SURFACE_LW_IRRADIANCE,
        # SKY_SURFACE_PS_ACTIVE_RADIATION,
        # CLEAR_SKY_SURFACE_PS_ACTIVE_RADIATION,
        # SKY_SURFACE_UVA_IRRADIANCE,
        # SKY_SURFACE_UVB_IRRADIANCE,
        # SKY_SURFACE_UV_INDEX,
        # WINDSPEED_2M,  # include done 2
        # TEMP,  # include done 2
        # DEW_FROST,  # include, done 2
        # WET_TEMP,  # include, done 2
        # EARTH_SKIN_TEMP,  # include, done 2
        # TEMP_RANGE,
        # TEMP_MAX,  # include, done 2
        # TEMP_MIN,  # include, running 2
        # SPECIFIC_HUMIDITY,
        RELATIVE_HUMIDITY,  # include, running 2
        # PRECIPITATION,  # include, done 1
        # SURFACE_PRESSURE,
        # WINDSPEED_10M,  # include, done 1
        # WINDSPEED_10M_MAX,
        # WINDSPEED_10M_MIN,
        # WINDSPEED_10M_RANGE,
        # WIND_DIRECTION_10M,
        # WINDSPEED_50M,
        # WINDSPEED_50M_MAX,
        # WINDSPEED_50M_MIN,
        # WINDSPEED_50M_RANGE,
        # WIND_DIRECTION_50M,
    ]
    LIST_NASA_POWER_DATASETS_SB_DAILY = [
        # COOLING_DEGREE_DAYS_ABOVE_ZERO,
        # COOLING_DEGREE_DAYS_ABOVE_10,
        # COOLING_DEGREE_DAYS_ABOVE_18,
        # HEATING_DEGREE_DAYS_BELOW_ZERO,
        # HEATING_DEGREE_DAYS_BELOW_10,
        # HEATING_DEGREE_DAYS_BELOW_18
    ]
    LIST_NASA_POWER_DATASETS_AG_DAILY = [
        #SURFACE_SOIL_WETNESS,  # include, done 2
        #ROOT_SOIL_WETNESS,  # include, running 2
        PROFILE_SOIL_MOISTURE  # include, running 1
    ]

    LIST_NASA_POWER_DATASETS_RE_MONTHLY = [
        SKY_SURFACE_SW_IRRADIANCE,
        # CLEAR_SKY_SURFACE_SW_IRRADIANCE,
        # SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE,
        # SKY_SURFACE_SW_DIFFUSE_IRRADIANCE,
        # SKY_INSOLATION_CLEARNESS_INDEX,
        # CLEAR_SKY_INSOLATION_CLEARNESS_INDEX,
        # SKY_SURFACE_ALBEDO,
        # TOA_SW_IRRADIANCE,
        CLOUD_AMOUNT,  # NOT done, back end service issue on NASA POWER's side.
        SKY_SURFACE_PS_ACTIVE_RADIATION,
        # CLEAR_SKY_SURFACE_PS_ACTIVE_RADIATION,
        # SKY_SURFACE_UVA_IRRADIANCE,
        # SKY_SURFACE_UVB_IRRADIANCE,
        # SKY_SURFACE_UV_INDEX,
        WINDSPEED_2M,
        TEMP,
        DEW_FROST,
        WET_TEMP,
        EARTH_SKIN_TEMP,
        # TEMP_RANGE,
        TEMP_MAX,
        TEMP_MIN,
        # SKY_SURFACE_LW_IRRADIANCE,
        SPECIFIC_HUMIDITY,
        RELATIVE_HUMIDITY,
        PRECIPITATION,
        PRECIPITATION_SUM,
        # SURFACE_PRESSURE,
        WINDSPEED_10M,
        # WINDSPEED_10M_MAX,
        # WINDSPEED_10M_MIN,
        # WINDSPEED_10M_RANGE,
        # WIND_DIRECTION_10M,
        # WINDSPEED_50M,
        # WINDSPEED_50M_MAX,
        # WINDSPEED_50M_MIN,
        # WINDSPEED_50M_RANGE,
        # WIND_DIRECTION_50M
    ]
    LIST_NASA_POWER_DATASETS_SB_MONTHLY = [
        # COOLING_DEGREE_DAYS_ABOVE_ZERO,
        # COOLING_DEGREE_DAYS_ABOVE_10,
        # COOLING_DEGREE_DAYS_ABOVE_18,
        # HEATING_DEGREE_DAYS_BELOW_ZERO,
        # HEATING_DEGREE_DAYS_BELOW_10,
        # HEATING_DEGREE_DAYS_BELOW_18
    ]
    LIST_NASA_POWER_DATASETS_AG_MONTHLY = [
        SURFACE_SOIL_WETNESS,
        ROOT_SOIL_WETNESS,
        PROFILE_SOIL_MOISTURE
    ]

    LIST_NASA_POWER_DATASETS_RE_CLIMATOLOGY = [
        SKY_SURFACE_SW_IRRADIANCE,
        # SKY_SURFACE_SW_IRRADIANCE_GMT,
        # CLEAR_SKY_SURFACE_SW_IRRADIANCE,
        # SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE,
        # SKY_SURFACE_SW_DIFFUSE_IRRADIANCE,
        # SKY_INSOLATION_CLEARNESS_INDEX,
        # SKY_SURFACE_ALBEDO,
        # TOA_SW_IRRADIANCE,
        CLOUD_AMOUNT,
        SKY_SURFACE_PS_ACTIVE_RADIATION,
        CLEAR_SKY_SURFACE_PS_ACTIVE_RADIATION,
        # SKY_SURFACE_UVA_IRRADIANCE,
        # SKY_SURFACE_UVB_IRRADIANCE,
        # SKY_SURFACE_UV_INDEX,
        # SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE_MAX,
        # SKY_SURFACE_SW_DIRECT_NORMAL_IRRADIANCE_MIN,
        # SKY_SURFACE_SW_DIFFUSE_IRRADIANCE_MAX,
        # SKY_SURFACE_SW_DIFFUSE_IRRADIANCE_MIN,
        # MIDDAY_INSOLATION_INCIDENT,
        WINDSPEED_2M,
        TEMP,
        DEW_FROST,
        WET_TEMP,
        EARTH_SKIN_TEMP,
        # TEMP_RANGE,
        TEMP_MAX,
        TEMP_MIN,
        # EARTH_SKIN_TEMP_MAX,
        # EARTH_SKIN_TEMP_MIN,
        # SKY_SURFACE_LW_IRRADIANCE,
        SPECIFIC_HUMIDITY,
        RELATIVE_HUMIDITY,
        PRECIPITATION,
        PRECIPITATION_SUM,
        # SURFACE_PRESSURE,
        WINDSPEED_10M,
        # WINDSPEED_10M_MAX,
        # WINDSPEED_10M_MIN,
        # WINDSPEED_10M_RANGE,
        # WINDSPEED_50M,
        # WINDSPEED_50M_MAX,
        # WINDSPEED_50M_MIN,
        # WINDSPEED_50M_RANGE,
        # CLOUD_AMOUNT_GMT
    ]
    LIST_NASA_POWER_DATASETS_SB_CLIMATOLOGY = [
        # COOLING_DEGREE_DAYS_ABOVE_ZERO,
        # COOLING_DEGREE_DAYS_ABOVE_10,
        # COOLING_DEGREE_DAYS_ABOVE_18,
        # HEATING_DEGREE_DAYS_BELOW_ZERO,
        # HEATING_DEGREE_DAYS_BELOW_10,
        # HEATING_DEGREE_DAYS_BELOW_18
    ]
    LIST_NASA_POWER_DATASETS_AG_CLIMATOLOGY = [
        SURFACE_SOIL_WETNESS,
        ROOT_SOIL_WETNESS,
        PROFILE_SOIL_MOISTURE
    ]


class Utilities:
    @staticmethod
    def list_bucket_data(project, bucket):
        """Lists files contained in a bucket.

        :param project: Google cloud platform project ID
        :type project: String

        :param bucket: Google cloud platform bucket name
        :type bucket: String

        :returns: Lists containing files directories.
        :rtype: List
        """
        # Storage client
        client = storage.Client(project=project)
        bucket = client.get_bucket(bucket)

        list_csv = []
        list_excel = []
        list_archives = []
        list_raster = []
        list_vector = []

        for blob in bucket.list_blobs():
            content_name = blob.name
            if content_name.endswith('.csv'):
                list_csv.append(content_name)
            elif content_name.endswith('.zip') or content_name.endswith('.7z'):
                list_archives.append(content_name)
            elif content_name.endswith('.shp'):
                list_vector.append(content_name)

        return list_csv, list_excel, list_archives, list_raster, list_vector

    @staticmethod
    def move_data(source_bucket, destination_bucket, source_file, destination_file):
        """Moves a file from a bucket to other location or bucket.

        :param source_bucket: Bucket name where the file is stored
        :type source_bucket: String

        :param destination_bucket: Destination bucket name to which the file will be moved
        :type destination_bucket: String

        :param source_file: File which will be moved
        :type source_file: String

        :param destination_file: Location to which the file will be moved
        :type destination_file: String

        :returns: True if data move has been successful, false if data move has failed
        :rtype: boolean
        """
        try:
            client = storage.Client(project=Default.PROJECT_ID)
            bucket = client.bucket(source_bucket)
            destination_bucket = client.bucket(destination_bucket)

            blob_to_move = bucket.blob(source_file)
            bucket.copy_blob(
                blob_to_move,
                destination_bucket,
                destination_file
            )
        except Exception as e:
            # Loading from csv file into bigquery failed
            # The newly created bigquery table will be deleted
            print("Could not move " + source_file)
            print("EXCEPTION: " + str(e))
            return False

        # Deletes the source file if the file has been copied to the destination
        bucket.delete_blob(source_file)

        # Returns if the file has been moved
        return True

    @staticmethod
    def convert_json_to_newline_json(data_json):
        """Convert JSON/GEOJSON to newline JSON. This is required for BigQuery table creation.

        :param data_json: JSON/GEOJSON data
        :type data_json: JSON/GEOJSON

        :returns: Newline JSON formatted string
        :rtype: Newline JSON
        """
        list_newline_json = []

        list_features = data_json['features']
        for feature in list_features:
            feat_properties = feature['properties']
            feat_id = feat_properties['id']
            feat_desc = feat_properties['desc']
            feat_geom = feature['geometry']

            new_json_feat = {
                'id': feat_id,
                'desc': feat_desc,
                'geometry': feat_geom
            }
            list_newline_json.append(new_json_feat)

        return list_newline_json

    @staticmethod
    def shp_to_geojson(shp_file):
        """Converts a shapefile stored in Google cloud storage GEOJSON.

        :param shp_file: Google cloud storage directory of the shapefile (e.g. gs://bucket/folder/file.shp)
        :type shp_file: Shapefile
        """

        print('shp found')

        gc_shp = 'gs://' + Default.BUCKET_TRIGGER + '/' + shp_file

        shp_geopandas = geopandas.read_file(gc_shp)
        shp_json = json.loads(shp_geopandas.to_json())
        newline_json = Utilities.convert_json_to_newline_json(shp_json)

        print('newline json created')

        client_bq = bigquery.Client()

        bq_table_uri = Default.PROJECT_ID + '.' + Default.BIQGUERY_DATASET + '.' + shp_file.replace('.shp', '')

        schema = [
            bigquery.SchemaField('id', 'INTEGER', mode='NULLABLE'),
            bigquery.SchemaField('desc', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('geometry', 'GEOGRAPHY', mode='NULLABLE'),
        ]

        table = bigquery.Table(bq_table_uri, schema=schema)
        client_bq.create_table(table)

        print('table created')

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        print('start load')

        load_job = client_bq.load_table_from_json(newline_json, bq_table_uri, job_config=job_config)
        load_job.result()

        print('done')

    @staticmethod
    def write_to_file(file, lines):
        """Writes lines to a text/CSV file.

        :param file: Output/target file
        :type file: String

        :param lines: Variable which contains a list of the lines which needs to be written to the file
        :type lines: List
        """
        if not os.path.exists(file):
            # File does not exist, create it
            with open(file, 'w+') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
        else:
            # File exists, append to it
            with open(file, 'a') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')

        f.close()

    @staticmethod
    def write_to_log(file, line):
        """Writes to a log text file.

        :param file: Output/target file
        :type file: String

        :param line: Variable which contains a list of the lines which needs to be written to the log file
        :type line: List
        """
        if True:
            now = datetime.now()
            line = '[' + str(now) + '] ' + line
            print(line)

            if not os.path.exists(file):
                # File does not exist, create it
                with open(file, 'w+') as f:
                    f.write(line)
                    f.write('\n')
            else:
                # File exists, append to it
                with open(file, 'a') as f:
                    f.write(line)
                    f.write('\n')

            f.close()

    @staticmethod
    def unzip(zip_file):
        """Unzips a zip file stored in a Google cloud storage bucket.

        :param zip_file: Google cloud storage directory (e.g. gs://bucket/folder/file.zip)
        :type zip_file: String

        :returns: True if the zip file extracted successfully, false if it failed
        :rtype: boolean
        """
        try:
            client = storage.Client(project=Default.PROJECT_ID)
            bucket = client.get_bucket(Default.BUCKET_TRIGGER)

            blob = bucket.blob(zip_file)
            zipbytes = io.BytesIO(blob.download_as_string())

            if zipfile.is_zipfile(zipbytes):
                with zipfile.ZipFile(zipbytes, 'r') as myzip:
                    for contentfilename in myzip.namelist():
                        contentfile = myzip.read(contentfilename)

                        blob_upload = bucket.blob(contentfilename)
                        blob_upload.upload_from_string(contentfile)
        except Exception as e:
            # Loading from csv file into bigquery failed
            # The newly created bigquery table will be deleted
            print("Could unzip " + zip_file)
            print("EXCEPTION: " + str(e))
            return False

        # Returns True if the file unzipped correctly
        return True

    @staticmethod
    def get_dataset_list(community, temporal):
        """Unzips a zip file stored in a Google cloud storage bucket.

        :param community: Renewable energy ('RE'), sustainable buildings ('SB'), or agroclimatology ('AG')
        :type community: String

        :param temporal: 'daily', 'monthly', or 'climatology'
        :type temporal: String

        :returns: A list contains the datasets which will be downloaded from NASA POWER
        :rtype: list
        """
        if community == 'RE':
            # Renewable energy
            if temporal == Default.DAILY:
                return Definitions.LIST_NASA_POWER_DATASETS_RE_DAILY
            elif temporal == Default.MONTHLY:
                return Definitions.LIST_NASA_POWER_DATASETS_RE_MONTHLY
            elif temporal == Default.CLIMATOLOGY:
                return Definitions.LIST_NASA_POWER_DATASETS_RE_CLIMATOLOGY
        elif community == 'SB':
            # Sustainable buildings
            if temporal == Default.DAILY:
                return Definitions.LIST_NASA_POWER_DATASETS_SB_DAILY
            elif temporal == Default.MONTHLY:
                return Definitions.LIST_NASA_POWER_DATASETS_SB_MONTHLY
            elif temporal == Default.CLIMATOLOGY:
                return Definitions.LIST_NASA_POWER_DATASETS_SB_CLIMATOLOGY
        elif community == 'AG':
            # Agroclimatology
            if temporal == Default.DAILY:
                return Definitions.LIST_NASA_POWER_DATASETS_AG_DAILY
            elif temporal == Default.MONTHLY:
                return Definitions.LIST_NASA_POWER_DATASETS_AG_MONTHLY
            elif temporal == Default.CLIMATOLOGY:
                return Definitions.LIST_NASA_POWER_DATASETS_AG_CLIMATOLOGY

        # List could not be determined
        return []

    @staticmethod
    def append_field_names(list_field_names, period, name, start_date, end_date):
        """Appends field names to an existing list. Daily only requires a single field,
        monthly requires 13 (Jan to Dec and average monthly), and climatology also
        requires 13 (Jan to Dec and annual).

        :param list_field_names: List of fieldnames
        :type list_field_names: list

        :param period: 'daily', 'monthly', or 'climatology'
        :type period: String

        :param name: The prefix to add to the field name
        :type name: String

        :param start_date: Start of the date range
        :type start_date: String

        :param end_date: End of the date range
        :type end_date: String

        :returns: Contains the updated fields list
        :rtype: list
        """

        if period == Default.DAILY:

            day_count = Utilities.get_day_count(
                start_date,
                end_date
            )

            i = 1
            while i <= day_count:
                if i <= 9:
                    # For the first 9 numbers a '0' is added (e.g. 19980109)
                    date = start_date[:len(start_date) - 2] + '0' + str(i)
                else:
                    date = start_date[:len(start_date) - 2] + str(i)
                field_name = '{}_{}'.format(
                    name,
                    date
                )
                list_field_names.append(field_name)
                i = i + 1
        elif period == Default.MONTHLY:
            for field_prefix in Default.MONTHLY_PREFIX:
                field_name = '{}_{}_{}'.format(
                    name,
                    field_prefix,
                    start_date
                )
                list_field_names.append(field_name)
        else:
            # Climatology
            for field_prefix in Default.CLIMATOLOGY_PREFIX:
                field_name = '{}_{}'.format(
                    name,
                    field_prefix
                )
                list_field_names.append(field_name)

        return list_field_names

    @staticmethod
    def table_to_geojson(dataset_id, table_name):
        client = bigquery.Client()

        table_json = table_name + ".json"
        destination_uri = "gs://{}/{}".format(Default.BUCKET_TEMP, table_json)
        dataset_ref = bigquery.DatasetReference(Default.PROJECT_ID, dataset_id)
        table_ref = dataset_ref.table(table_name)
        job_config = bigquery.job.ExtractJobConfig()
        job_config.destination_format = bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON

        extract_job = client.extract_table(
            table_ref,
            destination_uri,
            job_config=job_config,
            # Location must match that of the source table.
            location=Default.REGION,
        )  # API request
        extract_job.result()  # Waits for job to complete.

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(Default.BUCKET_TEMP)
        blob = bucket.blob(table_json)

        blob_string = str(blob.download_as_string(client=None))
        blob_string = blob_string.replace('\'b', '')
        blob_string = blob_string[2:]  # Removes '\b' at the start of the string
        split_json = blob_string.split(r'\n')  # Creates a list
        split_json = split_json[:len(split_json) - 1]  # Removes the last element of the list

        blob_json = [json.loads(line) for line in split_json]
        data_geojson = Utilities.json_to_geojson(blob_json, 0, 1)

        bucket.delete_blob(table_json)

        return data_geojson

    @staticmethod
    def get_request_content_indices(period):
        """Gets the latitude index, longitude index, and a list of indices for the
        CSV file contents received from NASA POWER when a request is done. These indices
        differs for daily, monthly, and climatology.

        :param period: 'daily', 'monthly', or 'climatology'
        :type period: String

        :returns: lat_index contains the latitude index
        :rtype: integer

        :returns: lon_index contains the longitude index
        :rtype: integer

        :returns: value_index contains a list of indices for the values
        :rtype: list
        """
        if period == Default.DAILY:
            # Only a lat, long, and a single value
            lat_index = 0
            lon_index = 1
            value_index = [5]
        elif period == Default.MONTHLY:
            # Lat, lon, all months and monthly average
            lat_index = 2
            lon_index = 3
            value_index = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        else:
            # Climatology. Lat, lon, all months, and annual
            lat_index = 1
            lon_index = 2
            value_index = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

        return lat_index, lon_index, value_index

    @staticmethod
    def get_day_count(start_date, end_date):
        """Get the number of days in the given date range.

        :param start_date: Start date of the date range (YYYYMMDD)
        :type start_date: str

        :param end_date: End date of the date range (YYYYMMDD)
        :type end_date: str

        :returns: Number of days in the given date range
        :rtype: int
        """
        frequency = 'D'  # Daily
        date_format = "%Y%m%d"  # YYYYMMDD
        list_dates = pd.date_range(start_date, end_date, freq=frequency).strftime(date_format).tolist()
        number_of_days = len(list_dates)

        return number_of_days

    @staticmethod
    def get_date_list(temporal, start_year, end_year, start_month, end_month, start_day, end_day):
        """Based on the temporal type and dates provided, this function returns a list of dates.
        For daily it will return all days, monthly all the months, and for climatology it will return no dates.
        Climatology does not require dates.

        :param temporal: 'daily', 'monthly', or 'climatology'
        :type temporal: String

        :param start_year: Start year
        :type start_year: int

        :param end_year: End year
        :type end_year: int

        :param start_month: Start month
        :type start_month: int

        :param end_month: End month
        :type end_month: int

        :param start_day: Start day
        :type start_day: int

        :param end_day: End day
        :type end_day: int

        :returns: True if a date will be required for the request, otherwise False
        :rtype: boolean

        :returns: A list which contains the dates which will be used to perform requests
        :rtype: list
        """
        if temporal == Default.DAILY:
            # Converts all values to string
            # This is required for the pandas date_range method
            start_year = str(start_year)
            end_year = str(end_year)
            start_month = str(start_month)
            end_month = str(end_month)
            start_day = str(start_day)
            end_day = str(end_day)

            list_dates = []

            # YYYYMMDD
            pd_start_date = "{}-{}-{}".format(start_year, start_month, start_day)
            pd_end_date = "{}-{}-{}".format(end_year, end_month, end_day)

            frequency = 'M'  # Daily
            date_format = "%Y%m%d"
            list_days_temp = pd.date_range(pd_start_date, pd_end_date, freq=frequency).strftime(date_format).tolist()

            for day in list_days_temp:
                list_dates.append(
                    {
                        'start_date': day[:len(day) - 2] + '01',
                        'end_date': day
                    }
                )
            dates_required = True
        elif temporal == Default.MONTHLY:
            list_years_temp = range(start_year, end_year + 1)
            list_dates = []

            for year in list_years_temp:
                dates = {
                    'start_date': str(year),
                    'end_date': str(year)
                }
                list_dates.append(dates)
            dates_required = True
        else:
            # Climatology requires no date
            # A single item added so that it enters the loop
            # Value will not be used
            list_dates = [-1]
            dates_required = False

        return dates_required, list_dates

    @staticmethod
    def transform_daily_data(lines):
        """Transforms the contents received from NASA POWER by creating columns for each day from the
        received contents.

        :param lines: The lines received from NASA POWER
        :type lines: list

        :returns: List which contains each of the transformed rows. The rows will now consist of columns
        :rtype: list
        """
        columns = []
        column_contents = []
        cur_day = None
        for line in lines:
            split_line = line.split(',')  # All columns of the row
            day = int(split_line[4])

            if cur_day is None:
                # Only performed at the start of the transformation
                cur_day = day

            if day > cur_day:
                # Next column (next day)
                columns.append(column_contents)
                column_contents = [line]
                cur_day = day
            else:
                # Append to current column (continuation of the same day)
                column_contents.append(line)
        columns.append(column_contents)  # Appends the new columns

        column_count = len(columns)  # Number of days in the month
        transformed_lines = []
        # Creates the new rows from the daily columns
        if column_count > 0:
            contents_count = len(columns[0])
            i = 0
            # Creates each row
            while i < contents_count:
                transformed_line = ''
                for column in columns:
                    column_line = column[i]
                    if transformed_line == '':
                        # Includes lat and lon if it's the start of a row
                        column_line_split = column_line.split(',')
                        lat = column_line_split[0]
                        lon = column_line_split[1]
                        value = column_line_split[5]
                        transformed_line = "{},{},{}".format(
                            lat,
                            lon,
                            value
                        )
                    else:
                        # Lat and lon no longer required, as it exists in the row
                        column_line_split = column_line.split(',')
                        transformed_line = "{},{}".format(
                            transformed_line,
                            column_line_split[5]
                        )
                transformed_lines.append(transformed_line)  # Adds the transformed row
                i = i + 1

        return transformed_lines

    @staticmethod
    def get_bq_dataset(period):
        """Gets the list of datasets associated with the provided temporal type.

        :param period: Temporal period (e.g. daily, monthly, or climatology)
        :type period: str

        :returns: All the datasets (e.g. windspeed) with the given temporal type
        :rtype: str
        """
        if period == Default.DAILY:
            return Default.LIST_BQ_DATASETS[0]
        elif period == Default.MONTHLY:
            return Default.LIST_BQ_DATASETS[1]
        else:
            return Default.LIST_BQ_DATASETS[2]

    @staticmethod
    def json_to_geojson(data_json, lat_index, lon_index):
        """Takes newline json as input and converts it to geojson. The index in the attribute table
        of the latitude and longitude fields needs to be provided.
        Currently for POINT data, but can be changed to include other types.

        :param data_json: Newline json which contains the spatial data
        :type data_json: Newline json

        :param lat_index: Index field which contains the latitude
        :type lat_index: int

        :param lon_index: Index field which contains the longitude
        :type lon_index: int

        :returns: Geojson version of the newline json data
        :rtype: geojson
        """
        list_elements = []
        for element in data_json:
            lat = 0
            lon = 0
            list_properties = {}
            i = 0
            for field in element:
                if i == lat_index:
                    # Latitude field
                    lat = element[field]
                elif i == lon_index:
                    # Longitude field
                    lon = element[field]
                else:
                    # Other fields (e.g. temperature)
                    list_properties[field] = element[field]

                i = i + 1

            new_element = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lat, lon]
                },
                'properties': list_properties
            }
            list_elements.append(new_element)

        data_geojson = {
            'type': 'FeatureCollection',
            'features': list_elements
        }

        return data_geojson

    @staticmethod
    def list_bigquery_tables(bq_dataset):
        """Lists all BigQuery tables in the given dataset.

        :param bq_dataset: BigQuery dataset
        :type bq_dataset: str

        :returns: List of tables found in the provided dataset
        :rtype: list
        """

        client = bigquery.Client()
        tables = client.list_tables(bq_dataset)

        return tables

    @staticmethod
    def get_data(link):
        """Performs a get request on the provided link. Several checks and try/exceptoions is done
        to avoid unexpected errors and to keep the code running.

        :param link: Address for the request
        :type link: str

        :returns: True if the request succeeded, False if it failed
        :rtype: boolean

        :returns: Received request contents
        :rtype: str
        """
        try:
            # Performs the requests and gets the contents from NASA POWER
            result = requests.get(link, timeout=Default.DEFAULT_TIMEOUT)
            result_status = result.status_code
            if result_status == 200:
                # Contents received from NASA POWER
                content = result.content
            else:
                # Errorenous response from NASA POWER
                Utilities.write_to_log("log.txt", "\t\t\tREQUEST ERROR: " + str(result_status))
                Utilities.write_to_log("log.txt", "\t\t\tCONTENT ERROR: " + str(result.content))
                return False, ''
        except Timeout:
            Utilities.write_to_log("log.txt", "\t\t\tTIMEOUT EXCEPTION")
            return False, ''
        except Exception as e:
            Utilities.write_to_log("log.txt", "\t\t\tEXCEPTION: " + str(e))
            return False, ''

        return True, content

    @staticmethod
    def load_csv_into_bucket(bucket_name, contents, csv_name):
        """Uploads string into a CSV file into a bucket.

        :param bucket_name: Google cloud storage bucket name
        :type bucket_name: str

        :param contents: Contents to be written to the CSV file
        :type contents: str

        :param csv_name: Name to give to the CSV file
        :type csv_name: str

        :returns: True if the CSV data has been stored in the bucket successful, false if it failed
        :rtype: boolean
        """
        try:
            # Writes the CSV file to a bucket
            client = storage.Client(project=Default.PROJECT_ID)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(csv_name)
            blob.upload_from_string(contents)
        except Exception as e:
            Utilities.write_to_log("log.txt", "Could not create bucket CSV file " + csv_name)
            Utilities.write_to_log("log.txt", "EXCEPTION: " + str(e))
            return False

        return True

    @staticmethod
    def load_csv_into_bigquery(upload_uri, bq_table_uri, schema, skip_leading_rows=1):
        """Loads a CSV file stored in a bucket into BigQuery.

        :param upload_uri: Google cloud storage directory (e.g. gs://bucket/folder/file)
        :type upload_uri: uri

        :param bq_table_uri: Google cloud storage directory (e.g. gs://bucket/folder/file)
        :type bq_table_uri: uri

        :param schema: Fields structure of the BigQuery table
        :type schema: list

        :param skip_leading_rows: Number of rows to skip at the start of the file
        :type skip_leading_rows: int

        :returns: True if the CSV data has been stored in BigQuery successful, false if it failed
        :rtype: boolean
        """
        client_bq = bigquery.Client()
        try:
            table = bigquery.Table(bq_table_uri, schema=schema)
            client_bq.create_table(table)
        except Exception as e:
            Utilities.write_to_log("log.txt", "Could not create BigQuery table " + bq_table_uri)
            Utilities.write_to_log("log.txt", "EXCEPTION: " + str(e))
            return False

        try:
            job_config = bigquery.LoadJobConfig(
                schema=schema,
                skip_leading_rows=skip_leading_rows,
                source_format=bigquery.SourceFormat.CSV
            )

            load_job = client_bq.load_table_from_uri(
                upload_uri, bq_table_uri, job_config=job_config
            )
            load_job.result()
        except Exception as e:
            # Loading from csv file into bigquery failed
            # The newly created bigquery table will be deleted
            Utilities.write_to_log("log.txt", "Could not load " + upload_uri)
            Utilities.write_to_log("log.txt", "EXCEPTION: " + str(e))
            client_bq.delete_table(bq_table_uri)
            return False

        # Returns True if loading the data into BigQuery succeeded
        return True

    @staticmethod
    def append_to_bigquery_table(target_table_id, temp_table_id, list_field_names):
        """Append new columns to an existing table in BigQuery.

        :param target_table_id: ID for the target table in BigQuery: e.g. your-project.your_dataset.your_table_name
        :type target_table_id: str

        :param temp_table_id: ID for the temporary table in BigQuery: e.g. your-project.your_dataset.your_table_name
        :type temp_table_id: str

        :param list_field_names: Names for new field(s)
        :type list_field_names: list

        :return: True if succeeded, False if not
        :type: boolean
        """
        # Construct a BigQuery client object.
        client = bigquery.Client()

        try:
            # Gets the table. table_id == "your-project.your_dataset.your_table_name"
            table = client.get_table(target_table_id)  # Make an API request.

            # Updates the table schema
            original_schema = table.schema
            new_schema = original_schema[:]  # Copy of the original schema
            for field in list_field_names:
                bq_field = bigquery.SchemaField(field, 'FLOAT', mode='NULLABLE')

                if bq_field not in new_schema:
                    # Only adds the field if it does not exist
                    # If the field does exist, the contents will be overwritten
                    new_schema.append(bq_field)

            # Adds the new fields
            table.schema = new_schema
            client.update_table(table, ["schema"])
        except Exception as e:
            # Could not update the schema of the table
            Utilities.write_to_log("log.txt", "Could not update the table schema")
            Utilities.write_to_log("log.txt", "EXCEPTION: " + str(e))
            return False

        try:
            # Performs a query to add the data to the new field
            for field in list_field_names:
                query_job = client.query(
                    "UPDATE " + target_table_id +
                    " a SET a." + field + " = b." +
                    field + " FROM " + temp_table_id +
                    " b WHERE a." + Default.LAT_FIELD + " = b."
                    + Default.LAT_FIELD +
                    " AND a." + Default.LON_FIELD +
                    " = b." + Default.LON_FIELD
                )
                query_job.result()
        except Exception as e:
            # Could not perform the query on the table
            Utilities.write_to_log("log.txt", "Could not perform the query")
            Utilities.write_to_log("log.txt", "EXCEPTION: " + str(e))
            return False

        return True


def run():
    print("run")
    """Downloads data from NASA POWER and stores it in BigQuery
        """
    skip_leading_rows = Default.SKIP_LEADING_ROWS  # Number of rows which will be skipped at the start of the file
    skip_trailing_rows = Default.SKIP_TRAILING_ROWS  # Number of rows at the enc of the file which will be skipped

    # Start and end dates
    start_y = 2007
    end_y = 2022
    start_m = 1
    end_m = 6
    start_d = 1
    end_d = 30

    # Google cloud platform
    client = storage.Client(project=Default.PROJECT_ID)
    bucket = client.bucket(Default.BUCKET_TEMP)
    client_bq = bigquery.Client()

    project = '--project{0}'.format(Default.PROJECT_ID)
    region = '--region={0}'.format(Default.REGION)
    temp_location = '--temp_location=gs://{0}/pipeline_temp/'.format(Default.BUCKET_TEMP)
    staging_location = '--staging_location=gs://{0}/pipeline_staging/'.format(Default.BUCKET_TEMP)
    # runner = '--runner={0}'.format('DirectRunner')
    runner = '--runner={0}'.format('DataFlowRunner')
    argv = [
        project,
        staging_location,
        temp_location,
        runner,
        region
    ]

    with beam.Pipeline(argv=argv) as p:
        print("beam")
        # Community: Renewable energy, sustainable buildings, or climatology
        for community in Default.NASA_POWER_COMMUNITY:
            # Period/temporal: Daily, monthly, or climatology
            for period in Default.NASA_POWER_TEMPORAL_AVE:
                # BigQery dataset (e.g. weather_daily, weather_monthly, or weather_climatology)
                bq_dataset = Utilities.get_bq_dataset(period)

                # Indices for columns in request contents from NASA POWER
                lat_index, lon_index, value_index = Utilities.get_request_content_indices(period)

                # Gets the list of datasets to loop through
                # Based on community and period
                list_datasets = Utilities.get_dataset_list(community, period)
                if community == 'AG':
                    # The agriculture community data can also be obtained using the renewable community.
                    # The advantage of this is data the RE community responds with lat, lon, year, month, day.
                    # This agrees with other data field schemas. AG responds with lat, lon, year, day-in-year
                    community = 'RE'

                if len(list_datasets) == 0:
                    # List datasets could not be determined, skip
                    continue

                # Performs requests on each dataset
                for dataset in list_datasets:
                    print("DATASET: " + dataset["name"])

                    dataset_key = dataset['key']
                    dataset_name = dataset['name']
                    # dataset_description = dataset['description']

                    # Gets a list of dates based on the start and end date
                    date_required, list_dates = Utilities.get_date_list(
                        period,
                        start_y,
                        end_y,
                        start_m,
                        end_m,
                        start_d,
                        end_d
                    )

                for date in list_dates:
                    list_field_names = []

                    # Table name which will be used for the BigQuery table
                    # and temporary CSV file
                    if period == Default.DAILY:
                        # Daily has years added because of the 10k column limit of BigQuery tables
                        table_name = '{}_{}_{}_{}_{}'.format(
                            dataset_name,
                            community,
                            period,
                            start_y,
                            end_y
                        )
                    else:
                        # Climatology and monthly will have much less than 10k columns
                        table_name = '{}_{}_{}'.format(
                            dataset_name,
                            community,
                            period
                        )
                    file_name = table_name + '.csv'

                    # Quick test to see of the BigQuery table exists
                    try:
                        client_bq.get_table(Default.PROJECT_ID + '.' + bq_dataset + '.' + table_name)
                        table_exist = True
                    except NotFound:
                        table_exist = False

                    with io.StringIO() as file_mem:
                        # Sets the dates
                        if date_required:
                            # Daily and yearly
                            start_date = date['start_date']
                            end_date = date['end_date']
                        else:
                            # Climatology period type does not require dates
                            start_date = ''
                            end_date = ''

                        if period != Default.CLIMATOLOGY:
                            # Climatology does not make use of dates
                            print("DATE: " + start_date + " TO " + end_date)

                        # Lat long will be added only once to a table
                        if not table_exist:
                            list_field_names.append(Default.LAT_FIELD)
                            list_field_names.append(Default.LON_FIELD)

                        # Adds fields to the list for the next dataset/date
                        list_field_names = Utilities.append_field_names(
                            list_field_names,
                            period,
                            dataset_name,
                            start_date,
                            end_date
                        )

                        for extent in Default.SA_GRID_EXTENTS:
                            # Extent of the tile
                            lat_min = extent["lat_min"]
                            lat_max = extent["lat_max"]
                            lon_min = extent["lon_min"]
                            lon_max = extent["lon_max"]

                            print("EXTENT: " + str(extent))

                            # Request link
                            if date_required:
                                # Dates required for daily and monthly
                                link = '{}/{}/regional?parameters={}&start={}&end={}&community={}&format={}&latitude-min={}&latitude-max={}&longitude-min={}&longitude-max={}'.format(
                                    Default.NASA_POWER_URL,
                                    period,
                                    dataset_key,
                                    start_date,
                                    end_date,
                                    community,
                                    Default.NASA_POWER_FORMAT,
                                    lat_min,
                                    lat_max,
                                    lon_min,
                                    lon_max
                                )
                            else:
                                # No date for climatology
                                link = '{}/{}/regional?parameters={}&community={}&format={}&latitude-min={}&latitude-max={}&longitude-min={}&longitude-max={}'.format(
                                    Default.NASA_POWER_URL,
                                    period,
                                    dataset_key,
                                    community,
                                    Default.NASA_POWER_FORMAT,
                                    lat_min,
                                    lat_max,
                                    lon_min,
                                    lon_max
                                )

                            success = False
                            max_requests = False
                            request_count = 0
                            # Performs the get request
                            while not success and not max_requests:
                                # NASA POWER will on occasion respond with errorenous content,
                                # or data could not be retrieved on their side. This is not a common issue, and
                                # performing another request should solve the problem. This will allow downloading
                                # to continue with no interruption.
                                success, content = Utilities.get_data(link)
                                request_count = request_count + 1

                                if not success:
                                    # If the request did not succeed, the script will wait for a time period
                                    # as the cause is likely from the minor
                                    time.sleep(Default.DEFAULT_SLEEP)
                                if request_count >= Default.MAX_REQUESTS:
                                    # This is done to avoid a permanent loop (e.g. NASA POWER is down)
                                    max_requests = True

                            if max_requests:
                                # The data could not be retrieved
                                # Print errors to the text file for later use or reruns
                                Utilities.write_to_log("date_skipped.txt", "\t\t\tDATASET: {}".format(
                                    dataset_name
                                ))
                                Utilities.write_to_log("date_skipped.txt", "\t\t\tMAX REQUESTS")
                                Utilities.write_to_log("date_skipped.txt", "\t\t\tDATE SKIPPED: {} TO {}".format(
                                    start_date,
                                    end_date
                                ))
                                # Closes the memory file
                                file_mem.close()
                                # Skip this date range and go to the next date range
                                break

                            # Newline not stored as '\n' character, so use r'\n'
                            split_content = str(content).split(r'\n')

                            # Removes unwanted lines at the start and end of the data
                            split_content = split_content[
                                            skip_leading_rows:(len(split_content) - skip_trailing_rows)]

                            if period == Default.DAILY:
                                split_content = Utilities.transform_daily_data(split_content)

                            for line in split_content:
                                # Latitude, longitude and value
                                line = line.replace('\n', '')
                                list_columns = line.split(',')

                                # A check required only for climatology
                                if period == Default.CLIMATOLOGY:
                                    # This test is only required for climatology.
                                    # Climatology has a last row which equals '\\r'
                                    # This row (or any other) will be ignored/skipped
                                    if len(list_columns) < 15:
                                        continue

                                if period == Default.DAILY:
                                    # Transformtion has been done for daily
                                    write_to_mem = line
                                elif period == Default.MONTHLY:
                                    # Lat, lon, all months, and average monthly
                                    write_to_mem = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
                                        list_columns[lat_index],
                                        list_columns[lon_index],
                                        list_columns[value_index[0]],
                                        list_columns[value_index[1]],
                                        list_columns[value_index[2]],
                                        list_columns[value_index[3]],
                                        list_columns[value_index[4]],
                                        list_columns[value_index[5]],
                                        list_columns[value_index[6]],
                                        list_columns[value_index[7]],
                                        list_columns[value_index[8]],
                                        list_columns[value_index[9]],
                                        list_columns[value_index[10]],
                                        list_columns[value_index[11]],
                                        list_columns[value_index[12]]
                                    )
                                else:
                                    # Climatology
                                    write_to_mem = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
                                        list_columns[lat_index],
                                        list_columns[lon_index],
                                        list_columns[value_index[0]],
                                        list_columns[value_index[1]],
                                        list_columns[value_index[2]],
                                        list_columns[value_index[3]],
                                        list_columns[value_index[4]],
                                        list_columns[value_index[5]],
                                        list_columns[value_index[6]],
                                        list_columns[value_index[7]],
                                        list_columns[value_index[8]],
                                        list_columns[value_index[9]],
                                        list_columns[value_index[10]],
                                        list_columns[value_index[11]],
                                        list_columns[value_index[12]]
                                    )

                                file_mem.write(write_to_mem)
                                file_mem.write('\n')

                            data_in_mem = file_mem.getvalue()
                            data_in_mem = data_in_mem[:len(data_in_mem) - 1]
                            csv_upload_success = Utilities.load_csv_into_bucket(
                                Default.BUCKET_TEMP,
                                data_in_mem,
                                file_name)

                            if not csv_upload_success:
                                # Print errors to the text file for later use or reruns
                                print("\t\t\tDATASET: {}".format(
                                    dataset_name
                                ))
                                print("\t\t\tMAX REQUESTS")
                                print("\t\t\tDATE SKIPPED: {} TO {}".format(
                                    start_date,
                                    end_date
                                ))
                                # Closes the memory file
                                file_mem.close()
                                # Skip this date range and go to the next date range
                                break

                                # Temporary CSV file URI and BigQuery table URI
                            upload_uri = 'gs://' + Default.BUCKET_TEMP + '/' + file_name
                            bq_table_uri = Default.PROJECT_ID + '.' + bq_dataset + '.' + table_name

                            bq_upload_success = False
                            if not table_exist:
                                # Create new table as it does not exist
                                print("CREATING TABLE")

                                schema = []
                                for field in list_field_names:
                                    bq_field = bigquery.SchemaField(field, 'FLOAT', mode='NULLABLE')
                                    schema.append(bq_field)

                                bq_upload_success = Utilities.load_csv_into_bigquery(
                                    upload_uri,
                                    bq_table_uri,
                                    schema,
                                    skip_leading_rows=0)
                            else:
                                # Table exists, content will be appended as new columns
                                print("APPENDING")

                                schema = [
                                    bigquery.SchemaField(Default.LAT_FIELD, 'FLOAT', mode='NULLABLE'),
                                    bigquery.SchemaField(Default.LON_FIELD, 'FLOAT', mode='NULLABLE')
                                ]
                                for field in list_field_names:
                                    bq_field = bigquery.SchemaField(field, 'FLOAT', mode='NULLABLE')
                                    schema.append(bq_field)

                                # Creates a temporary table in BigQuery
                                # This table will be used to store the appending columns by making use of a query
                                bq_temp_table_uri = Default.PROJECT_ID + '.' + bq_dataset + '.temp_' + table_name
                                bq_temp_upload_success = Utilities.load_csv_into_bigquery(
                                    upload_uri,
                                    bq_temp_table_uri,
                                    schema,
                                    skip_leading_rows=0)

                                # Skip if previous step failed
                                if bq_temp_upload_success:
                                    # Appends to a BigQuery table using a query
                                    bq_upload_success = Utilities.append_to_bigquery_table(
                                        bq_table_uri,
                                        bq_temp_table_uri,
                                        list_field_names
                                    )

                                # Deletes the temporary table created in BigQuery
                                client_bq.delete_table(bq_temp_table_uri, not_found_ok=True)

                            # Removes the temporary CSV file stored in the bucket
                            bucket.delete_blob(file_name)

                            # If the table creation or field appending failed
                            if not bq_upload_success:
                                # Print errors to the text file for later use or reruns
                                print("\t\t\tDATASET: {}".format(
                                    dataset_name
                                ))
                                print("\t\t\tMAX REQUESTS")
                                print("\t\t\tDATE SKIPPED: {} TO {}".format(
                                    start_date,
                                    end_date
                                ))
                                # Closes the memory file
                                file_mem.close()
                                # Skip this date range and go to the next date range
                                break

                            # Closes the memory file when done with the current date
                            file_mem.close()

                            return

    print("done")


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    run()
