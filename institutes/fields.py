from __future__ import absolute_import
import json
import six
import functools

import django

from django.core.exceptions import ValidationError
from django.db import models

try:
    from django.utils.encoding import smart_unicode as smart_text

    smart_text  # placate pyflakes
except ImportError:
    from django.utils.encoding import smart_text

# SubfieldBase causes RemovedInDjango110Warning in 1.8 and 1.9, and
# will not work in 1.10 or later
if django.VERSION[:2] >= (1, 8):
    field_metaclass = type
else:
    from django.db.models import SubfieldBase

    field_metaclass = SubfieldBase

field_class = functools.partial(six.with_metaclass, field_metaclass)


class JSONField(field_class(models.TextField)):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", {})
        super(JSONField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return {}
        value = value or "{}"
        if isinstance(value, six.binary_type):
            value = six.text_type(value, "utf-8")
        if isinstance(value, six.string_types):
            try:
                # with django 1.6 i have '"{}"' as default value here
                if value[0] == value[-1] == '"':
                    value = value[1:-1]

                return json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, six.string_types):
            super(JSONField, self).validate(value, model_instance)
            try:
                json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return json.dumps(value)
        except Exception as err:
            raise ValidationError(str(err))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_text(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        return self.get_prep_value(self._get_val_from_obj(obj))

    def deconstruct(self):
        name, path, args, kwargs = super(JSONField, self).deconstruct()

        if self.default != {}:
            kwargs["default"] = self.default

        return name, path, args, kwargs
