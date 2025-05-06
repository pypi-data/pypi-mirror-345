from inspect import signature
from functools import wraps


class FunctionRegistry:
    def __init__(self):
        self._functions = {}
        self._metadata = {}

    def register(self, name, **metadata):
        def decorator(func):
            # برای متدهای کلاس، اولین پارامتر (cls) را نادیده می‌گیریم
            sig = signature(func)
            parameters = {}
            required_params = []

            # پارامترهای تابع را پردازش می‌کنیم
            for i, (name_param, param) in enumerate(sig.parameters.items()):
                if i == 0 and name_param in ('cls', 'self'):
                    continue  # از پارامتر cls/self صرف نظر می‌کنیم

                parameters[name_param] = {
                    'type': param.annotation if param.annotation != param.empty else 'any',
                    'default': param.default if param.default != param.empty else None,
                    'description': metadata.get('params', {}).get(name_param, '')
                }
                if param.default == param.empty and not str(param).startswith('*'):
                    required_params.append(name_param)

            # ثبت تابع
            self._functions[name] = func
            self._metadata[name] = {
                'description': metadata.get('description', ''),
                'parameters': parameters,
                'required': required_params,
                'returns': metadata.get('returns', {}),
                'permission': metadata.get('permission', 'any'),
            }
            return func

        return decorator

    def get_function(self, name):
        """دریافت تابع ثبت شده"""
        return self._functions.get(name)

    def get_metadata(self, name=None):
        """دریافت متادیتای توابع"""
        if name:
            return self._metadata.get(name)
        return self._metadata

    def list_functions(self):
        """لیست تمام توابع ثبت شده"""
        return list(self._functions.keys())


# نمونه گلوبال از رجیستری
registry = FunctionRegistry()