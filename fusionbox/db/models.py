import os

from django.db import models


def generic_upload_to(instance, filename):
    """
    Generic `upload_to` function for models.FileField and models.ImageField
    which uploads files to `<app_label>/<module_name>/<file_name>`.
    """
    return os.path.join(instance._meta.app_label, instance._meta.module_name, filename)


class QuerySetManager(models.Manager):
    """
    http://djangosnippets.org/snippets/734/

    Easy extending of the base manager without needing to define multiple
    managers and queryset classes.

    Example Usage
    ::

        from django.db.models.query import QuerySet
        from fusionbox.db.models import QuerySetManager

        class Foo(models.Model):
            objects = QuerySetManager()
            class QuerySet(QuerySet):
                def published(self):
                    return self.filter(is_published=True)
    """
    use_for_related_fields = True

    def get_query_set(self):
        return self.model.QuerySet(self.model)

    def __getattr__(self, attr, *args):
        if attr.startswith('__') or attr == 'delete':
            raise AttributeError
        return getattr(self.get_query_set(), attr, *args)
