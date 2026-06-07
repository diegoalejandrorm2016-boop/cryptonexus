from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from decimal import Decimal
import requests

from trading.models import Portfolio, Transaction
from trading.utils.email import send_trade_email

BINANCE_BASE = 'https://api.binance.com/api/v3'

SUPPORTED_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT',
    'LTCUSDT', 'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'XLMUSDT', 'ETCUSDT',
]


def _get_price(symbol: str) -> float | None:
    try:
        resp = requests.get(f'{BINANCE_BASE}/ticker/price', params={'symbol': symbol}, timeout=5)
        if resp.ok:
            return float(resp.json()['price'])
    except Exception:
        pass
    return None


@login_required
def trade_view(request):
    symbol = request.GET.get('symbol', 'BTCUSDT').upper()
    if symbol not in SUPPORTED_SYMBOLS:
        symbol = 'BTCUSDT'

    price = _get_price(symbol)

    # Posición actual del usuario en esa cripto
    try:
        position = Portfolio.objects.get(user=request.user, symbol=symbol)
        position_qty = float(position.quantity)
    except Portfolio.DoesNotExist:
        position_qty = 0.0

    context = {
        'symbol': symbol,
        'price': price,
        'symbols': SUPPORTED_SYMBOLS,
        'balance': float(request.user.balance),
        'position_qty': position_qty,
        'periods': {'1d': '1D', '1w': '1S', '1m': '1M', '1y': '1A'},
        'pct_options': [25, 50, 75, 100],
    }
    return render(request, 'trading/trade.html', context)


@login_required
def buy_view(request):
    if request.method != 'POST':
        return redirect('trade')

    symbol = request.POST.get('symbol', '').upper()
    try:
        amount_usd = Decimal(request.POST.get('amount', '0'))
    except Exception:
        messages.error(request, 'Cantidad inválida.')
        return redirect(f'/trading/?symbol={symbol}')

    if symbol not in SUPPORTED_SYMBOLS or amount_usd <= 0:
        messages.error(request, 'Datos de compra inválidos.')
        return redirect('trade')

    price = _get_price(symbol)
    if not price:
        messages.error(request, 'No se pudo obtener el precio. Intenta de nuevo.')
        return redirect(f'/trading/?symbol={symbol}')

    price_decimal = Decimal(str(price))

    if amount_usd > request.user.balance:
        messages.error(request, f'Saldo insuficiente. Tienes ${request.user.balance:.2f} USD.')
        return redirect(f'/trading/?symbol={symbol}')

    quantity = amount_usd / price_decimal

    # Actualizar balance
    request.user.balance -= amount_usd
    request.user.save(update_fields=['balance'])

    # Actualizar portafolio (precio promedio ponderado)
    portfolio, created = Portfolio.objects.get_or_create(
        user=request.user, symbol=symbol,
        defaults={'quantity': 0, 'avg_buy_price': 0}
    )
    old_qty = portfolio.quantity
    old_avg = portfolio.avg_buy_price
    new_qty = old_qty + quantity
    portfolio.avg_buy_price = ((old_qty * old_avg) + (quantity * price_decimal)) / new_qty
    portfolio.quantity = new_qty
    portfolio.save()

    # Registrar transacción
    tx = Transaction.objects.create(
        user=request.user,
        type=Transaction.BUY,
        symbol=symbol,
        quantity=quantity,
        price=price_decimal,
        total=amount_usd,
    )

    # Enviar email
    send_trade_email(request.user, tx)

    messages.success(
        request,
        f'✅ Compraste {float(quantity):.6f} {symbol} a ${price:,.2f} USD por un total de ${float(amount_usd):,.2f} USD.'
    )
    return redirect(f'/trading/?symbol={symbol}')


@login_required
def sell_view(request):
    if request.method != 'POST':
        return redirect('trade')

    symbol = request.POST.get('symbol', '').upper()
    try:
        sell_qty = Decimal(request.POST.get('quantity', '0'))
    except Exception:
        messages.error(request, 'Cantidad inválida.')
        return redirect(f'/trading/?symbol={symbol}')

    if symbol not in SUPPORTED_SYMBOLS or sell_qty <= 0:
        messages.error(request, 'Datos de venta inválidos.')
        return redirect('trade')

    try:
        portfolio = Portfolio.objects.get(user=request.user, symbol=symbol)
    except Portfolio.DoesNotExist:
        messages.error(request, f'No tienes {symbol} en tu portafolio.')
        return redirect(f'/trading/?symbol={symbol}')

    if sell_qty > portfolio.quantity:
        messages.error(request, f'Solo tienes {float(portfolio.quantity):.6f} {symbol}.')
        return redirect(f'/trading/?symbol={symbol}')

    price = _get_price(symbol)
    if not price:
        messages.error(request, 'No se pudo obtener el precio. Intenta de nuevo.')
        return redirect(f'/trading/?symbol={symbol}')

    price_decimal = Decimal(str(price))
    total_usd = sell_qty * price_decimal

    # Actualizar balance y portafolio
    request.user.balance += total_usd
    request.user.save(update_fields=['balance'])

    portfolio.quantity -= sell_qty
    if portfolio.quantity <= Decimal('0.00000001'):
        portfolio.delete()
    else:
        portfolio.save(update_fields=['quantity'])

    # Registrar transacción
    tx = Transaction.objects.create(
        user=request.user,
        type=Transaction.SELL,
        symbol=symbol,
        quantity=sell_qty,
        price=price_decimal,
        total=total_usd,
    )

    # Enviar email
    send_trade_email(request.user, tx)

    messages.success(
        request,
        f'✅ Vendiste {float(sell_qty):.6f} {symbol} a ${price:,.2f} USD por un total de ${float(total_usd):,.2f} USD.'
    )
    return redirect(f'/trading/?symbol={symbol}')
