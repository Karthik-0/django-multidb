# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from institutes.models import Institute



class Blog(models.Model):
    title = models.CharField(max_length=1024, db_index=True, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    institute = models.ForeignKey(Institute, null=True, blank=True)
