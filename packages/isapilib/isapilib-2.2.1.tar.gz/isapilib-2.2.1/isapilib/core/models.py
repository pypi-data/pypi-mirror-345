from django.conf import settings
from django.db import models
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from isapilib.api.models import UserAPI  # noqa keep this


class DynamicManager(models.Manager):
    _alias = None

    def using(self, alias):
        self._alias = alias
        return super().using(alias)

    def get_queryset(self):
        queryset = super().get_queryset()

        if isinstance(queryset.model._meta.db_table, dict):
            version = settings.DATABASES[self._alias]['INTELISIS_VERSION']
            db_table_options = queryset.model._meta.db_table

            try:
                queryset.model._meta.db_table = db_table_options[version]
            except KeyError:
                raise Exception(f'El modelo {queryset.model} no tiene una tabla para la versión {version}')

        return queryset


class BaseModel(models.Model):
    objects = DynamicManager()

    def _add_field(self, name):
        new_field = models.TextField(db_column=name)
        new_field.contribute_to_class(self, name)

    def get(self, name):
        if name not in [field.attname for field in self._meta.get_fields()]:
            self._add_field(name)

        return getattr(self, name)

    def set(self, name, value):
        if name not in [field.attname for field in self._meta.get_fields()]:
            self._add_field(name)

        setattr(self, name, value)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        query = self.__class__.objects.filter(pk=self.pk)

        if self.pk and query.exists():
            fields = update_fields or [
                field.name for field in self._meta.fields
                if field.name != self._meta.pk.name and not isinstance(field, (models.AutoField, models.BigAutoField))
            ]
            values = {field: getattr(self, field) for field in fields}
            query.update(**values)
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True


class DummyForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def __get__(self, instance, cls=None):
        try:
            value = super().__get__(instance, cls)
        except self.field.remote_field.model.DoesNotExist:
            value = getattr(instance, self.field.get_attname())
        return value

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.field.remote_field.model._meta.concrete_model):
            setattr(instance, self.field.get_attname(), value)
            instance._state.fields_cache.pop(self.field.name, None)
        else:
            return super().__set__(instance, value)


class DummyForeignKey(models.ForeignKey):
    forward_related_accessor_class = DummyForwardManyToOneDescriptor
