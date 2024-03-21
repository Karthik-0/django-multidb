# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six as six

from django.db import models
from tenant_schemas.models import TenantMixin

from institutes.fields import JSONField


@six.python_2_unicode_compatible
class Institute(TenantMixin):
    name = models.CharField("Name", blank=False, max_length=255)
    subdomain = models.CharField(max_length=255, blank=False, unique=True)
    db_settings = JSONField("DB Settings", blank=False, null=False)

    def __str__(self):
        return self.name