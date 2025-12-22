from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny , IsAuthenticated
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

User = get_user_model()


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] 

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user    

@login_required
def google_login_callback(request):
    user = request.user

    Social_accounts = SocialAccount.objects.filter(user=user)
    print("Social_accounts:", Social_accounts)

    social_account = Social_accounts.first()
    if not social_account:
        return redirect('http://localhost:5173/login/callback/?error=Nosocialaccountfound')


    token = SocialToken.objects.filter(account=social_account, account__provider='google').first()

    if token:
        print("Google Token:", token.token)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:5173/login/callback/?access_token={access_token}')
    else:
        return redirect('http://localhost:5173/login/callback/?error=Notokenfound')
    

@csrf_exempt
def validate_google_token(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                google_access_token = data.get('access_token')
                print("Received Google Access Token:", google_access_token)

                if not google_access_token:
                    return JsonResponse({'detail': 'Access token is required.'}, status=400)
                return JsonResponse({'detail': 'Token is valid.'}, status=200)
            except json.JSONDecodeError:
                return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
            return JsonResponse({'detail': 'Method not allowed.'}, status=405)  
        