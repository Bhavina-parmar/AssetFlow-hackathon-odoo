from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import UserRole
from .serializers import UserSerializer, UserDetailSerializer

User = get_user_model()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        # Django AbstractUser uses username for auth; we support email lookup
        try:
            user_obj = User.objects.get(email__iexact=email)
            username = user_obj.username
        except User.DoesNotExist:
            # Fallback: treat email field as username
            username = email

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Incorrect email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'role': user.role,
                'username': user.username,
            }
        }, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        department_id = request.data.get('department', None)

        if not name or not email or not password:
            return Response(
                {'detail': 'name, email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {'detail': 'Password must be at least 6 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {'detail': 'An account with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build a username from email prefix, ensure uniqueness
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        # Split name into first/last
        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.EMPLOYEE,
        )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'role': user.role,
                'username': user.username,
            }
        }, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Employees (User management)
# ---------------------------------------------------------------------------

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD for users (employees). Admins can create / promote / toggle status.
    All authenticated users can list and retrieve.
    """
    serializer_class = UserDetailSerializer
    filterset_fields = ['role', 'is_active']

    def get_queryset(self):
        qs = User.objects.all().order_by('first_name', 'last_name', 'username')
        search = self.request.query_params.get('search', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]   # Admins enforced in perform_create / serializer

    def perform_create(self, serializer):
        # Only admin can create employees via API
        if self.request.user.role != UserRole.ADMIN:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only admins can create employee accounts.')
        serializer.save()

    @action(detail=True, methods=['post'], url_path='promote')
    def promote(self, request, pk=None):
        if request.user.role != UserRole.ADMIN:
            return Response({'detail': 'Only admins can promote employees.'}, status=status.HTTP_403_FORBIDDEN)
        employee = self.get_object()
        role = request.data.get('role')
        if role not in UserRole.values:
            return Response({'detail': f'Invalid role. Choose from: {UserRole.values}'}, status=status.HTTP_400_BAD_REQUEST)
        employee.role = role
        employee.save()
        return Response(UserDetailSerializer(employee).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        if request.user.role != UserRole.ADMIN:
            return Response({'detail': 'Only admins can toggle employee status.'}, status=status.HTTP_403_FORBIDDEN)
        employee = self.get_object()
        employee.is_active = not employee.is_active
        employee.save()
        return Response(UserDetailSerializer(employee).data, status=status.HTTP_200_OK)
