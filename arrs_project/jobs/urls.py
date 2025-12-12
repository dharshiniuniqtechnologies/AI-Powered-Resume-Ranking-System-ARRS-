from rest_framework.routers import DefaultRouter
from .views import JobViewSet

router = DefaultRouter()
router.register('', JobViewSet, basename='job')

urlpatterns = router.urls


# from django.urls import path
# from .views import JobViewSet

# urlpatterns = [
#     path('', JobViewSet.as_view({'get': 'list'})),
#     path('<int:pk>/', JobViewSet.as_view({'get': 'retrieve'})),
#     path('create/', JobViewSet.as_view({'post': 'create'})),
#     path('<int:pk>/update/', JobViewSet.as_view({'put': 'update'})),
#     path('<int:pk>/delete/', JobViewSet.as_view({'delete': 'destroy'})),
# ]