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
