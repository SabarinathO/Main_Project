from django.shortcuts import render,redirect
from Products.models import Product, ProductImage
from .models import Contact
from django.contrib.auth.decorators import login_required
from .models import Seller
# Create your views here.
def home(request):
    products_with_images_priority = []
    for product in Product.objects.filter(sold=False,priority__gt=0,priority__lt=5).order_by('priority')[:4]:
        first_image = product.images.first()  # Use the related_name 'images' to get images
        products_with_images_priority.append({
            'product': product,
            'image': first_image.image.url if first_image else None  # Handle case where no image exists
        })

    products_with_images_id = []
    products_with_images_id = [
        {
            'product': product,
            'image': product.images.first().image.url if product.images.first() else None
        }
        for product in Product.objects.all().exclude(sold=True).order_by('-id')[:4]
    ]   
    return render(request, 'home.html',{'products_with_images_priority':products_with_images_priority, 'products_with_images_id':products_with_images_id})

def contact(request):
    success=None
    if request.method=='POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        subject=request.POST.get('subject')
        message=request.POST.get('message')
        Contact.objects.create(name=name,email=email,subject=subject,message=message)
        sucess="Your message has been send successfully"
    return render(request, 'contact.html',{'success':success}) 

def about(request): 
    return render(request, 'about.html')

@login_required(login_url='/signin/')
def sell(request):
    success = None
    if request.method == 'POST':
        sellerName = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        productModel = request.POST.get('productModel')
        otherProduct = request.POST.get('otherProduct')
        if productModel == 'Other':
            productModel = otherProduct
        name = request.POST.get('productName')
        price = request.POST.get('price')
        description = request.POST.get('description')
        primaryImage = request.FILES.get('primaryImage')
        images = request.FILES.getlist('additionalImages')

        if hasattr(request.user, 'customer_profile'):
            user = request.user.customer_profile
        else:
            return render(request, 'sell.html', {'success': "You are not a customer"})

        if not all([sellerName, email, phone, productModel, name, price, description, primaryImage]):
            return render(request, 'sell.html', {'success': "All fields are required"})

        try:
            seller, created = Seller.objects.get_or_create(
                name=sellerName, email=email, phone=phone, user=user
            )
            product = Product.objects.create(
                name=name, model=productModel, price=price, description=description, seller=seller
            )
            ProductImage.objects.create(product=product, image=primaryImage)
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            success = "Your product has been added successfully"
        except Exception as e:
            success = f"Error occurred: {e}"

    return render(request, 'sell.html', {'success': success})


def sellHistory(request):
    user=request.user.customer_profile
    seller=Seller.objects.get(user=user)
    selled_products=Product.objects.filter(seller=seller,sold=True).order_by('-created_at')
    pending_products=Product.objects.filter(seller=seller,sold=False).order_by('-created_at')
    selled_products_with_images=[
        {
          'product':selled_product,
          'image':  selled_product.images.first().image.url if selled_product.images.first() else None,
          'delivered_date': selled_product.sold_date,
          'reciever': selled_product.reciever.name if selled_product.reciever else None,
          'receiever_phone': selled_product.reciever.phone if selled_product.reciever else None,
        }
        for selled_product in selled_products
    ]

    pending_products_with_images=[
        {
          'product':pending_product,
          'image':  pending_product.images.first().image.url if pending_product.images.first() else None
        }
        for pending_product in pending_products
    ]
    context = {
        'selled_products_with_images': selled_products_with_images,
        'pending_products_with_images': pending_products_with_images,
    }
    return render(request, 'sellHistory.html', context)

def item_Withdrawn(request,id):
    product=Product.objects.get(id=id)
    product.delete()
    return redirect(sellHistory)

