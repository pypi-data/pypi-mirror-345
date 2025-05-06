from custom_base_django.functions.function_registry import registry

# @registry.register(
#     'calculate_sum',
#     description='Calculates sum of two numbers',
#     params={
#         'a': 'First number',
#         'b': 'Second number'
#     },
#     returns={'type': 'number', 'description': 'Sum of inputs'},
#     permission='authenticated'
# )
# def calculate_sum(a, b):
#     return a + b
#
# @registry.register(
#     'admin_task',
#     description='Admin only function',
#     permission='admin'
# )
# def admin_task():
#     return "This is an admin only task"