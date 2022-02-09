from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import movie_list, movie_details
# from .views import WatchListAV, WatchDetailAV, StreamPlatformAV, StreamPlatformDetailAV, ReviewList, ReviewDetail

from .views import(
    WatchListAV, 
    WatchDetailAV, 
    StreamPlatformAV, 
    StreamPlatformDetailAV,
    ReviewCreate, 
    ReviewList, 
    ReviewDetail,
    StreamPlatformVS,
    WatchListGV
) 

router = DefaultRouter()
router.register('stream', StreamPlatformVS, basename='streamplatform')

urlpatterns = [
    path('list/', WatchListAV.as_view(), name='watch-list'),
    path('<int:pk>/', WatchDetailAV.as_view(), name='watch-detail'),
    path('new-list/', WatchListGV.as_view(), name='watch-lists'),
    path('', include(router.urls)),
    # path('stream', StreamPlatformAV.as_view(), name='stream-list'),
    # path('stream/<int:pk>', StreamPlatformDetailAV.as_view(), name='stream-detail'),
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name='review-create'),
    path('<int:pk>/reviews/', ReviewList.as_view(), name='review-list'),
    path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
]
