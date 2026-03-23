# store/serializers.py
from rest_framework import serializers
from .models import Category, Product, ProductImage, Order, OrderItem

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = ['id','name','slug','description','price','weight_g','stock','images','category']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product','quantity','unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','status','total','shipping_address','phone','items','created_at']
        read_only_fields = ['user','status','total','created_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['shipping_address','phone','items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(user=user, total=0, **validated_data)
        total = 0
        for it in items_data:
            product_id = it.get('product')
            quantity = it.get('quantity')
            product = Product.objects.get(pk=product_id)
            if product.stock < quantity:
                raise serializers.ValidationError(f'Not enough stock for {product.name}')
            unit_price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=unit_price)
            product.stock -= quantity
            product.save()
            total += float(unit_price) * quantity
        order.total = total
        order.save()
        return order
