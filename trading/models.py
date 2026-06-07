from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Usuario con balance demo para trading."""
    email = models.EmailField(unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(default=timezone.now)

    # Perfil
    age = models.PositiveIntegerField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    @property
    def portfolio_value(self):
        """Valor total del portafolio en USD."""
        return sum(p.current_value for p in self.portfolios.all())

    @property
    def total_equity(self):
        """Balance + valor del portafolio."""
        return float(self.balance) + self.portfolio_value


class Portfolio(models.Model):
    """Posición abierta de una cripto para un usuario."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    symbol = models.CharField(max_length=20)          # ej: BTCUSDT
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    avg_buy_price = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolios'
        unique_together = ('user', 'symbol')
        verbose_name = 'Portafolio'
        verbose_name_plural = 'Portafolios'

    def __str__(self):
        return f"{self.user.email} — {self.symbol} x{self.quantity}"

    @property
    def cost_basis(self):
        return float(self.quantity) * float(self.avg_buy_price)

    # current_value se calcula desde la vista usando el precio live de Binance
    current_value = 0.0
    current_price = 0.0
    pnl = 0.0
    pnl_pct = 0.0


class Transaction(models.Model):
    """Registro de cada compra o venta."""
    BUY = 'buy'
    SELL = 'sell'
    TYPE_CHOICES = [(BUY, 'Compra'), (SELL, 'Venta')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    total = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'transactions'
        ordering = ['-timestamp']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return f"{self.get_type_display()} {self.quantity} {self.symbol} @ {self.price}"
