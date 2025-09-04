import ckan.logic as logic
_get_action = logic.get_action
import ckan.plugins.toolkit as toolkit
import logging

logger = logging.getLogger(__name__)


@toolkit.chained_action
def package_create(original_action, context, data_dict):
    logger.warning(context)
    logger.warning(data_dict)
    return
    data_dict["type"] = "metadata-form"
    access = toolkit.check_access("package_create", context, data_dict)
    result = original_action(context, data_dict) if access else None
    return result


@toolkit.chained_action
def resource_create(original_action, context: dict, data_dict: dict) -> dict:
    model = context['model']
    user = context['user']
    logger.warning(context)
    logger.warning(data_dict)