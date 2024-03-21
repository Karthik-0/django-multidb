import time
from django.db import close_old_connections, connection, connections
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

    def get_tenant_from_testpress_subdomain(self, request, hostname):
        try:
            domain_parts = hostname.split(".")
            subdomain = domain_parts[0]
            if subdomain.lower() == "www":
                subdomain = domain_parts[1]
            request.institute = request.tenant = Institute.objects.get(
                subdomain=subdomain
            )
            connection.set_tenant(request.tenant)
            return request.tenant
        except Institute.DoesNotExist:
            return None
        
    def process_request(self, request):
        hostname = self.hostname_from_request(request)
        db_settings = self.get_db_settings_for_subdomain(hostname)
        if db_settings:
            db_aliases = db_settings.keys()
            for key in connections.databases.keys():
                if key not in db_aliases:
                    del connections.databases[key]
    
            for key, value in db_settings.items():
                connections.databases[key].update(value)
            connection.close()
        connection.set_schema_to_public()
        if not self.get_tenant_from_testpress_subdomain(request, hostname):
            raise Exception("Tenant not found")
        
        
