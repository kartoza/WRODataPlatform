import typing
import enum

WRO_ORG_NAME = 'wro'

ISO_TOPIC_CATEGOY_VOCABULARY_NAME: typing.Final[str] = "iso_topic_categories"

WRO_METADATA_FIELDS = [
    'email',
    'title',
    'name',
    'authors-0-author_name',
    'authors-0-author_surname',
    'authors-0-author_email',
    'authors-0-author_organization',
    'authors-0-author_department',
    'authors-0-contact_same_as_author',
    'contact_person-0-contact_name',
    'contact_person-0-contact_email',
    'contact_person-0-contact_orgnization',
    'contact_person-0-contact_department',
    'notes',
    'owner_org',
    'citation-0-citation_title',
    'citation-0-citation_date',
    'citation-0-citation_identifier',
    'did_author_or_contact_organization_collect_the_data',
    'data_collection_organization',
    'dataset_language',
    'publisher',
    'publication_date',
    'wrc_project_number',
    'license',
    'dataset_license_url',
    'keywords',
    'spatial',
    'wro_theme',
    'data_structure_category',
    'uploader_estimation_of_extent_of_processing',
    'data_classification',
    'data_reference_date-0-data_reference_date_from',
    'data_reference_date-0-data_reference_date_to',
    'alternative_identifier',
    'vertical_extent_datum',
    'minimum_maximum_extent-0-minimum_vertical_extent',
    'minimum_maximum_extent-0-maximum_vertical_extent',
    'tags-0-tag_name',
    'tags-0-tag_type',
    'agreement'
    ]

WRO_METADATA_REQUIRED_FIELDS = [
    'email',
    'title',
    'name',
    'authors-0-author_name',
    'contact_person-0-contact_name',
    'contact_person-0-contact_email',
    'notes',
    'owner_org',
    'data_collection_organization',
    'publisher',
    'publication_date',
    'license',
    'keywords',
    'spatial',
    'wro_theme',
    'data_structure_category',
    'uploader_estimation_of_extent_of_processing',
    'data_classification',
    'agreement'
]

PACKAGE_NON_EXTRAS_FIELDS = [
    'title',
    'name',
    'private',
    'author',
    'author_email',
    'maintainer',
    'maintainer_email',
    'license_id',
    'notes',
    'url',
    'version',
    'state',
    'type',
    'extras'
]

PROJECTION = {
    "32737": "UTM37S",
    "32733": "UTM33S",
    "32738": "UTM38S",
    "32734": "UTM34S",
    "32732": "UTM32S",
    "32735": "UTM35S",
    "32629": "UTM29N",
    "32731": "UTM31S",
    "32736": "UTM36S",
    "32739": "UTM39S",
    "32627": "UTM27N",
    "32740": "UTM40S",
    "32638": "UTM38N",
    "32609": "UTM09N",
    "32643": "UTM43N",
    "32630": "UTM30N",
    "32619": "UTM19N",
    "32751": "UTM51S",
    "32728": "UTM28S",
    "32724": "UTM24S",
    "32729": "UTM29S",
    "32621": "UTM21N",
    "32633": "UTM33N",
    "32628": "UTM28N",
    "32634": "UTM34N",
    "32730": "UTM30S",
    "32757": "UTM57S",
    "32727": "UTM27S",
    "32637": "UTM37N",
    "32631": "UTM31N",
    "32615": "UTM15N",
    "32752": "UTM52S",
    "32623": "UTM23N",
    "32635": "UTM35N",
    "32636": "UTM36N",
    "32750": "UTM50S",
    "32749": "UTM49S",
    "32632": "UTM32N",
    "32654": "UTM54N",
    "32613": "UTM13N",
    "32614": "UTM14N",
    "32617": "UTM17N",
    "32719": "UTM19S",
    "32626": "UTM26N",
    "32625": "UTM25N",
    "32624": "UTM24N",
    "32622": "UTM22N",
    "32745": "UTM45S",
    "32649": "UTM49N",
    "32718": "UTM18S",
    "32717": "UTM17S",
    "32754": "UTM54S",
    "32753": "UTM53S",
    "32640": "UTM40N",
    "32639": "UTM39N",
    "32723": "UTM23S",
    "32648": "UTM48N",
    "32760": "UTM60S",
    "32644": "UTM44N",
    "32748": "UTM48S",
    "32612": "UTM12N",
    "32755": "UTM55S",
    "32641": "UTM41N",
    "32652": "UTM52N",
    "32616": "UTM16N",
    "32646": "UTM46N",
    "32642": "UTM42N",
    "32610": "UTM10N",
    "32620": "UTM20N",
    "32618": "UTM18N",
    "32759": "UTM59S",
    "32720": "UTM20S",
    "32645": "UTM45N",
    "32650": "UTM50N",
    "32647": "UTM47N",
    "32722": "UTM22S",
    "32611": "UTM11N",
    "32651": "UTM51N",
    "32721": "UTM21S",
    "32653": "UTM53N",
    "32657": "UTM57N",
    "32608": "UTM08N",
    "32604": "UTM04N",
    "32758": "UTM58S",
    "32756": "UTM56S",
    "32655": "UTM55N",
    "32603": "UTM03N",
    "32605": "UTM05N",
    "4326": "Geographic WGS84",
    "900913": "Google Mercator",
    "0": "ORBIT"
}

ISO_TOPIC_CATEGORIES: typing.Final[typing.List[typing.Tuple[str, str]]] = [
    ("farming", "Farming"),
    ("biota", "Biota"),
    ("boundaries", "Boundaries"),
    ("climatologyMeteorologyAtmosphere", "Climatology, Meteorology, Atmosphere"),
    ("economy", "Economy"),
    ("elevation", "Elevation"),
    ("environment", "Environment"),
    ("geoscientificInformation", "Geoscientific Information"),
    ("health", "Health"),
    ("imageryBaseMapsEarthCover", "Imagery, Basemaps, Earth Cover"),
    ("intelligenceMilitary", "Intelligence, Millitary"),
    ("inlandWaters", "Inland Waters"),
    ("location", "Location"),
    ("oceans", "Oceans"),
    ("planningCadastre", "Planning, Cadastre"),
    ("society", "Society"),
    ("structure", "Structure"),
    ("transportation", "Transportation"),
    ("utilitiesCommuinication", "Utilities, Communication"),
]

class DatasetManagementActivityType(enum.Enum):
    REQUEST_MAINTENANCE = "requested dataset maintenance"
    REQUEST_PUBLICATION = "requested dataset publication"


#  id                | text                        |           | not null |
#  name              | character varying(100)      |           | not null |
#  title             | text                        |           |          |
#  version           | character varying(100)      |           |          |
#  url               | text                        |           |          |
#  notes             | text                        |           |          |
#  author            | text                        |           |          |
#  author_email      | text                        |           |          |
#  maintainer        | text                        |           |          |
#  maintainer_email  | text                        |           |          |
#  state             | text                        |           |          |
#  license_id        | text                        |           |          |
#  type              | text                        |           |          |
#  owner_org         | text                        |           |          |
#  private           | boolean                     |           |          | false
#  metadata_modified | timestamp without time zone |           |          |
#  creator_user_id   | text                        |           |          |
#  metadata_created  | timestamp without time zone |           |          |