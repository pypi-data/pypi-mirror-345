from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# from cus.function_registry import registry
import json
import logging
from django.http import JsonResponse
from custom_base_django.functions.function_registry import registry
from .permissions import HasFunctionPermission
from ..models.base import CustomManageFiscalDelete

logger = logging.getLogger(__name__)

def custom_serializer(obj):
    if isinstance(obj, datetime):
        # تبدیل datetime به رشته با فرمت ISO
        return obj.isoformat()
    if isinstance(obj, CustomManageFiscalDelete):
        return  obj.get_data()
    try:
        return str(obj)  # تلاش برای تبدیل به دیکشنری
    except AttributeError:
        raise TypeError(f"Type {type(obj)} not serializable")


class FunctionAPIView(APIView):
    permission_classes = [IsAuthenticated, HasFunctionPermission]
    registry = registry

    def post(self, request, function_name):
        func = self.registry.get_function(function_name)
        if not func:
            return Response(
                {'error': f'Function "{function_name}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        metadata = self.registry.get_metadata(function_name)
        missing_params = [
            p for p in metadata['required']
            if p not in data
        ]

        if missing_params:
            return Response(
                {
                    'error': 'Missing required parameters',
                    'missing': missing_params,
                    'required': metadata['required']
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"User {request.user.username} calling {function_name} with data: {data}")

        try:
            result = func(**data)
            logger.info(f"Function {function_name} executed successfully")
            return JsonResponse(json.loads(json.dumps({"result": result},  default=custom_serializer, ensure_ascii=False)))#json.dumps(data, default=str, ensure_ascii=False, indent=4))
        except Exception as e:
            logger.error(f"Error in {function_name}: {str(e)}", exc_info=True)
            return Response(
                {'errors': [str(e)]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FunctionMetadataView(APIView):
    registry = registry

    def get(self, request, function_name=None):
        if function_name:
            metadata = self.registry.get_metadata(function_name)
            if not metadata:
                return Response(
                    {'error': 'Function not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(metadata)
        else:
            return Response(self.registry.get_metadata())