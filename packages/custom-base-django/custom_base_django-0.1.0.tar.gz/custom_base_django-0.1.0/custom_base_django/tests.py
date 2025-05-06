# from django.test import TestCase

# Create your tests here.

class BaseStruct:
    nested_fields = dict()
    extra_non_required_fields = list()
    extra_writable_fields = list()
    readonly_fields = list()
    exclude_fields = list()
    blank_objects = dict()
    pk_field = None
    model = None
    must_save = True

    class Meta:
        fields = '__all__'
        model = None

    def to_dict(self):
        class_attrs = {attr: getattr(self.__class__, attr) for attr in dir(self.__class__) if
                       not attr.startswith("__") and getattr(self.__class__, attr) and attr != 'to_dict'}
        instance_attrs = self.__dict__
        return {**class_attrs, **instance_attrs}

b = BaseStruct()

def k(self,):
    super(self.__class__, self).kk()
    self.s = self.d * 50
class B():
    x=1

    def kk(self):
        self.v = 465

class AA:
    def __init__(self, x):
        self.x = 2*x

    def __get__(self, instance, owner):
        if not instance:
            ...
        return instance.k * self.x

class BB:
    k = 3
    a = AA(12)

print(BB().a)

X = type("A",(B,),{"d":1, "k": k})
x = X()
x.k()
b.Meta.model = BaseStruct
dict_  = b.to_dict()
print(dict_)