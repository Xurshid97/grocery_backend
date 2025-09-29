from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    raqam = models.CharField(max_length=20, unique=True, blank=True, null=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.raqam:
            self.raqam = self.username  # Default to username if no raqam provided
        super().save(*args, **kwargs)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    delivery_instructions = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.district}, {self.region}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    weight_unit = models.CharField(max_length=20, default='kg', choices=[('kg', 'Kilograms'), ('dona', 'Dona')], null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='product_images/')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[('Karta', 'Karta'), ('Bank o\'tkazmasi', 'Bank o\'tkazmasi'), ('Naqd', 'Naqd')])
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Payment {self.id} by {self.user.username}"
