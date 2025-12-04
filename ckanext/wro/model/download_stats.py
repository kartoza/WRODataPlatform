"""Download statistics tracking model."""
import datetime
from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ckan.model import meta, Package, Resource, User, domain_object


download_stats_table = Table(
    'wro_download_stats',
    meta.metadata,
    Column('id', String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column('resource_id', String(36), ForeignKey('resource.id'), nullable=False),
    Column('package_id', String(36), ForeignKey('package.id'), nullable=False),
    Column('user_id', String(36), ForeignKey('user.id'), nullable=True),
    Column('ip_address', String(45), nullable=True),
    Column('user_agent', String(500), nullable=True),
    Column('downloaded_at', DateTime, default=datetime.datetime.utcnow),
)


class DownloadStats(domain_object.DomainObject):
    """Download statistics for resources."""

    @classmethod
    def log_download(cls, resource_id, package_id, user_id=None, ip_address=None, user_agent=None):
        """Log a download event."""
        import uuid

        download = cls()
        download.id = str(uuid.uuid4())
        download.resource_id = resource_id
        download.package_id = package_id
        download.user_id = user_id
        download.ip_address = ip_address
        download.user_agent = user_agent
        download.downloaded_at = datetime.datetime.utcnow()

        meta.Session.add(download)
        meta.Session.commit()

        return download

    @classmethod
    def get_resource_download_count(cls, resource_id):
        """Get total downloads for a resource."""
        return meta.Session.query(cls).filter_by(resource_id=resource_id).count()

    @classmethod
    def get_package_download_count(cls, package_id):
        """Get total downloads for all resources in a package."""
        return meta.Session.query(cls).filter_by(package_id=package_id).count()


meta.mapper(DownloadStats, download_stats_table)
