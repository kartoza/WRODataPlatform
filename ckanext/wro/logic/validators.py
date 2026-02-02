from json import tool
import logging
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import Missing
from ckantoolkit import get_validator

logger = logging.getLogger(__name__)
ignore_missing = get_validator('ignore_missing')
not_empty = get_validator('not_empty')

def conditional_date_reference_validator(key, flattened_data, errors, context):
    """
        changes the "required" value of some fields
        according to some conditional logic (e.g. 
        changes with other fields making the field
        not required anymore).
    """
    logger.debug('======================== iniside validator' , flattened_data)
    missing_str = "missing value, set data classification to static if there is no time frame"
    from_date_value = flattened_data[('data_reference_date', 0, 'data_reference_date_from')]
    to_date_value = flattened_data[('data_reference_date', 0, 'data_reference_date_to')] 
    
    try:
        data_classification = flattened_data[('data_classification',)]
        if data_classification == "static":
            return ignore_missing(key, flattened_data, errors, context)
        elif from_date_value == "" or to_date_value == "":
            raise toolkit.Invalid(missing_str)
            
    except KeyError:
        raise toolkit.Invalid(missing_str)


def author_same_as_contact(key, flattened_data, errors, context):
    """
        If the checkbox "contact_same_as_author" is checked:
        1. Make contact fields optional (ignore_missing)
        2. Copy author data to contact person fields

        Otherwise, contact fields are required.
    """
    logger.debug("======= from author_same_as_contact validator, data=", flattened_data)

    # Check if any author has contact_same_as_author checked
    contact_author_found = False
    author_index = None

    # Look through all authors to find one with contact_same_as_author checked
    for i in range(10):  # Support up to 10 authors
        try:
            checkbox_value = flattened_data.get(('authors', i, 'contact_same_as_author'))
            if checkbox_value and checkbox_value not in (False, toolkit.missing, '', 'False'):
                contact_author_found = True
                author_index = i
                break
        except (KeyError, TypeError):
            continue

    if not contact_author_found:
        return not_empty(key, flattened_data, errors, context)

    # Copy author data to contact person if checkbox is checked
    # Map author fields to contact fields
    field_mapping = {
        'author_name': 'contact_name',
        'author_email': 'contact_email',
        'author_organization': 'contact_orgnization',  # Note: typo in schema
        'author_department': 'contact_department',
    }

    # Get the current contact field being validated
    if len(key) >= 3:
        contact_field = key[2]  # e.g., 'contact_name', 'contact_email'
        contact_index = key[1]  # e.g., 0

        # Find the corresponding author field
        for author_field, contact_mapped in field_mapping.items():
            if contact_field == contact_mapped:
                author_value = flattened_data.get(('authors', author_index, author_field))
                if author_value and author_value != toolkit.missing:
                    # Set the contact field value from author
                    flattened_data[key] = author_value
                    return author_value
                break

    return ignore_missing(key, flattened_data, errors, context)


def author_or_contact_collected_data(key, flattened_data, errors, context):
    """
        checking if the contact or author
        collected the data, if not, the
        name of the collecting org should
        be provided.
    """
    author_or_contact_collected_data_checkbox = flattened_data[('did_author_or_contact_organization_collect_the_data',)]
    if author_or_contact_collected_data_checkbox == toolkit.missing or author_or_contact_collected_data_checkbox == False:
        return not_empty(key, flattened_data, errors, context)
    else:
        return ignore_missing(key, flattened_data, errors, context)

def agreement(value):
    """
        users must agree to continue form submission
    """
    if value == toolkit.missing:
        raise toolkit.Invalid("must be checked")
    else:
        return value
    

def lower_case(value) -> str:
    """
    Ensures the value contains only lowercase letters.
    If value is missing or None, skip validation by returning None.
    """
    if isinstance(value, Missing) or value is None:
        return None  # ✅ return None, not Missing

    if not isinstance(value, str):
        raise toolkit.Invalid("Value must be a string")

    for letter in value:
        if letter.isupper():
            raise toolkit.Invalid(
                f'format is alphabetical, all letters should be in lower cases. '
                f'Please use lower case instead of "{letter}".'
            )
    return value
