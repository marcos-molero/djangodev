from django.urls import path
from sesion.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
handler404 = 'ws.views.custom_404_view'
handler500 = 'ws.views.custom_500_view'