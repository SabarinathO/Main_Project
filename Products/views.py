from django.shortcuts import render
from .models import Product, ProductImage

# Create your views here.

def products(request):
    # Fetch all products with their first image
    products_with_images = []
    for product in Product.objects.all().exclude(sold=True):
        first_image = product.images.first()  # Use the related_name 'images' to get images
        products_with_images.append({
            'product': product,
            'image': first_image.image.url if first_image else None  # Handle case where no image exists
        })
    return render(request, 'products.html',{'products_with_images':products_with_images}) # This is the view that will be rendered when the user visits the products page.


def product_detail(request,id):
    product=Product.objects.get(id=id)
    images = product.images.all()
    related_products = Product.objects.filter(model=product.model).exclude(id=id)[:3]
    related_products_with_images = []
    for related_product in related_products:
        first_image = related_product.images.first()
        related_products_with_images.append({
            'product': related_product,
            'image': first_image.image.url if first_image else None
        })
    context = {'product':product,'images':images,'related_products':related_products_with_images}    
    return render(request, 'product_detail.html',context) # This is the view that will be rendered when the user visits the product detail page.