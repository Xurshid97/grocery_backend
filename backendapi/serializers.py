from rest_framework import serializers
from .models import Product, Category, Order, SubCategory, Address, Payment, CustomUser
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
    class Meta:
        model = Address
        fields = ['*']



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
        fields = ['id', 'username', 'raqam', 'addresses', 'delivery_addresses', 'payments', 'orders']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'product_id', 'quantity', 'order_date', 'status']
        read_only_fields = ['user', 'order_date']

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
