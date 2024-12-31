from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            logout(request)
            response = Response(
                {'message': 'Successfully logged out'}, 
                status=status.HTTP_200_OK
            )
            response.delete_cookie('sessionid')
            response.delete_cookie('csrftoken')
            # If you store JWT in cookies, also add:
            # response.delete_cookie('jwt')
            return response
        except:
            return Response(
                {'error': 'Something went wrong'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
