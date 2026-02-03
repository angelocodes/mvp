from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsQAAdmin, IsAnalystOrHigher, IsSelfOrQAAdmin
from apps.audit.utils import AuditLogger
from apps.audit.models import AuditLog
from apps.projects.models import Project


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsQAAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        AuditLogger.log_user_action(
            self.request.user,
            'create',
            user,
            {'created_username': user.username, 'created_role': user.role}
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsQAAdmin]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        AuditLogger.log_auth_action(
            user,
            'login',
            {'ip_address': request.META.get('REMOTE_ADDR', 'unknown')}
        )
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    user = request.user
    logout(request)
    AuditLogger.log_auth_action(
        user,
        'logout',
        {'username': user.username}
    )
    return Response({'message': 'Logged out successfully'})


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsSelfOrQAAdmin])
def update_profile(request, pk=None):
    """
    Update user profile information.
    Users can update their own profile. QA can update any profile.
    """
    # If pk is provided, update that user (QA only can do this via permission)
    # If no pk, update current user
    if pk:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user
    
    # Fields that can be updated
    allowed_fields = ['email', 'first_name', 'last_name']
    
    # Update fields
    updated_fields = []
    for field in allowed_fields:
        if field in request.data:
            old_value = getattr(user, field)
            new_value = request.data[field]
            if old_value != new_value:
                setattr(user, field, new_value)
                updated_fields.append(field)
    
    if updated_fields:
        user.save()
        
        # Log the update action
        AuditLogger.log_user_action(
            request.user,
            'update',
            user,
            {'updated_fields': updated_fields}
        )
        
        return Response({
            'message': 'Profile updated successfully',
            'updated_fields': updated_fields
        })
    
    return Response({'message': 'No changes made'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    Requires current password for verification.
    """
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    # Validate inputs
    if not current_password or not new_password:
        return Response(
            {'error': 'Current password and new password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify current password
    if not check_password(current_password, user.password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password length
    if len(new_password) < 8:
        return Response(
            {'error': 'New password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check new password is different
    if check_password(new_password, user.password):
        return Response(
            {'error': 'New password must be different from current password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    # Update session to prevent logout
    update_session_auth_hash(request, user)
    
    # Log password change (without storing the password)
    AuditLogger.log_user_action(
        request.user,
        'update',
        user,
        {'updated_fields': ['password']}
    )
    
    return Response({'message': 'Password changed successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request, pk=None):
    """
    Get user statistics including projects created, validations submitted, etc.
    Users can view their own stats. QA can view any user's stats.
    """
    # Determine which user to get stats for
    if pk and request.user.role == 'qa':
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user
    
    # Calculate statistics
    stats = {
        'user_id': user.id,
        'username': user.username,
    }
    
    # Projects created by user
    stats['projects_created'] = Project.objects.filter(created_by=user).count()
    
    # Validations submitted (count audit log entries for validation actions)
    validation_actions = ['submit', 'update']
    stats['validations_submitted'] = AuditLog.objects.filter(
        user=user,
        object_type='validation',
        action__in=validation_actions
    ).count()
    
    # Projects reviewed (for reviewers)
    stats['projects_reviewed'] = Project.objects.filter(reviewer=user).count()
    
    # Total activity count
    stats['total_activity'] = AuditLog.objects.filter(user=user).count()
    
    # Days active (from date joined to today)
    days_since_joined = (timezone.now().date() - user.date_joined.date()).days
    stats['days_active'] = max(1, days_since_joined)
    
    # Recent activity count (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    stats['recent_activity'] = AuditLog.objects.filter(
        user=user,
        timestamp__gte=thirty_days_ago
    ).count()
    
    return Response(stats)
