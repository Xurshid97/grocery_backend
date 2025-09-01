from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView


from .models import Product, Category, Order, CustomUser
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    OrderSerializer,
    RegisterSerializer,
    UserSerializer,
    MyTokenObtainPairSerializer
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Response payload
        response_data = {
            "username": user.username,
            "raqam": user.raqam,
            "access": access_token,
        }

        response = Response(response_data, status=status.HTTP_201_CREATED)

        # Store refresh token in secure HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,        # ⚠️ Set True in production (requires HTTPS)
            samesite="None",
            max_age=60 * 60 * 24 * 7,  # 7 days
        )

        return response


class TokenRefreshView(generics.GenericAPIView):
    """Refresh access token using the refresh token stored in cookies."""

    permission_classes = [permissions.AllowAny]  # must be AllowAny

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        print(f"Refresh token from cookies: {refresh_token}")  # Debugging line
        if not refresh_token:
            return Response({"detail": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """Return the logged-in user's profile data (addresses, orders, payments, etc.)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        print(f"Updating user profile with data: {request.data}")  # Debugging line
        print(f"Is serializer valid? {serializer}")  # Debugging line
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # disable pagination for categories


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow users to see their own orders
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["cost", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        queryset = Product.objects.all().order_by("-created_at")
        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(subcategory__category_id=category_id)  # ✅ fixed relation
        return queryset

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # Assumes serializer sets user
        refresh = RefreshToken.for_user(user)
        response_data = serializer.validated_data
        response_data['username'] = user.username
        response_data['raqam'] = user.raqam
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite="None",
            max_age=60 * 60 * 24 * 7
        )
        return response
