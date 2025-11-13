"""
Authentication views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import date
from .serializers import UserSerializer, AttendanceSerializer
from .models import Attendance


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'detail': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is None or not user.is_active:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Record attendance/login
        today = date.today()
        attendance, created = Attendance.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'login_time': timezone.now(),
                'is_active': True,
            }
        )
        
        # If attendance exists but user logged out, start new session
        if not created and not attendance.is_active:
            # When logging in again after logout:
            # - Preserve original login_time (first login of the day)
            # - Store current time as updated_at to track when this session started
            # - Clear logout_time (will be set again on next logout)
            # - Set is_active = True
            # Note: The previous session's duration should have already been
            # calculated and stored in total_duration when they logged out
            current_time = timezone.now()
            attendance.logout_time = None  # Clear previous logout time
            attendance.is_active = True
            # Use update() to set updated_at to current time (session start time)
            Attendance.objects.filter(id=attendance.id).update(
                is_active=True,
                logout_time=None,
                updated_at=current_time
            )
        
        # If user is already logged in (is_active=True), don't change anything
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Record logout time
            today = date.today()
            try:
                attendance = Attendance.objects.get(user=request.user, date=today, is_active=True)
                logout_time = timezone.now()
                attendance.logout_time = logout_time
                attendance.is_active = False
                
                # Calculate current session duration
                if attendance.login_time:
                    # Get the session start time
                    # If this is the first session, use login_time
                    # If this is a subsequent session, use updated_at (which was set when they logged in again)
                    if attendance.total_duration:
                        # This is a subsequent session - session started when they logged in again
                        # updated_at was set to the login time in the login view
                        session_start_time = attendance.updated_at
                        current_session_duration = logout_time - session_start_time
                        
                        # Add current session to total
                        if current_session_duration.total_seconds() > 0:
                            attendance.total_duration += current_session_duration
                        else:
                            # Fallback: calculate from first login (shouldn't happen, but safety)
                            total_elapsed = logout_time - attendance.login_time
                            attendance.total_duration = total_elapsed
                    else:
                        # First session of the day - calculate from first login
                        current_session_duration = logout_time - attendance.login_time
                        attendance.total_duration = current_session_duration
                
                attendance.save()
            except Attendance.DoesNotExist:
                pass  # No active attendance record
            
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    """Get current user information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RefreshTokenView(APIView):
    """Refresh access token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


from rest_framework import viewsets
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from common.permissions import IsAdminOrOwner

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Create user with password"""
        user = serializer.save()
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
            user.save()


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """Attendance viewset (read-only)"""
    queryset = Attendance.objects.select_related('user')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'date', 'is_active']
    ordering_fields = ['date', 'login_time']
    ordering = ['-date', '-login_time']
    
    def get_queryset(self):
        """Filter by current user unless admin"""
        queryset = super().get_queryset()
        if self.request.user.role not in ['admin', 'owner', 'manager']:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance for current user"""
        today = date.today()
        attendance = Attendance.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        if attendance:
            # Update duration if still active
            if attendance.is_active and attendance.login_time:
                attendance.total_duration = attendance.calculate_duration()
                attendance.save()
            
            serializer = self.get_serializer(attendance)
            return Response(serializer.data)
        else:
            return Response({'detail': 'No attendance record for today'}, status=status.HTTP_404_NOT_FOUND)

