from rest_framework.permissions import BasePermission


class IsQAAdmin(BasePermission):
    """
    Allows access only to QA users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'qa'


class IsAnalystOrHigher(BasePermission):
    """
    Allows access to Analyst, Reviewer, QA.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['analyst', 'reviewer', 'qa']


class IsReviewerOrHigher(BasePermission):
    """
    Allows access to Reviewer, QA.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['reviewer', 'qa']


class IsSelfOrQAAdmin(BasePermission):
    """
    Allows users to access/modify their own data.
    QA users can access/modify any user's data.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # QA can do anything
        if request.user.role == 'qa':
            return True
        
        # Check if this is for the current user
        # For views with pk parameter
        pk = view.kwargs.get('pk') if hasattr(view, 'kwargs') else None
        
        # For API views with pk in URL
        if pk:
            return str(request.user.id) == str(pk)
        
        # For endpoints without pk (assumed to be for current user)
        return True
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # QA can access any object
        if request.user.role == 'qa':
            return True
        
        # Check if object is the user themselves
        if hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False
