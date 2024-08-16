from django.urls import path
from .views import AllRafflesView, RaffleView, ParticipateView, WinnersView, VerifyTicketView
from . import views


urlpatterns = [
    path('', views.AllRafflesView.as_view()),
    path('raffles/', AllRafflesView.as_view()),
    path('raffles/<uuid:id>/', RaffleView.as_view()),
    path('raffles/<uuid:id>/participate/', ParticipateView.as_view()),
    path('raffles/<uuid:id>/winners/', WinnersView.as_view()),
    path('raffles/<uuid:id>/verify-ticket/', VerifyTicketView.as_view()),
]