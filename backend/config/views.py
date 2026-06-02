from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health_check(request):
    return Response({
        "success": True,
        "message": "EOA API server is running.",
        "data": {
            "status": "ok"
        }
    })
