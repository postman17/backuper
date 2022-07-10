from django.urls import path

from backup.views import OauthCodeView, OauthCredsSucceedView


app_name = "backup"

urlpatterns = [
    path("oauth-code/", OauthCodeView.as_view(), name="oauth-code"),
    path("oauth-creds-succeed/", OauthCredsSucceedView.as_view(), name="oauth-code"),
]
