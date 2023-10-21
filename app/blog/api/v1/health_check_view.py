"""
Sample view for checking the healthy of CICD instruction.
"""
from rest_framework import (
    views,
    status,
    response
)


class HealthCheckApiView(views.APIView):
    """Sample class for checking whether
    the CICD works correctly or not."""
    def get(self, request, *args, **kwargs):
        return response.Response({
            'detail': 'DONE'
        }, status=status.HTTP_200_OK)
