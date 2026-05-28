
from django.contrib import admin
from .models import (
    Stock,
    StockPrice,
    StockChartPoint,
    Watchlist,
    StockTrendStat,
    StockAiAnalysis,
)

admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(StockChartPoint)
admin.site.register(Watchlist)
admin.site.register(StockTrendStat)
admin.site.register(StockAiAnalysis)