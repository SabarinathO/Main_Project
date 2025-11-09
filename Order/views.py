from django.shortcuts import render,redirect
from Products.models import Product
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from datetime import datetime
# Create your views here.
@login_required(login_url='/signin/')
def cart(request): 
    user=request.user.customer_profile
    order,created=Order.objects.get_or_create(customer=user,complete=False,status=Order.CART_STAGE)
    if request.method=='POST':
        id=request.POST.get('product_id') 
        product=Product.objects.get(id=id)
        existing_order_item=OrderItem.objects.filter(order=order,product=product)
        if existing_order_item.exists():
            order_item=existing_order_item[0]
            order_item.quantity+=1
            order_item.save()
        else:
            order_item=OrderItem.objects.create(product=product,order=order,quantity=1)
    total_price = order.items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or 0
    print("Total Price Value:", total_price)
    print("Total Price Type:", type(total_price))
    return render(request,'cart.html',{'order_items':order.items.all(),'total_price':total_price})

def removeItem(request,id):
    order_item=OrderItem.objects.get(id=id)
    product=order_item.product
    user=request.user.customer_profile
    order=Order.objects.get(customer=user,status=Order.CART_STAGE)
    existing_order_item=OrderItem.objects.filter(order=order,product=product)
    if existing_order_item.exists():
        order_item=existing_order_item[0]
        order_item.quantity-=1
        order_item.save()
        if order_item.quantity==0:
            order_item.delete()
    return redirect('cart')

def checkout(request):  
    user=request.user.customer_profile
    order=Order.objects.get(customer=user,status=Order.CART_STAGE)
    total_price = 0
    if order:
        total_price = order.items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or 0
        request.session["cart_visited"] = True    
    return render(request,'checkout.html',{'total_price':total_price})

def orderConfirm(request):
    if not request.session.get("payment_visited"):
        return redirect("payment") 
    user=request.user.customer_profile
    order=Order.objects.get(customer=user,status=Order.CART_STAGE)
    total_price = order.items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or 0

    # Fetch product and seller details
    order_items = order.items.all()
    product_details = []
    for item in order_items:
        product_details.append(f"Product: {item.product.name},Seller: {item.product.seller.name},Phone: {item.product.seller.phone}")

    # Create email content
    subject = "Order Details & Seller Information"
    message = f"Dear {user.name},\n\nHere are the seller details for your order:\n\n"
    message += "\n".join(product_details)
    message += f"\n\nTotal Price: ₹{total_price}"
    message += "\n\nPlease contact the seller for any queries regarding the product.\n\n"
    message += "\nThank you for shopping with us!"


    # Send email
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender email
        [request.user.email],  # Customer email
        fail_silently=False
    )

    order.complete=True
    order.status=Order.ORDER_CONFIRMED
    order.save()
    payment_method = request.session.pop("payment_method","Not Available")
    request.session.pop("cart_visited", None)
    request.session.pop("payment_visited", None)
    context={'total_price':total_price,'payment_method':payment_method.replace("_", " ").title(),'order':order}
    return render(request,'order_confirm.html',context) 

def previousOrders(request):
    user = request.user.customer_profile
    pending_orders = Order.objects.filter(customer=user, complete=True).exclude(status__in=[Order.CART_STAGE, Order.ORDER_DELIVERED])
    delivered_orders = Order.objects.filter(customer=user, status=Order.ORDER_DELIVERED).order_by('-delivered_date')
    context={'pending_orders':pending_orders,'delivered_orders':delivered_orders}
    return render(request,'previous_orders.html',context)


@csrf_exempt
def update_order_status(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get("status", "").lower()

            if new_status != "delivered":
                return JsonResponse({"success": False, "error": "Invalid status update"}, status=400)

            order = get_object_or_404(Order, id=order_id)
            order.status = Order.ORDER_DELIVERED
            order.delivered_date = datetime.now()
            order.save()

            for item in order.items.all():
                item.product.sold=True
                item.product.recieved=True
                item.product.reciever=order.customer
                item.product.sold_date=datetime.now()
                item.product.save()


            items = []
            for item in order.items.all():
                image_url = (
                    item.product.images.first().image.url
                    if item.product.images.exists() else "/static/images/default.png"
                )
                items.append({
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "product_image": image_url
                })

            return JsonResponse({
                "success": True,
                "delivered_date": order.delivered_date.strftime('%Y-%m-%d'),
                "items": items
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
