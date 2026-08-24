from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.service import run_service


class MonitoringDashboardView(APIView):

    def post(self, request):

        result = run_service(request.data)

        return Response(result)