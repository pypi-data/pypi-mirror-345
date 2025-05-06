import decimal
from datetime import date, datetime
from decimal import Decimal
from django.db import models
from django.db.models import QuerySet, Q
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (  # NOQA # isort:skip
    BooleanField, CharField, ChoiceField, DateField, DateTimeField, DecimalField,
    DictField, DurationField, EmailField, Field, FileField, FilePathField, FloatField,
    HiddenField, HStoreField, IPAddressField, ImageField, IntegerField, JSONField,
    ListField, ModelField, MultipleChoiceField, ReadOnlyField,
    RegexField, SerializerMethodField, SlugField, TimeField, URLField, UUIDField,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import as_serializer_error, raise_errors_on_nested_writes
from django.contrib.postgres.fields import ArrayField
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.utils import model_meta
from django.apps import apps

from custom_base_django.utils import model_fields_type_map, FreeField


class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'  # برای تنظیم تعداد آیتم‌ها در هر صفحه از طریق پارامتر URL
    max_page_size = 200


    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # تعداد کل آیتم‌ها
            'total_pages': self.page.paginator.num_pages,  # تعداد کل صفحات
            'current_page': self.page.number,  # شماره صفحه فعلی
            'next': self.get_next_link(),  # لینک صفحه بعدی
            'previous': self.get_previous_link(),  # لینک صفحه قبلی
            'results': data  # داده‌های صفحه فعلی
        })

class empty:
    pass


serializer_list = dict()

__all__ = ['DynamicFieldsModelSerializer', 'NesteSerializerDefinition', ]

class CustomDecimalField(DecimalField):
    def to_representation(self, value):
        return float(value)

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.to_internal_value(data)
        self.run_validators(value)
        return value


MAP = {
    "integer": 0,
    "float": 0.0,
    "char": "",
    "datetime": "2024-01-01",
    "boolean": False,
    }


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        ArrayField: ListField,
        models.JSONField: JSONField,
        models.AutoField: IntegerField,
        models.BigIntegerField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.CommaSeparatedIntegerField: CharField,
        models.DateField: DateField,
        models.DateTimeField: DateTimeField,
        models.DecimalField: CustomDecimalField,
        models.DurationField: DurationField,
        models.EmailField: EmailField,
        models.Field: ModelField,
        models.FileField: FileField,
        models.FloatField: FloatField,
        models.ImageField: ImageField,
        models.IntegerField: IntegerField,
        models.NullBooleanField: BooleanField,
        models.PositiveIntegerField: IntegerField,
        models.PositiveSmallIntegerField: IntegerField,
        models.SlugField: SlugField,
        models.SmallIntegerField: IntegerField,
        models.TextField: CharField,
        models.TimeField: TimeField,
        models.URLField: URLField,
        models.UUIDField: UUIDField,
        models.GenericIPAddressField: IPAddressField,
        models.FilePathField: FilePathField,
    }

    class BaseStruct:
        def __init__(self):
            self.nested = dict()
            self.nested_fields = dict()
            self.extra_non_required_fields = list()
            self.extra_writable_fields = list()
            self.readonly_fields = list()
            self.exclude_fields = list()
            self.extra_fields = list()
            self.extra_validations = list()
            self.blank_objects = dict()
            self.pk_field = None
            self.model = None
            self.must_save = True
            self.is_authenticated = False
            self.custom_query = dict()

            self.fields = None
            self.model = None

            self.with_nested = True
            self.include_metadata = True
            self.include_fks_str = True

        def to_dict(self):
            class_attrs = {attr: getattr(self.__class__, attr) for attr in dir(self.__class__) if
                           not attr.startswith("__")}
            instance_attrs = self.__dict__
            attrs = {attr: getattr(self, attr) for attr in {**class_attrs, **instance_attrs} if
                    attr not in ['to_dict', 'nested', 'fields']}
            return {**self.nested, **attrs}

    pagination_class = CustomPagination
    nested_fields = dict()
    extra_non_required_fields = list()
    extra_writable_fields = list()
    extra_fields = list()
    readonly_fields = list()
    exclude_fields = list()
    blank_objects = dict()
    pk_field = None
    model = None
    must_save = True
    is_authenticated = False
    custom_query = dict()

    def pre_get(self, *args, **kwargs):
        ...

    def past_get(self, *args, **kwargs):
        ...

    def pre_post(self, *args, **kwargs):
        ...

    def past_post(self, *args, **kwargs):
        ...

    extra_validations = list()

    @staticmethod
    def raise_validation_error(title="error", text="Some errors occurred!", code=1):
        raise ValidationError({title: text}, code=code)

    @classmethod
    def get_queryset(cls, view_obj, *args, **kwargs):
        queryset = cls.model.search_q(getattr(view_obj, 'search_q', ''), cls.custom_query, view_obj=view_obj)
        query_fields = queryset.get_query_fields() if hasattr(queryset, 'get_query_fields') else []
        func_filter = getattr(view_obj, 'get_dynamic_filters', None)
        queryset = queryset.filter(func_filter(query_fields)) if func_filter else queryset
        queryset = queryset.order_by(view_obj.order_by) if not queryset.ordered else queryset
        return queryset

    def _get_data(self, *args, **kwargs):
        self.pre_get(*args, **kwargs)
        self.res_data = self.data
        self.past_get(*args, **kwargs)
        return self.res_data

    @classmethod
    def get_json_response(cls, view_obj, *args, **kwargs):
        if view_obj.instance:
            serializer = cls(view_obj.instance, include_metadata=view_obj.include_metadata, view_obj=view_obj)
            data = serializer._get_data(*args, **kwargs)
            return JsonResponse(data)
        else:
            queryset = cls.get_queryset(view_obj, *args, **kwargs)
            cls.past_get(view_obj, *args, **kwargs)
            if cls.pagination_class and view_obj.request.GET.get('paginated', "true").lower() != 'false':
                paginator = cls.pagination_class()
                result_page = paginator.paginate_queryset(queryset, view_obj.request)
                serializer = cls(result_page, with_nested=False, include_metadata=False, include_fks_str=False, many=True, view_obj=view_obj)
                return paginator.get_paginated_response(serializer.data)
            else:
                serializer = cls(queryset, with_nested=False, include_metadata=False, include_fks_str=False, many=True, view_obj=view_obj)
                return JsonResponse(serializer.data, safe=False)

    @classmethod
    def post_json_data(cls, view_obj, *args, **kwargs):
        if view_obj.get_data:
            return cls.get_json_response(view_obj, *args, **kwargs)

        if view_obj.instance:
            view_obj.instance.view_obj = view_obj
            serializer = cls(view_obj.instance, data=view_obj.request.data, view_obj=view_obj)
        else:
            serializer = cls(data=view_obj.request.data, view_obj=view_obj)
        serializer.must_save = view_obj.must_save
        serializer.pre_post(*args, **kwargs)
        if serializer.is_valid():
            serializer.save()
            serializer.past_get(*args, **kwargs)
            cls.past_post(view_obj, *args, **kwargs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def __init_class__(self):
        if self.Meta.fields == '__all__':
            self.Meta.fields = [field for field in self.get_fields()]

        for field in self.fields:
            if isinstance(self.fields[field], serializers.ListSerializer):
                prop = getattr(self.model(), field)
                if prop is not None:
                    serializer_class = self.fields[field].child.__class__
                    if isinstance(prop, QuerySet):
                        self.__class__.nested_fields[field] = (None, None)
                        self.__class__.blank_objects[f'blank_{field}'] = serializer_class(serializer_class.model())
                    elif hasattr(prop, 'field'):
                        self.__class__.nested_fields[field] = (prop.field.name, prop.field.to_fields[0])# cache_name replace with name
                        self.__class__.blank_objects[f'blank_{field}'] = serializer_class(serializer_class.model())

        self.Meta.fields = self.Meta.fields + self.model.related_properties + self.model.related_meta_properties + ['navigation_instances']
        self.__class__.writable_fields = set(self.Meta.fields)

    def pop_some_fields(self):
        if not self.with_nested :#or (not getattr(self.instance, 'pk', None) and self.method == 'get'):
            for field in self.nested_fields.keys():
                self.fields.pop(field, None)

        if not self.include_metadata:
            fields = [field for field in self.fields]
            for field in fields:
                if field.__contains__("_meta_data"):
                    self.fields.pop(field, None)
            self.fields.pop('navigation_instances', None)

        if not self.include_fks_str:
            for field in self.model.related_properties:
                self.fields.pop(field, None)

    def __init__(self, *args, with_nested=None, include_metadata=None, include_fks_str=None, parent_field=None, view_obj=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.with_nested = self.with_nested if with_nested == None else with_nested
        self.include_metadata = self.include_metadata if include_metadata == None else include_metadata
        self.include_fks_str = self.include_fks_str if include_fks_str == None else include_fks_str
        self.view_obj = view_obj
        self.nested_datas = dict()
        self.nested_instances = dict()
        self.pop_some_fields()
        self.fields.get(self.pk_field).required = False

        # self.include_metadata = kwargs.pop('metadata', True)
        for field in self.exclude_fields:
            self.fields.pop(field, None)

        if parent_field:
            f = self.fields.get(parent_field)
            if f:
                f.read_only = True

        for field in self.extra_non_required_fields:
            f = self.fields.get(field)
            if f:
                f.required = False
                f.allow_blank = True
                f.allow_null = True

        for field in self.readonly_fields:
            f = self.fields.get(field)
            if f:
                f.read_only = True

        # for field in self.fields:
        #     if self.fields[field].read_only and self.model.has_setter(field):
        #         self.fields[field] = FreeField(required=False, read_only=False, allow_blank=True, allow_null=True)


        # if kwargs.get('data'):
        #     self.__nested_init__(**kwargs)

    def get_structure(self, required_only=False, required_status=False):
        fields = dict()
        for field in self.fields:
            if field in self.nested_fields:
                type_str = self.fields[field].child.get_structure(required_only, required_status)
            else:
                type_str = str(type(self.fields[field])).replace("<class 'rest_framework.fields.","").replace("Field'>","")
                type_str = type_str.replace("<class 'rest_framework.relations.PrimaryKeyRelated","f_key")
                type_str = type_str.replace("<class 'rest_framework.serializers.ListSerializer'>","dict")
                type_str = type_str.lower()
                type_str = type_str.replace("<class 'sepidar_api.serializers.customdecimal","float")
                type_str = MAP.get(type_str, type_str)
                if type_str == "f_key":
                    type_str = str(self.fields[field].queryset.model).lower()
                    type_str = type_str.split(".")[-1].replace("'>", "")
                    type_str = f"rel({type_str})"
            if required_only:
                if self.fields[field].required or field in self.nested_fields:
                    fields[field] = type_str
            else:
                if required_status and self.fields[field].required:
                    fields[field] = f"{type_str} (*)"
                else:
                    fields[field] = type_str

        return fields

    # تبدیل اطلاعات دیتا به اطلاعات معتبر منطبق بر فیلد های مدل. همچنین برخی پراپرتی ها که ستر دارند و در دیتا امده اند هم در دیتای ولید شده اضافه می شوند
    # def to_internal_value(self, data):
    #     try:
    #         value = super().to_internal_value(data)
    #         return value
    #     except Exception as e:
    #         raise e

    # بازنویسی به صورتی که نستد را ساپورت میکند و ابجکت جاری را برای نستد ها ست میکند. همچنین حالت سیو فالس را هم ساپورت میکند
    def save(self, **kwargs):
        # self.instance = super().save(**kwargs)
        if self.must_save:
            self.instance.save(**kwargs)
            for child_instance in self.child_instances_for_delete:
                child_instance.delete()
            for field in self.nested_fields:
                for child_serializer in self.child_serializers.get(field, []):
                    if self.nested_fields[field][0]:
                        if getattr(getattr(self.model,field), 'is_generic_relation', None):
                            extra_keys = getattr(self.instance, field).filters
                            for key, value in extra_keys.items():
                                setattr(child_serializer.instance, key, value)
                            setattr(child_serializer.instance, self.nested_fields[field][0], self.instance.pk)
                        else:
                            setattr(child_serializer.instance, self.nested_fields[field][0], self.instance)
                    child_serializer.save(**kwargs)
        return self.instance

    # برای ولیدیت کردن اطلاعات در سریالایزر در پست و پوت
    def run_validation(self, data=None):
        data = data or {}
        errors = {}

        try:
            for extra_validation in list(self.extra_validations):
                extra_validation(self, data=data)
            # self.Meta.model.extra_validation(instance=self.instance, data=data)
        except ValidationError as exc:
            errors.update({"extra_validation": as_serializer_error(exc)})

        self.nested_datas = dict()
        for field in self.nested_fields:
            self.nested_datas[field] = data.pop(field, None)

        if isinstance(data, dict):
            extra_fields = [key for key in self.readonly_fields if key in data.keys()]
            if extra_fields:
                errors.update({"data_structure":
                    f"""فیلدهای اضافی در پست: ({', '.join(extra_fields)})--- لیست فیلدهای مجاز:({', '.join(self.writable_fields)})"""})
        if (self.instance and data.get(self.pk_field) and self.instance.pk != data.get(self.pk_field)):
            errors.update({"pk_not_valid": "pk not valid for this request"})

        try:
            data = super().run_validation(data)
        except ValidationError as exc:
            data = {attr: value for attr, value in data.items()
                    if attr in (self.fields - self.nested_fields.keys() - set(self.readonly_fields))
                      and not (self.fields[attr].read_only and not self.model.has_setter(attr))
                    }
            errors.update({"details": as_serializer_error(exc)})

        try:
            self.instance = self.update_instance(data)
        except Exception as exc:
            errors.update({"save_errors": str(exc)})

        try:
            data = self.nested_run_validation(data)
        except ValidationError as exc:
            errors.update({"nested_data": as_serializer_error(exc)})
        if errors:
            raise ValidationError(errors)
        return data

    # برای حالت نستد تمام دیتاهای نستد را ولیدیت میکند و همچنین لیستی از سریالایزرهای نستد درست میکند که در زمان سیو به درد میخورد
    def nested_run_validation(self, data=None):
        errors = {}
        data = data or {}
        self.child_serializers = dict()
        self.nested_instances = dict()
        self.child_instances_for_delete = list()
        for field in self.nested_fields:
            nested_datas = self.nested_datas[field]
            if not nested_datas or self.fields[field].read_only:
                continue
            related_name = getattr(self.instance, field, None) if self.instance and self.instance.pk else None
            old_childes = related_name.all() if related_name else None
            child_serializer_class = self.fields[field].child.__class__
            child_pk_field = child_serializer_class.pk_field#self.nested_fields[field][1]
            child_pk_values = list()
            self.child_serializers[field] = list()
            i = 0
            for nested_data in nested_datas:
                nested_errors = {}
                parent_id = nested_data.get(self.nested_fields[field][0] or '_')
                if parent_id and (not self.instance or self.instance.pk != parent_id):
                    nested_errors.update({"invalid_parent_id": "parent id not valid for some nested items"})
                child_pk_value = nested_data.get(child_pk_field)
                if child_pk_value:
                    child_pk_values.append(child_pk_value)
                child_filter = Q(**{child_pk_field: child_pk_value or -1})
                child_instance = old_childes.filter(child_filter).first() if old_childes else None
                if child_pk_value and not child_instance:
                    nested_errors.update({"invalid_child_id": "This child not in previous childes!!"})
                nested_data.update({"_parent_": self.instance})
                child_serializer = child_serializer_class(instance=child_instance, data=nested_data)
                if self.nested_fields.get(field) and self.nested_fields[field][0]:
                    parent_field = child_serializer.fields.get(self.nested_fields[field][0])
                    if parent_field:
                        parent_field.required = False
                if child_serializer.is_valid():
                    self.child_serializers[field].append(child_serializer)
                else:
                    nested_errors.update({'validation': child_serializer._errors})
                if nested_errors:
                    list_nested_errors = errors.get(f"{field}", [])
                    list_nested_errors.append({f"{i}": nested_errors})
                    errors.update({f"{field}": list_nested_errors})
                i += 1
            if old_childes:
                self.child_instances_for_delete += [old_child for old_child in old_childes.exclude(**{f"{child_pk_field}__in": child_pk_values})]
        if errors:
            raise ValidationError(errors)
        return data

    # برای نمایس اطلاعات توسط سریالایزر در گت
    def to_representation(self, instance, **kwargs):
        #این متد در گت فراخوانی می شود
        # خذف متا دیتا در صورتی که در اینت سریالایزر متا را غیر فعال کرده باشیم (برای افزایش سرعت در گت لیست ایتم های دارای نستند
        if not self.include_metadata:
            fields = [field for field in self.fields]
            for field in fields:
                if field.__contains__("_meta_data"):
                    self.fields.pop(field, None)
            self.fields.pop('navigation_instances', None)
            for field in self.nested_fields.keys():
                _field = self.fields.get(field)
                if _field:
                    _field.child.include_metadata = False

        # حذف نستد ها در مواردی که ریلیتد نیم داریم و اینستن نداریم یا پرامری کی ندارد
        if not self.instance or (not isinstance(self.instance, list) and not getattr(self.instance,'pk', None)):
            for field in self.nested_fields.keys():
                if self.nested_fields[field][0]:
                    self.fields.pop(field, None)
        # سوپر متد اصلی
        data = super().to_representation(instance)
        # تغیر وضعیت رکواید بودن یا رید انلی بودن فیلدها در اطلاعات متا بر اساس تغییرات در سریالایزر
        if self.include_metadata:
            data['meta_datas'] = {}
            for field in self.fields:
                if field.__contains__("_meta_data"):
                    f = data.pop(field, None)
                    if f:
                        f_name = field.replace("_meta_data", "")
                        _field = self.fields.get(f_name)
                        if _field:
                            has_setter = not self.model.has_setter(f_name)
                            f.update({'read_only': _field.read_only and has_setter, 'required': _field.required})
                            data['meta_datas'][f_name] = f
                if self.nested_fields and field in self.nested_fields:
                    _field = self.fields.get(field)
                    data['meta_datas'][field] = {"type": "list",
                                                 "verbose_name": field,
                                                 "validators": [],
                                                 "field_type": "ListSerializer",
                                                 'required': _field.required,
                                                 'read_only': _field.read_only}
                if self.extra_fields and field in self.extra_fields:
                    _field = self.fields.get(field)
                    data['meta_datas'][field] = {"type": "other",
                                                 "verbose_name": field,
                                                 "validators": [],
                                                 "field_type": "Other",
                                                 'required': _field.required,
                                                 'read_only': _field.read_only}
                    # data['meta_datas'][field] = {"type": model_fields_type_map.get(type(field), "other"),
                    #                             "verbose_name": field.verbose_name,
                    #                             'required': field.null,
                    #                             "validators": [validator.__dict__ for validator in field.default_validators],
                    #                             "field_type": field.get_internal_type(),
                    #                             # "field_name": field.name
                    #                             }
            # اضافه کردن ابجکت های بلنک به دیتا
            data['blank_objects'] = dict()
            for key, value in self.blank_objects.items():
                key = key.replace('blank_', '')
                data['blank_objects'][key] = value.data

        #تغییر نوع داده در مواردی که کویری مستقیم میزنیم و اطلاعات دسیمال و دیت تایم به صورت ابجکت بر میکردند و باید رشته شوند که در سریالایزر خطا ایجاد نکند
        for field, value in data.items():
            if isinstance(value, (date, datetime)):
                data[field] = str(value)
            elif isinstance(value, Decimal):
                data[field] = float(value)
        pk = (self.instance.pk or 0) if self.instance else 0
        pk = pk or data.get(self.pk_field,0) or 0
        data['meta_datas'].update({"post_url": reverse('dynamic-api-detail',
                                                       kwargs={'pk': pk,
                                                               'model':f"{self.model._meta.app_label}-{self.model._meta.model_name}"})})

        return data

    # اطلاعات دیتا را در اینستن مقدار دهی میکنیم
    # def update_from_data(self, instance, data):
    #     for field in self.fields - self.nested_fields.keys() - set(self.readonly_fields):
    #         if self.fields[field].read_only and not self.instance.has_setter(field):
    #             continue
    #         value = data.get(field, 'NA')
    #         if not field == self.pk_field and value != 'NA':
    #             try:
    #                 setattr(instance, field, value)
    #             except Exception as e:
    #                 print(str(e))
    #     return instance

    # بر اساس اطلاعات دریافتی و مدل مرتبط اینتنس سریالایزر را مقدار دهی میکنیم
    def update_instance(self, data):
        if not self.instance:
            self.instance = self.model()
        # self.instance = self.update_from_data(self.instance, data)
        self.instance = self.update_instance_from_data(instance=self.instance, validated_data=data)
        return self.instance

    def update_instance_from_data(self, instance, validated_data):
        try:
            raise_errors_on_nested_writes('update', self, validated_data)
            info = model_meta.get_field_info(instance)
            m2m_fields = []

            for attr, value in validated_data.items():
                if attr in info.relations and info.relations[attr].to_many:
                    m2m_fields.append((attr, value))
                elif value and not isinstance(value, models.Model) and attr in info.relations and info.relations[attr].related_model:
                    related_model = info.relations[attr].related_model
                    # تبدیل ID به اینستنس مدل
                    value = related_model.objects.get(pk=value)

                setattr(instance, attr, value)

            for attr, value in m2m_fields:
                field = getattr(instance, attr)
                field.set(value)

            return instance
        except Exception as e:
            print(str(e))

    # def update_instance_from_data(self, instance, validated_data):
    #     raise_errors_on_nested_writes('update', self, validated_data)
    #     info = model_meta.get_field_info(instance)
    #     m2m_fields = []
    #     for attr, value in validated_data.items():
    #         if attr in info.relations and info.relations[attr].to_many:
    #             m2m_fields.append((attr, value))
    #         else:
    #             setattr(instance, attr, value)
    #     for attr, value in m2m_fields:
    #         field = getattr(instance, attr)
    #         field.set(value)
    #     return instance


class NesteSerializerDefinition:
    def __init__(self, serializer_class:DynamicFieldsModelSerializer, params=None):
        self.serializer_class = serializer_class
        self.params = params or {}