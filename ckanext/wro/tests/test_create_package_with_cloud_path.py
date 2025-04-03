import pytest
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan import model

CORRECT_PACKAGE = {
    'email':"tester@email.com", 
    'title':"test package create", 
    'name':"test_package_create", 
    'authors-0-author_name':"tester",
    "authors-0-contact_same_as_author":True, 
    'notes':"unit testing dataset",
    'owner_org':"kartoza", 
    'did_author_or_contact_organization_collect_the_data':True, 
    'publisher':"no-limits publish", 
    'publication_date':"2022-08-16", 
    'license':"Open (Creative Commons)", 
    'keywords':"metadata", 
    'spatial':"-22.1265, 16.4699, -34.8212, 32.8931", 
    'wro_theme':"agriculture", 
    'data_structure_category':"structured", 
    'uploader_estimation_of_extent_of_processing':"raw", 
    'data_classification':"static", 
    'agreement':True
}

def test_create_package():
    """
    if the package is created
    correctly
    """
    pass

def test_package_extras():
    """
    if package extras
    exist with new
    packages
    """
    pass

def test_cloud_path():
    """
    if cloud path 
    exists with
    new packages
    """
    pass

def test_send_failure_flash_message():
    """
    tests if the system
    sends flash messages
    when package create
    fails
    """
    pass