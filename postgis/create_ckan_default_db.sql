CREATE DATABASE ckan_default;
create user ckan_default with password 'ckan';
grant all privileges on database ckan_default to ckan_default;
