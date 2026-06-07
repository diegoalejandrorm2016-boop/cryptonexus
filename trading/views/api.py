from django.http import JsonResponse
from django.views.decorators.http import require_GET
import requests

BINANCE_BASE = 'https://api.binance.com/api/v3'

SUPPORTED_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT',
    'LTCUSDT', 'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'XLMUSDT', 'ETCUSDT',
]

INTERVAL_MAP = {
    '1d': ('1h', 24),
    '1w': ('4h', 42),
    '1m': ('1d', 30),
    '1y': ('1w', 52),
}


@require_GET
def api_prices(request):
    """Devuelve precios actuales de todas las criptos soportadas."""
    try:
        resp = requests.get(f'{BINANCE_BASE}/ticker/24hr', timeout=5)
        resp.raise_for_status()
        all_tickers = resp.json()
        data = [
            {
                'symbol': t['symbol'],
                'price': float(t['lastPrice']),
                'change': float(t['priceChangePercent']),
                'volume': float(t['quoteVolume']),
                'high': float(t['highPrice']),
                'low': float(t['lowPrice']),
            }
            for t in all_tickers
            if t['symbol'] in SUPPORTED_SYMBOLS
        ]
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def api_klines(request, symbol):
    """Devuelve velas OHLCV de Binance para el símbolo y período dados."""
    symbol = symbol.upper()
    if symbol not in SUPPORTED_SYMBOLS:
        return JsonResponse({'success': False, 'error': 'Símbolo no soportado.'}, status=400)

    period = request.GET.get('period', '1d')
    interval, limit = INTERVAL_MAP.get(period, ('1h', 24))

    try:
        resp = requests.get(
            f'{BINANCE_BASE}/klines',
            params={'symbol': symbol, 'interval': interval, 'limit': limit},
            timeout=5,
        )
        resp.raise_for_status()
        raw = resp.json()
        candles = [
            {
                'time': k[0],
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5]),
            }
            for k in raw
        ]
        return JsonResponse({'success': True, 'data': candles})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def api_price_single(request, symbol):
    """Devuelve el precio actual de un símbolo."""
    symbol = symbol.upper()
    if symbol not in SUPPORTED_SYMBOLS:
        return JsonResponse({'success': False, 'error': 'Símbolo no soportado.'}, status=400)
    try:
        resp = requests.get(f'{BINANCE_BASE}/ticker/price', params={'symbol': symbol}, timeout=5)
        resp.raise_for_status()
        return JsonResponse({'success': True, 'price': float(resp.json()['price'])})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
