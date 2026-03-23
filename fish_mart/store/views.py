from rest_framework import viewsets, permissions
from .models import Product, Order, Category
from .serializers import ProductSerializer, OrderSerializer, OrderCreateSerializer
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from django.http import HttpResponse
from .models import Product
from django.http import JsonResponse
import json

# =========================
# TEMPLATE VIEWS (UPDATED)
# =========================

def home_page(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)[:8]

    return render(request, 'pages/home.html', {
        'categories': categories,
        'products': products
    })


def dashboard(request):
    products = Product.objects.all()
    total_products = products.count()
    total_orders = Order.objects.count()

    return render(request, 'pages/dashboard.html', {
        'products': products,
        'total_products': total_products,
        'total_orders': total_orders
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'pages/login.html')

def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Category', 'Price', 'Stock',
        'Batch Number', 'Model Number', 'Processed Time'
    ])

    products = Product.objects.all()

    for p in products:
        writer.writerow([
            p.name,
            p.category.name if p.category else '',
            p.price,
            p.stock,
            p.batch_number,
            p.model_number,
            p.processed_time
        ])

    return response


def import_products_csv(request):
    if request.method == 'POST':
        file = request.FILES['file']

        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        next(reader)  # skip header

        for row in reader:
            Product.objects.create(
                name=row[0],
                price=row[2],
                stock=row[3],
                batch_number=row[4],
                model_number=row[5],
            )

        return redirect('dashboard')

    return render(request, 'pages/import.html')


def update_stock(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        stock = data.get("stock")

        product = Product.objects.get(id=pk)
        product.stock = stock
        product.save()

        return JsonResponse({"status": "success"})

def logout_view(request):
    logout(request)
    return redirect('home')

# =========================
# API VIEWS (UNCHANGED)
# =========================

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created_at')