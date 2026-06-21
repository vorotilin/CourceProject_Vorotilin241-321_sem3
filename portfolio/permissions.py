from rest_framework.permissions import BasePermission, SAFE_METHODS
from typing import Any
from rest_framework.request import Request


class IsOwnerOrAdmin(BasePermission):
    """
    Разрешает изменение только владельцу объекта или администратору.
    Безопасные методы (GET, HEAD, OPTIONS) доступны всем.
    """

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """
        Проверяет права на уровне конкретного объекта.
        Args:
            request: HTTP-запрос с данными пользователя
            view: ViewSet, обрабатывающий запрос
            obj: Объект модели (Project или Event)
        """
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        ):
            return True
        return hasattr(obj, 'user') and obj.user == request.user
