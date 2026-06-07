from django.urls import path
from trading.views import (
    index_view,
    register_view, login_view, logout_view,
    dashboard_view, history_view,
    trade_view, buy_view, sell_view,
    api_prices, api_klines, api_price_single,
)

from trading.views.auth import profile_view

urlpatterns = [
    # Inicio
    path('', index_view, name='index'),

    # Auth (equivale a /auth/* en Flask)
    path('auth/register/', register_view, name='register'),
    path('auth/login/',    login_view,    name='login'),
    path('auth/logout/',   logout_view,   name='logout'),

    # Perfil
    path('dashboard/profile/', profile_view, name='profile'),

    # Dashboard
    path('dashboard/',         dashboard_view, name='dashboard'),
    path('dashboard/history/', history_view,   name='history'),

    # Trading
    path('trading/',      trade_view, name='trade'),
    path('trading/buy/',  buy_view,  name='buy'),
    path('trading/sell/', sell_view,  name='sell'),

    # API REST → Binance proxy
    path('api/prices/',                   api_prices,       name='api_prices'),
    path('api/price/<str:symbol>/',      api_price_single, name='api_price_single'),
    path('api/klines/<str:symbol>/',     api_klines,       name='api_klines'),
]

