from flask import request, Response, jsonify, Blueprint
from ckan.plugins import toolkit
from ckan.common import c
from ckan.logic import ValidationError
from ckan.lib.mailer import mail_user, MailerException
import xml.dom.minidom as dom
import logging
from datetime import datetime
from ..constants import (
    WRO_METADATA_REQUIRED_FIELDS as xml_minimum_set,
    WRO_METADATA_FIELDS as xml_full_set,
)
from xml.parsers.expat import ExpatError
from ..constants import PACKAGE_NON_EXTRAS_FIELDS

# About this Blueprint:
# -------------
# parsing xml file to extract info
# necessary to create a dataset,
# calls dataset create action.
# use it as root_url/dataset/xml_parser/

logger = logging.getLogger(__name__)

xml_parser_blueprint = Blueprint(
    "xml_parser",
    __name__,
    url_prefix="/dataset/xml_parser",
    template_folder="templates",
)

creator = ""


@xml_parser_blueprint.route("/", methods=["GET", "POST"])
def extract_files():
    """
    the blueprint allows for multiple
    files to be sent at once, extract
    each and call parse_xml_dataset.
    retutn success after all files
    parsed.
    """
    # files = request.files.to_dict()
    global creator
    creator = c.userobj
    xml_files = request.files.getlist("xml_dataset_files")
    # loggin the request files.
    logger.debug("from xml parser blueprint, the xmlfiles object should be:", xml_files)
    err_msgs = []
    info_msgs = []
    for xml_file in xml_files:
        check_result = check_file_fields(xml_file)
        if check_result is None:
            err_msgs.append(
                f'something went wrong during "{xml_file.filename}" dataset creation!'
            )
        if check_result["state"] == False:
            err_msgs.append(check_result["msg"])
        else:
            info_msgs.append(check_result["msg"])
    # aggregate messages
    if len(err_msgs) > 0:
        res = {"info_msgs": info_msgs, "err_msgs": err_msgs}
        send_email_to_creator(res)
        return jsonify({"response": res})

    else:
        # only when all packages are created
        res = {"info_msgs": info_msgs, "err_msgs": err_msgs}
        send_email_to_creator(res)
        return jsonify({"response": "all packages were created", "status": 200})


def check_file_fields(xml_file) -> dict:
    """
    performs different checks over
    the xml files.

    returns:
    -----
    object with status: False and a message
    or status:True.
    """
    root = None
    # has data check
    dataset = file_has_xml_dataset(xml_file)
    file_name_reference = xml_file.filename
    if dataset["state"]:
        root = dataset["root"]
    else:
        return dataset
    if root is not None:
        # return and object of the root
        root = return_object_root(root)
        # has field more than maximum set
        maximum_fields_check_ob = maximum_fields_check(root, file_name_reference)
        if maximum_fields_check_ob["state"] == False:
            return {"state": False, "msg": maximum_fields_check_ob["msg"]}
        # has field less than minimum set
        minimum_set_check_ob = minimum_set_check(root, file_name_reference)
        if minimum_set_check_ob["state"] == False:
            return {"state": False, "msg": minimum_set_check_ob["msg"]}
        root = handle_date_fields(root)
        return create_ckan_dataset(root)
        # things went ok
    else:
        return {"state": False, "msg": "something went wrong during dataset creation"}


def file_has_xml_dataset(xml_file):
    """
    parses a file,
    checks if file has a
    dataset and returns it.
    """
    try:
        dom_ob = dom.parse(xml_file)
    except ExpatError:
        """
        this happens when the file is
        completely empty without any tags
        """
        return {"state": False, "msg": f"file {xml_file.filename} is empty!"}

    root = dom_ob.firstChild
    if root.hasChildNodes():
        """
        this will cause the same problem as above
        """
        return {"state": True, "root": root}
    else:
        return {"state": False, "msg": f"file {xml_file.filename} is empty!"}


def return_object_root(root):
    """
    transform the xml dom
    root into an object of
    tag_name:tag_value
    """
    ob_root = {}
    for field in root.childNodes:
        if field.nodeType != 3:
            ob_root[field.tagName] = field.childNodes[0].data

    return ob_root


def maximum_fields_check(root_ob, file_name_reference: str):
    """
    checking if the provided field
    is more than the maximum set
    of EMC datasets fields.
    """
    root_ob_keys = root_ob.keys()
    for field in root_ob_keys:
        if field not in xml_full_set:
            return {
                "state": False,
                "msg": f'field "{field}" '
                + f'in the file "{file_name_reference}" is not within the '
                + "maximum set of allowed xml fields",
            }
    return {"state": True}


def minimum_set_check(root_ob: dict, file_name_reference: str):
    """
    checking if the xml file fields
    has the minimum required set.
    """
    # adding field "name" later dynamically
    for tag in xml_minimum_set:
        if tag not in root_ob:
            if tag != "name":
                msg = f'field "{tag}" is a required field, missed in file "{file_name_reference}"'
                return {"state": False, "msg": msg}
    return {"state": True}


def handle_date_fields(root_ob):
    """
    date fields need to be
    iso compliant in order
    to create the package,
    transform date strings
    to dates.
    """
    # date_fields = ["data_reference_date-0-data_reference_date_from", "data_reference_date-0-data_reference_date_to"]
    # for field in date_fields:
    #     iso_date_field = handle_date_field(root_ob[field])
    #     root_ob.update(iso_date_field)
    return root_ob


def create_ckan_dataset(root_ob):
    """
    create package via ckan api's
    package_create action.
    """
    logger.debug("from xml parser blueprint", root_ob)
    package_title = root_ob["title"]
    slug_url_field = change_slug_url_field(package_title)
    root_ob.update({"name": slug_url_field})
    root_ob.update({"type": "metadata-form"})
    root_ob = extra_fields(root_ob)
    # raise RuntimeError(root_ob)
    create_action = toolkit.get_action("package_create")
    try:
        create_action(data_dict=root_ob)
    except ValidationError as e:
        error_summary = e.__str__().replace("None","")
        error_summary = "" if error_summary is None else error_summary
        return {
            "state": False,
            "msg": f'error creating package "{package_title}": ' + error_summary,
        }
    return {"state": True, "msg": f'package "{package_title}" were created'}


def handle_date_field(date_field):
    """
    returns a date from iso-string
    YY-MM-DDTHH:MM:SS
    """
    iso_date = datetime.fromisoformat(date_field)
    return {date_field: iso_date}

def send_email_to_creator(res):
    """
    per issue #105 we need
    to send emails to creator
    for mail_user function
    check https://github.com/ckan/ckan/blob/master/ckan/lib/mailer.py
    """
    global creator
    msg_body = (
        "xml upload process completed, please navigate to the"
        + "following messages: \n"
    )
    created_packages_msgs = res["info_msgs"]
    error_packages_msgs = res["err_msgs"]
    msg_body += "created packages: \n"
    for msg in created_packages_msgs:
        msg_body += f"{msg} \n"
    msg_body += "packages with errors upon creation \n"
    for msg in error_packages_msgs:
        msg_body += f"{msg} \n"
    try:
        mail_user(creator, subject="creating dataset via xml upload", body=msg_body)
    except MailerException as e:
        return


def extra_fields(root_ob):
    """
    each dataset has key, value
    extra data attached, inserted
    into package_extra database.
    """
    #root_ob.update({"extras":[]})
    temp_ob = {}
    # for key in root_ob:
    #     if key not in PACKAGE_NON_EXTRAS_FIELDS:
    #         #root_ob["extras"].append({"key":key,"value":root_ob[key]})
    #         temp_ob.update({"key":key,"value":root_ob[key]})
    
    # raise RuntimeError(temp_ob)
    root_ob.update(root_ob)
    # these are the extra keys, remove them from the rest of the dataset 
    # keys = [key for key in root_ob.keys()] # deep copy
    # for key in keys:
    #     if key not in PACKAGE_NON_EXTRAS_FIELDS:
    #         root_ob.pop(key) 
    # raise RuntimeError("the root object:",root_ob)
    return root_ob

def change_slug_url_field(dataset_title):
    """
    ckan refuses url names 
    for datasets with special
    chars, removes those if any 
    """
    for item in dataset_title:
        if item in "!”#$%&'()*+,-./:;<=>?@[\]^_`{|}~.":
            dataset_title = dataset_title.replace(item, "")

    dataset_title = dataset_title.replace(" ", "-")
    return dataset_title
