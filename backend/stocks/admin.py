from django.contrib import admin
from .models import Stock, StockPrice, StockChartPoint, Watchlist, StockTrendStat


admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(StockChartPoint)
admin.site.register(Watchlist)
admin.site.register(StockTrendStat)