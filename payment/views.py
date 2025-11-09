import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse


# Set your Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY

def payment(request):
    if not request.session.get("cart_visited"):  # If cart not visited, redirect
        return redirect("cart")
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        request.session["payment_method"] = payment_method
        request.session["payment_visited"] = True
        order_id = request.POST.get("order_id")
        total_amount = request.POST.get("totalamount")
        
        if payment_method == "stripe":
            # Convert amount to cents as Stripe expects amounts in cents
            amount_in_cents = int(float(total_amount) * 100)
            
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "unit_amount": amount_in_cents,
                            "product_data": {
                                "name": f"Order {order_id}",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("orderConfirm")),
                cancel_url=request.build_absolute_uri(reverse("checkout")),
            )

            return redirect(checkout_session.url)  # Redirect to Stripe Checkout Page
        elif payment_method == "cash_on_delivary":
            return redirect("orderConfirm")
    return redirect('checkout')    



