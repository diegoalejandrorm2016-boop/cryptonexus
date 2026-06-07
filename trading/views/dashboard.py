from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import requests

from trading.models import Portfolio, Transaction

BINANCE_BASE = 'https://api.binance.com/api/v3'


def _fetch_prices(symbols: list[str]) -> dict[str, float]:
    """Obtiene precios actuales de Binance para una lista de símbolos."""
    prices = {}
    try:
        resp = requests.get(f'{BINANCE_BASE}/ticker/price', timeout=5)
        if resp.ok:
            for item in resp.json():
                if item['symbol'] in symbols:
                    prices[item['symbol']] = float(item['price'])
    except Exception:
        pass
    return prices


@login_required
def dashboard_view(request):
    portfolios = Portfolio.objects.filter(user=request.user, quantity__gt=0)
    symbols = [p.symbol for p in portfolios]
    prices = _fetch_prices(symbols)

    portfolio_data = []
    total_invested = 0.0
    total_current = 0.0

    for p in portfolios:
        current_price = prices.get(p.symbol, 0.0)
        current_value = float(p.quantity) * current_price
        cost_basis = float(p.quantity) * float(p.avg_buy_price)
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis else 0

        total_invested += cost_basis
        total_current += current_value

        portfolio_data.append({
            'symbol': p.symbol,
            'quantity': float(p.quantity),
            'avg_buy_price': float(p.avg_buy_price),
            'current_price': current_price,
            'current_value': current_value,
            'cost_basis': cost_basis,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
        })

    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

    recent_txs = Transaction.objects.filter(user=request.user)[:5]

    context = {
        'portfolio': portfolio_data,
        'balance': float(request.user.balance),
        'total_invested': total_invested,
        'total_current': total_current,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'total_equity': float(request.user.balance) + total_current,
        'recent_transactions': recent_txs,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def history_view(request):
    qs = Transaction.objects.filter(user=request.user)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/history.html', {'page_obj': page_obj})
