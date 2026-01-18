from django.urls import path
from .views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, MeView

app_name = 'authentication'

urlpatterns = [
    path('jwt/obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('me', MeView.as_view(), name='user_me'),
]
