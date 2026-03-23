from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from store.views import ProductViewSet, OrderViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from store.views import ProductViewSet, OrderViewSet, dashboard, home_page
from store.views import login_view, logout_view
from store.views import export_products_csv, import_products_csv,update_stock

# Router configuration
router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')

# Root / Home View
def home(request):
    return JsonResponse({
        "message": "Welcome to Fish Mart API 🐟",
        "available_endpoints": {
            "admin": "/admin/",
            "products": "/api/products/",
            "orders": "/api/orders/",
            "token": "/api/token/",
        }
    })


urlpatterns = [
    path('', home_page, name='home'),  # ✅ NOW HTML PAGE

    path('dashboard/', dashboard, name='dashboard'),  # ✅ NEW PAGE

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('admin/', admin.site.urls),

    # API Routes
    path('api/', include(router.urls)),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('export-csv/', export_products_csv, name='export_csv'),
    path('import-csv/', import_products_csv, name='import_csv'),

    path('update-stock/<int:pk>/', update_stock, name='update_stock'),
]

# Media Files (Development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)