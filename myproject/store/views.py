import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse as url_for
from django.contrib.auth.models import User
from .models import Item, Order

DOMAIN = settings.DOMAIN
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
stripe.api_key = STRIPE_SECRET_KEY

@csrf_exempt
def products(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'create_order':
            item_id = request.POST.get('item_id')
            item = Item.objects.get(id=item_id)
            order, created = Order.objects.get_or_create(user=request.user, item=item, defaults={'quantity': 1})
            if created:
                return JsonResponse({'message': 'Order created successfully'}, status=201)
            else:
                return JsonResponse({'error': 'Failed to create order'}, status=400)
        elif request.POST.get('action') == 'delete_order':
            order_id = request.POST.get('order_id')
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                order.delete()
                return JsonResponse({'message': 'Order deleted successfully'}, status=200)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found'}, status=404)
        
        return JsonResponse({'error': 'Invalid action'}, status=400)

    elif request.method == 'GET':
        items = Item.objects.all()
        orders = Order.objects.filter(user=request.user) if request.user.is_authenticated else []
        total_price = sum(order.item.price * order.quantity for order in orders)

        context = {
            'items': items,
            'orders': orders,
            'total_price': total_price,
            'stripe_public_key': STRIPE_PUBLIC_KEY,
        }
        return render(request, 'products.html', context)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def item(request, item_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    item_object = Item.objects.filter(id=item_id)
    if not item_object.exists():
        return render(request, 'error.html')
    else:
        item_object = item_object.first()
        context = {
            'item_id': item_id,
            'item_name': item_object.name,
            'item_price': item_object.price,
            'stripe_public_key': STRIPE_PUBLIC_KEY,
        }
        return render(request, 'item.html', context)
        
def buy(request, item_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    item_object = Item.objects.get(id=item_id)
    stripe_id = item_object.stripe_id
    prices = stripe.Price.list(product=stripe_id)
    use_price_id = prices.data[0].id if prices.data else None

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': use_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=DOMAIN + url_for('store:success'),
        )
    except Exception as e:
        return str(e)

    return JsonResponse({'session_id': checkout_session.id})

def buy_orders(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    orders = Order.objects.filter(user=request.user) if request.user.is_authenticated else []
    if not orders.exists():
        return JsonResponse({'error': 'No orders found'}, status=404)
    
    line_items = []
    for order in orders:
        item_object = order.item
        stripe_id = item_object.stripe_id
        prices = stripe.Price.list(product=stripe_id)
        use_price_id = prices.data[0].id if prices.data else None
        line_items.append({
            'price': use_price_id,
            'quantity': order.quantity,
        })
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=DOMAIN + url_for('store:success'),
            client_reference_id=request.user.id,
        )
    except Exception as e:
        return str(e)

    return JsonResponse({'session_id': checkout_session.id})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id', None)
        if user_id:
            user = User.objects.get(id=user_id)
            user_order = Order.objects.filter(user=user)
            user_order.delete()
            print(f"Payment was successful for session ID: {session['id']}")
    return JsonResponse({'status': 'success'}, status=200)