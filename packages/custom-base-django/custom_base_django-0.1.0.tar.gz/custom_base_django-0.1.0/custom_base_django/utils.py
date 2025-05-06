from django.db.models import Q
from django.db import models
from django.conf import settings

from django.utils.timezone import now
from datetime import timedelta, datetime
from rest_framework.fields import CharField
import jdatetime

__all__ = ['Defaults', ]

from rest_framework.serializers import ListSerializer


class Defaults:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def now(self):
        time_delta_days = self.kwargs.get('time_delta_days', 0)
        return now() + timedelta(days=time_delta_days)#.strftime("%Y-%m-%d %H:%M")

    def object(self):
        try:
            model = self.kwargs.get('model', None)
            filters = self.kwargs.get('filters', {})
            return model.objects.filter(filters).first() if model else None
        except:
            return None


def get_variable_setting(variable_name, default):
    return getattr(settings, variable_name, default)


def get_all_subclasses(cls):
    subclasses = cls.__subclasses__()
    all_subclasses = []
    for subclass in subclasses:
        if not getattr(subclass._meta, 'abstract', False):
            all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


def q_to_dict(q_obj):
    result = {}
    for key, value in q_obj.children:
        if isinstance(value, Q):
            result[key] = q_to_dict(value)
        else:
            result[key] = value
    return result


model_fields_type_map ={models.CharField: "string", models.IntegerField: "int", models.DecimalField: "float",
                        models.FloatField: "float",
                        models.BooleanField: "bool", models.DateField: "date", models.DateTimeField: "date_time", list: "list", ListSerializer: "list"}


def get_meta_data(self, field_name):
    field = self._meta.get_field(field_name)
    res = {"type": model_fields_type_map.get(type(field), "other"), "verbose_name": field.verbose_name,
                'required': field.null,
                "validators": [validator.__dict__ for validator in field.default_validators],
                "field_type": field.get_internal_type(),
                # "field_name": field.name
           }
    if field.is_relation and field.related_model:
        model = field.related_model
        limit_to = field._limit_choices_to or {}
        objs = model.objects.filter(limit_to or Q())
        related_field = field.to_fields[0] or 'id'
        if not isinstance(limit_to, dict):
            limit_to = q_to_dict(limit_to)
        obj = getattr(self, field_name)
        if obj:
            res.update({"default": {"id": getattr(obj, related_field, None), "value": obj.get_data()}})
        else:
            res.update({"default": {"id": None, "value": None}})
        if objs.count() <= -1:
            res.update({"type": "list", "choice": [{"id": getattr(obj, related_field, None), "value": obj.get_data()} for obj in objs]})
        else:
            res.update({"type": "select_2", "url": f"/api2/{model._meta.app_label}-{model._meta.model_name}/?{'&'.join(f'{key}={value}' for key, value in limit_to.items())}"})
        res.update({"select_2_form": model.select_2_form})

    return res


def add_dynamic_property():
    from .models.base import BaseModelFiscalDelete as Model
    all_subclasses = get_all_subclasses(Model)
    for cls in all_subclasses:
        def make_str_property(f):
            def get_str(obj):
                f_obj = getattr(obj, f.name)
                return f_obj.__str__() if f_obj else None
            return property(lambda self: get_str(self))#getattr(self, f.name).__str__() if getattr(self, f.name) else None)

        def make_meta_data_property(f):
            return property(lambda self: get_meta_data(self, f.name))

        setattr(cls, 'related_properties', list())
        setattr(cls, 'related_meta_properties', list())
        setattr(cls, 'f_key_fields', list())
        for field in cls._meta.fields:
            # field meta_data
            property_name = f"{field.name}_meta_data"
            setattr(cls, property_name, make_meta_data_property(field))
            cls.related_meta_properties.append(property_name)

            if field.is_relation and field.related_model in all_subclasses:
                property_name = f"{field.name}_str"
                setattr(cls, property_name, make_str_property(field))
                cls.related_properties.append(property_name)
                cls.f_key_fields.append(field.name)

        cls.get_search_fields_lookup(depth=0)


def get_date(date_str, from_calendar="jalali"):
    if from_calendar.lower() == "jalali":
        year, month, day = map(int, date_str.split('-'))
        return jdatetime.date(year, month, day).togregorian()
    else:
        return datetime.strptime(date_str, "%Y-%m-%d")



def filter_json_to_Q(json):
    if not json.get("filters"):
        return Q(**json)
    filters_json = json.get("filters")
    filters_q = Q()
    for key, value in filters_json.get('conditions', {}).items():
        if filters_json.get('operator', '&'):
            filters_q &= filter_json_to_Q({key: value})
        elif filters_json.get('operator', '|'):
            filters_q |= filter_json_to_Q({key: value})
    return filters_q


class FreeField(CharField):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value