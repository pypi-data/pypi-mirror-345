import re

from click.core import F
from django.db import models
from django.db.models import QuerySet, Q
from django.db.models.expressions import RawSQL
from django.db.models.sql import Query
from django.db.models.sql.datastructures import BaseTable
from rest_framework.exceptions import ValidationError


from rest_framework import serializers
from ..serializers import NesteSerializerDefinition, DynamicFieldsModelSerializer
from ..utils import FreeField
from ..utils import Defaults
"""
    این فایل شامل کلاس‌ها و توابعی است که برای تعریف مدل‌های داده در جنگو استفاده می‌شوند.
    این کلاس‌ها و توابع امکانات مختلفی را برای مدیریت داده‌ها، فیلتر کردن، مرتب‌سازی، و اعتبارسنجی فراهم می‌کنند.

    کلاس‌های اصلی:
    - CustomQuerySet: کلاس کوئری‌ست سفارشی برای فیلتر کردن و مرتب‌سازی داده‌ها.
    - CustomRelatedNameManager: کلاس منیجر سفارشی برای مدیریت روابط بین مدل‌ها.
    - BaseModelFiscalDelete: کلاس مدل پایه برای مدل‌هایی که حذف فیزیکی ندارند.
    - BaseModelWitDateNotFiscalDelete: کلاس مدل پایه برای مدل‌هایی که حذف فیزیکی ندارند و دارای فیلدهای تاریخ ایجاد و به‌روزرسانی هستند.
    - BaseModelNotFiscalDelete: کلاس مدل پایه برای مدل‌هایی که حذف فیزیکی ندارند.
"""
__all__ = ['CustomQuerySet', 'CustomRelatedNameManager',
           'BaseModelFiscalDelete', 'BaseModelWitDateNotFiscalDelete', 'BaseModelNotFiscalDelete','CustomGenericRelation']


class CustomRelatedNameManager:
    def __init__(self, related_name, filter_kwargs=None, orders=None, function=None, qs_item_count=None):
        self.related_name = related_name
        self.filter_kwargs = filter_kwargs or {}
        self.orders = orders or []
        self.function = function
        self.field = None
        self.manager = None
        self.qs_item_count = qs_item_count

    def resolve_related_metadata(self, instance):
        if self.field is not None:
            return
        related_name = getattr(instance, self.related_name) #or getattr(instance.__class__, self.related_name, None)
        if related_name:
            self.field = related_name.field
            self.manager = related_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        self.resolve_related_metadata(instance)
        if not self.manager or not instance.pk:
            return self
        related_name = getattr(instance, self.related_name)
        # related_name = self.manager
        filters = {
            key: (getattr(instance, value.split('.')[1], None) if len(value.split('.')) > 1 else instance) if str(
                value).__contains__('self') else value for key, value in self.filter_kwargs.items() if
            not (isinstance(value, list) and len(value) == 2 and not eval(value[0].replace("self", "instance")))}
        if self.function:
            related_name = self.function(related_name, obj=self, instance=instance)
        queryset = related_name.filter(**filters).order_by(*self.orders) if self.orders else related_name.filter(**filters)
        if self.qs_item_count:
            limited_queryset = queryset[:self.qs_item_count]
            queryset = queryset.filter(pk__in=[item.pk for item in limited_queryset])
        return queryset


class CustomGenericRelation:
    def __init__(self, generic_model, to_field, filter_kwargs=None, orders=None, function=None, qs_item_count=None):
        self.filter_kwargs = filter_kwargs or {}
        self.orders = orders or []
        self.function = function
        self.field = generic_model._meta.get_field(to_field)
        self.manager = generic_model.objects
        self.is_generic_relation = True
        self.qs_item_count = qs_item_count

    def resolve_related_metadata(self, instance):
        setattr(self.field, 'to_fields', [instance._meta.pk.name])
        ...
        # if self.field is not None:
        #     return
        # self.field = related_name.field
        # self.manager = related_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        self.resolve_related_metadata(instance)
        if not self.manager or not instance.pk:
            return self
        related_name = self.manager
        filters = {
            key: (getattr(instance, value.split('.')[1], None) if len(value.split('.')) > 1 else instance) if str(
                value).__contains__('self') else value for key, value in self.filter_kwargs.items() if
            not (isinstance(value, list) and len(value) == 2 and not eval(value[0].replace("self", "instance")))}
        if self.function:
            related_name = self.function(related_name, obj=self, instance=instance)
        filters.update({self.field.name: instance.pk})
        queryset = related_name.filter(**filters).order_by(*self.orders) if self.orders else related_name.filter(**filters)
        if self.qs_item_count:
            limited_queryset = queryset[:self.qs_item_count]
            queryset = queryset.filter(pk__in=[item.pk for item in limited_queryset])

        queryset.filters = filters
        return queryset


class CustomBaseTable(BaseTable):
    def __init__(self, table_name, alias):
        super().__init__('custom_table', alias)

    def as_sql(self, compiler, connection):
        base, params = super().as_sql(compiler, connection)
        return f"({compiler.row_query}) custom_table", params


class CustomQuery(Query):
    row_query = None
    base_table_class = CustomBaseTable

    def __init__(self, model, row_query=None, with_sql_commands=''):
        super().__init__(model)
        self.row_query = row_query
        self.with_sql_commands = with_sql_commands

    def __compiler_as_sql(self, with_limits=True, with_col_aliases=False):
        final_sql, params = self.as_sql0(with_limits=with_limits, with_col_aliases=with_col_aliases)

        if final_sql.startswith("SELECT"):
            final_sql = f'''--with_start
{self.with_sql_commands}
--with_end 
{final_sql}'''

        matches = list(re.finditer(r"--with_start(.*?)--with_end", final_sql, re.DOTALL))
        if matches:
            first_match_end = matches[0].end()
            final_sql = final_sql[:first_match_end] + re.sub(r"--with_start(.*?)--with_end", "",
                                                             final_sql[first_match_end:],
                                                             flags=re.DOTALL)

        return final_sql, params

    def get_compiler(self, using=None, connection=None, elide_empty=True):
        compiler = super().get_compiler(using, connection, elide_empty)
        compiler.row_query = self.row_query
        self.as_sql0 = compiler.as_sql
        compiler.as_sql = self.__compiler_as_sql
        # self.compiler_ = compiler

        return compiler


class CustomQuerySet(models.QuerySet):
    def filter_active(self, is_active=True):
        return self.filter(is_active=is_active)

    def filter_by_publish(self):
        if getattr(self.model, 'publish'):
            return self.filter(publish=True)
        return self


class CustomManageFiscalDelete(models.Manager):
    def __init__(self):
        super().__init__()
        self._db = "default"
        self.queryset = None
        self._queryset_class = CustomQuerySet
        self._queryset_class.get_query_fields = self.get_query_fields

    def custom_raw(self, raw_query, with_sql_commands='', select_list=None, **params):
        if not select_list:
            select_list = []
        if isinstance(raw_query, str):
            raw_query = CustomQuery(self.model, raw_query, with_sql_commands)
            res = super().get_queryset()
            res.query = raw_query
        else:
            res = raw_query(**params)

        for select in select_list:
            if isinstance(select, (list, tuple)):
                res = res.annotate(**{select[0]: RawSQL(select[1], [])})
                # res = res.extra(select=select)
                # setattr(self.model, select.keys()[0], None)
            else:
                res = res.annotate(**{select: RawSQL(select, [])})
                # res = res.extra({f"{select}": select})
                # setattr(self.model, select, None)
        return res

    def get_queryset(self):
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints)

    @staticmethod
    def get_query_fields(self):
        if not getattr(self, 'query_fields', None):
            self.query_fields = [field.name for field in self.model._meta.get_fields()] + list(
                self.query.annotations.keys())
        return self.query_fields

    def filter_active(self, is_active=True):
        return self.get_queryset().filter_active(is_active=is_active)


class CustomManageNotFiscalDelete(CustomManageFiscalDelete):
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.model.get_queryset_all:
            qs = qs.filter(is_deleted=False)
        return qs


class Select2FormChoices(models.TextChoices):
    NONE = "None", "None"
    POPUP = "popup", "Popup"
    NEW_TAB = "new_tab", "New Tab"


class BaseModelFiscalDelete(models.Model):
    # برای مایگرت کردن دیتا
    migratable_data = False
    truncate_on_migrate_data = False
    # اگر این مدل در یک مدل دیگر به عنوان کلید خارجی باشد مشخص میکند که فرم اضافه کردن یا ویرایش سلکت 2 در فرانت چگونه باشد. پاپ آپ یا در صفحه جدید یا کلا قابل اضاف کردن نباشد
    select_2_form = Select2FormChoices.POPUP
    # کلاس سریالایزر پیش فرض را تعیین میکند
    SerializerBaseStruct = DynamicFieldsModelSerializer.BaseStruct
    # منیجر را تغییر می دهد
    objects = CustomManageFiscalDelete()

    extra_data_entity_type_name = None
    auto_numbers = []
    title = None
    related_properties = list()
    related_meta_properties = list()
    f_key_fields = list()
    readonly_fields = []
    NesteSerializerDefinition = NesteSerializerDefinition
    is_deleted = False
    get_queryset_all = False
    search_fields = []
    _search_fields_lookup = []
    default_struct = '__str__'
    child_annotate_field = None  # عنوان فیلدی از دیتابیس که به منظور ارجاع به این مدل (در مدلی که به این مدل کلید خارجی دارد) به صورت انوتیت در خروجی مورد استفاده قرار میگیرد

    is_active = models.BooleanField(default=True, verbose_name="is_active")

    @classmethod
    def get_search_fields_lookup(cls, depth=0):
        _search_fields_lookup = []
        if not cls.search_fields:
            cls.search_fields = []
            for field in cls._meta.fields:
                if (isinstance(field, (models.CharField, models.TextField, models.JSONField, models.URLField))
                        or (field.is_relation and field.related_model)
                        or field.primary_key):
                    cls.search_fields.append(field.name)

        for field_name in cls.search_fields:
            try:
                field = cls._meta.get_field(field_name)
                if field.is_relation and field.related_model:
                    if depth == 0:
                        model_class = field.related_model
                        search_fields_lookup = model_class.get_search_fields_lookup(depth=depth + 1).copy()
                        for search_field_lookup in search_fields_lookup:
                            _search_fields_lookup.append(f"{field_name}__{search_field_lookup}")
            except Exception as e:
                print(str(e))
            else:
                _search_fields_lookup.append(f"{field_name}__icontains")
        if depth == 0:
            cls._search_fields_lookup = _search_fields_lookup.copy()
        return _search_fields_lookup

    @classmethod
    def search_q(cls, q, custom_query=None, view_obj=None):
        filters = Q()
        if q:
            for search_field_lookup in cls._search_fields_lookup:
                filters |= Q(**{search_field_lookup: q})
        if custom_query:
            if q:
                for field in custom_query.get('select_list', {}):
                    filters |= Q(**{f"{field}__icontains": q})
            queryset = cls.objects.custom_raw(**custom_query, view_obj=view_obj)
        else:
            queryset = cls.objects
        return queryset.filter(filters)

    def add_child_annotate(self, queryset: QuerySet, parent_field: str) -> QuerySet:
        """
        :param queryset: کویری ست مرجع از مدلی که به این مدل کلید خارجی دارد
        :param parent_field: عنوان فیلدی از مدل بالا دست که به این مدل کلید خارجی در آن تعریف شده است
        :return: کویری ست را با فیلد رفرنس شده و به صورت parent_field_text بر میگرداند و به عبارتی یک فیلد با عنوان ترکیبی فیلد پرنت و تکست به کویری ست اضافه می شود
        """
        if self.child_annotate_field:
            return queryset.annotate(
                **{f'{parent_field}_text': RawSQL(f'{parent_field}__{self.child_annotate_field}', [])})
        return queryset

    @classmethod
    def has_setter(cls, prop_name):
        prop = getattr(cls, prop_name, None)
        if isinstance(prop, property):
            return prop.fset is not None  # چک می‌کنیم که setter وجود دارد یا نه
        return False

    @classmethod
    def get_model_fields(cls, method='get'):
        """
        Returns a list of field names for the given model,
        excluding related fields and unnecessary extras.
        """
        is_post = method.lower() == 'post'
        return [
            field.name
            for field in cls._meta.get_fields()
            # if not (field.is_relation or field.many_to_one or field.many_to_many or (is_post and field.editable))
            if not (getattr(field, 'related_name', None) or (is_post and field.editable))
        ]

    @classmethod
    def serializer_classes(cls):
        if not getattr(cls, '_serializer_classes', None):
            setattr(cls, '_serializer_classes', dict())
        return cls._serializer_classes

    @classmethod
    def serializer_name(cls, method: str, struct_name='default'):
        def first_upper(text: str):
            return f"{text[:1].upper()}{text[1:].lower()}"

        model_name = cls._meta.model_name
        app_label = cls._meta.app_label
        serializer_name = f'{first_upper(app_label)}{first_upper(model_name)}{first_upper(struct_name)}{first_upper(method)}Serializer'
        return serializer_name

    @classmethod
    def extra_validation(cls, instance=None, data=None, struct_name='default', **kwargs):
        # raise ValidationError(detail={"data_structure":"error text"}, code=10)
        return data

    def get_data(self, method='get', struct_name=None, include_metadata=False, with_nested=False):
        struct_name = struct_name or self.default_struct
        if struct_name == '__str__':
            return self.__str__()
        else:
            serializer_class = self.get_serializer(method, struct_name)
            return serializer_class(instance=self, include_metadata=include_metadata, with_nested=with_nested).data

    @classmethod
    def get_serializer(cls, method: str, struct_name='default', ):
        return cls._get_model_serializer(method, struct_name, )

    @classmethod
    def get_serializer_base_class(cls, struct_name='default', ):
        return cls.SerializerBaseStruct()

    @classmethod
    def _get_model_serializer(cls, method: str, struct_name, serializer_base_class=None):
        serializer_name = cls.serializer_name(method, struct_name)
        if serializer_name not in cls.serializer_classes().keys():
            cls.serializer_classes()[serializer_name] = cls.__get_model_serializer(method, serializer_name,
                                                                                   serializer_base_class)
        return cls.serializer_classes().get(serializer_name)

    @classmethod
    def __get_model_serializer(cls, method: str, serializer_name, serializer_base_class=None):
        def get_extra_fields(_fields, _nested_fields):
            if not _fields or _fields == '__all__':
                return {}
            model_fields = [f.name for f in cls._meta.get_fields()] +  (_nested_fields or [])
            extra_fields = []
            for field_name in _fields:
                if field_name not in model_fields:
                    extra_fields.append(field_name)

            fields_dict = {
                name: FreeField(required=False, read_only=False if cls.has_setter(name) else True, allow_blank=True, allow_null=True)
                for name in extra_fields
            }
            # for name in extra_fields:
            #     fields_dict[f'get_{name}'] = lambda self, obj, name=name: getattr(obj, name, None)
            return fields_dict

        if not serializer_base_class:
            serializer_base_class = cls.get_serializer_base_class()
        fields = serializer_base_class.fields
        if serializer_base_class.extra_fields or serializer_base_class.exclude_fields or serializer_base_class.readonly_fields:
            fields = fields or cls.get_model_fields()
            fields += serializer_base_class.extra_fields
        if fields and serializer_base_class.nested:
            fields = list(set(list(fields) + list(serializer_base_class.nested.keys())))

        serializer_base_class = serializer_base_class or cls.SerializerBaseStruct()
        # به روز کردن فیلدهای نستد به صورتی که فیلد پرنت در آنها حذف و اختیاری شود
        for field in serializer_base_class.nested:
            if isinstance(serializer_base_class.nested[field], cls.NesteSerializerDefinition):
                prop = getattr(cls(), field)
                params = serializer_base_class.nested[field].params
                if prop is not None:
                    if getattr(prop, 'field', None):
                        params.update({"parent_field": prop.field.name})
                params.update({"many": True})
                serializer_base_class.nested.update(
                    {field: serializer_base_class.nested[field].serializer_class(**params)})

        serializer_base_class.model = cls
        serializer_base_class.pk_field = cls._meta.pk.name
        serializer_base_class.extra_non_required_fields.append(cls._meta.pk)
        serializer_base_class.readonly_fields += cls.readonly_fields

        serializer_base_class.extra_non_required_fields += (cls.auto_numbers or []) + list(
            serializer_base_class.nested.keys())
        params = serializer_base_class.to_dict()
        Meta = type('Meta', (), {'model': cls, 'fields': fields if fields else '__all__'})
        params.update({'Meta': Meta})
        params.update(get_extra_fields(fields, list(serializer_base_class.nested.keys())))

        class_serializer = type(serializer_name, (DynamicFieldsModelSerializer,), params)
        serializer = class_serializer()
        serializer.__init_class__()
        return class_serializer


    @classmethod
    def raise_validation_error(cls, title="error", text="Some errors occurred!", code=1):
        raise ValidationError({title: text}, code=code)

    def __str__(self):
        title = self.title or getattr(self, 'full_name', '')
        code = getattr(self, 'code', '')
        code = f"(code: {code})" if code else ''
        number = getattr(self, 'number', '')
        number = f"(number: {number})" if number else ''
        address = getattr(self, 'address', '')
        address = f"(code: {address})" if address else ''
        return f"{title or code or number or address or ''}" or ''

    @property
    def navigation_instances(self):
        if self.pk:
            _first = self.__class__.objects.order_by('pk').first()
            _last = self.__class__.objects.order_by('pk').last()
            _previous = self.__class__.objects.filter(pk__lt=self.pk).order_by('pk').last()
            _next = self.__class__.objects.filter(pk__gt=self.pk).order_by('pk').first()
        else:
            _first = _last = _previous = _next = None
        return {
            "first": _first.pk if _first else None,
            "previous": _previous.pk if _previous else None,
            "self": self.pk,
            "next": _next.pk if _next else None,
            "last": _last.pk if _last else None,
        }

    def is_changed(self, compare_keys=None):
        if not self.pk:
            return True
        old_obj = self.__class__.objects.get(pk=self.pk)
        new, old = self.__dict__, old_obj.__dict__
        for k, v in new.items():
            if not compare_keys or k in compare_keys:
                try:
                    if v != old[k]:
                        return True
                except KeyError as e:
                    print(f'key error: {k} ', e.__traceback__.tb_lineno, e)
                    return True
                except TypeError as e:
                    print('TypeError: ', e.__traceback__.tb_lineno, e)
                    return True
        return False

    class Meta:
        abstract = True


class BaseModelNotFiscalDelete(BaseModelFiscalDelete):
    objects = CustomManageNotFiscalDelete()
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def hard_delete(self):
        super().delete()

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
            **kwargs
    ):
        if update_fields != ['is_deleted']:
            self.is_deleted = False
        super().save(*args,
                     force_insert,
                     force_update,
                     using,
                     update_fields)

    class Meta:
        abstract = True


class BaseModelWitDateNotFiscalDelete(BaseModelNotFiscalDelete):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    readonly_fields = ['created_at', 'updated_at']

    class Meta:
        abstract = True
