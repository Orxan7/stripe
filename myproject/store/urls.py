from django.urls import path
from django.views.generic import TemplateView

from .views import buy, buy_orders, item, products, stripe_webhook

urlpatterns = [
    path('', products, name='products'),
    path('success/', TemplateView.as_view(template_name="success.html"), name='success'),
    path('item/<int:item_id>/', item, name='item'),
    path('buy/<int:item_id>/', buy, name='buy'),
    path('buy-orders/', buy_orders, name='buy_orders'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
]