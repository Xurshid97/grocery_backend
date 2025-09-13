from rest_framework import serializers
from .models import Product, Category, Order, SubCategory, Address, Payment, CustomUser, OrderItem
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'raqam', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            raqam=validated_data.get('raqam', ''),
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'image', 'category']


class ProductSerializer(serializers.ModelSerializer):
    subcategory = SubCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'cost', 'discount', 'image',
            'created_at', 'subcategory', 'weight', 'weight_unit', 'created_by'
        ]


class AddressSerializer(serializers.ModelSerializer):
    region = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
    is_default = serializers.BooleanField(required=False)
    is_delivery = serializers.BooleanField(required=False)

    # user becomes current user not needed to come from outside
    user = serializers.PrimaryKeyRelatedField(read_only=True)


    class Meta:
        model = Address
        fields = ['id', 'user', 'delivery_instructions', 'street', 'district', 'region', 'city', 'postal_code', 'is_default', 'is_delivery']



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'status', 'payment_date']


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)  # fixed name
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')  # fixed
    orders = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='order_set')  # fixed

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'raqam', 'addresses', 'payments', 'orders']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login_field = attrs.get("username")  # correctly use username_field
        password = attrs.get("password")

        # Try authenticate with username
        user = authenticate(username=login_field, password=password)

        if not user:
            # Try phone
            try:
                user_obj = get_user_model().objects.get(raqam=login_field)
            except get_user_model().DoesNotExist:
                raise serializers.ValidationError("No user found with this username or phone")

            user = authenticate(username=user_obj.username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Generate tokens
        data = super().validate({"username": user.username, "password": password})

        # Add extra user info
        data["user"] = {
            "id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "phone": getattr(user, "raqam", None),
        }

        # add access token only not refresh token
        data["access"] = str(self.get_token(user))
        # Remove refresh token
        data.pop("refresh", None)
        return data

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # just user ID
    items = OrderItemSerializer(many=True)
    delivery_address = AddressSerializer()

    class Meta:
        model = Order
        fields = ["id", "user", "items", "order_date", "status", "delivery_address"]
        read_only_fields = ["user", "order_date"]

    def create(self, validated_data):
        print("Validated data:", validated_data)
        items_data = validated_data.pop("items")
        print("Items data:", items_data)

        delivery_address_data = validated_data.pop("delivery_address", None)
        address = None
        if delivery_address_data:
            address, created = Address.objects.get_or_create(
                user=self.context['request'].user,
                street=delivery_address_data.get('street', ''),
                district=delivery_address_data.get('district', ''),
                region=delivery_address_data.get('region', ''),
                city=delivery_address_data.get('city', ''),
                postal_code=delivery_address_data.get('postal_code', ''),
                defaults={
                    'delivery_instructions': delivery_address_data.get('delivery_instructions', ''),
                    'is_default': delivery_address_data.get('is_default', False),
                    'is_delivery': delivery_address_data.get('is_delivery', True)
                }
            )
        validated_data['delivery_address'] = address

        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
