def test_link_resources():
    """
    the behavior when the reosurce
    is a link, just provide a link
    to the resource
    """
    pass

def test_cloud_path_exits_with_package():
    """
    if there is no cloud
    path with the parent
    package, we need a 
    flash message to update
    it
    """
    pass


def test_file_exits():
    """
    the user can remove files
    after being added, check
    that the file exists
    """
    pass

def test_resource_url():
    """
    check if the resource
    url has the correct 
    schecma,
    https://storage.cloud.google.com/'+container_name+'/'+resource_cloud_path+'/'+ pkg_name + "/" + full_name
    where:
    cloud_path: same as the package extra cloud path (must be lowered case)
    full_name: composed of resource name + '_id_' + resource id + extension
    """
    pass