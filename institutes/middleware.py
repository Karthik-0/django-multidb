from django.db import connection, connections
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

from django.conf import settings

from institutes.models import Institute


class InstituteMiddleWare(MiddlewareMixin):
    TENANT_NOT_FOUND_EXCEPTION = Http404

    def hostname_from_request(self, request):
        """Extracts hostname from request. Used for custom requests filtering.
        By default removes the request's port and common prefixes.
        """
        return request.get_host().split(":")[0].lower()

    def get_db_settings_for_subdomain(self, hostname):
        domain_parts = hostname.split(".")
        subdomain = domain_parts[0]
        if subdomain.lower() == "www":
            subdomain = domain_parts[1]
        
        db_settings = cache.get(subdomain)
        if not db_settings:
            return None
        return db_settings

    def process_request(self, request):
        hostname = self.hostname_from_request(request)
        print("Host name : ", hostname)
        db_settings = self.get_db_settings_for_subdomain(hostname)
        if db_settings:
            settings.DATABASES["default"] = db_settings
        connection.set_schema_to_public()
        print(db_settings, Institute.objects.using("default").all(), connections.databases)
