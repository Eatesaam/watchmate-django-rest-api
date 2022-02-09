from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from ..models import Watchlist, StreamPlatform, Review
from .serializers import WatchlistSerializer, StreamPlatformSerializer, ReviewSerializer
from .permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly
from .throttling import ReviewCreateThrottle, ReviewListThrottle
from .pagination import WatchListPagination


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle]
    
    def get_queryset(self):
        return Review.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        watchlist = Watchlist.objects.get(pk=pk)
        
        user = self.request.user
        review_queryset = Review.objects.filter(watchlist=watchlist, review_user=user)
        
        if review_queryset.exists():
            raise ValidationError("You have already reviewed this watchlist")
        
        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating']) / 2 
        
        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()
        
        serializer.save(watchlist=watchlist, review_user=user)


class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewListThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)
    
class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'

# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    

# class ReviewList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# class StreamPlatformVS(viewsets.ViewSet):

#     def list(self, request):
#         queryset = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamPlatform.objects.all()
#         streamplatform = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(streamplatform)
#         return Response(serializer.data)
    
#     def create(self, request):
#         serializer = StreamPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)

class StreamPlatformVS(viewsets.ModelViewSet):
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer
    permission_classes = [IsAdminOrReadOnly]

    

class StreamPlatformAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request):
        streamplatforms = StreamPlatform.objects.all()
        serializer = StreamPlatformSerializer(
            streamplatforms, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = StreamPlatformSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    

class StreamPlatformDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            streamplatform = StreamPlatform.objects.get(pk=pk)
        except StreamPlatform.DoesNotExist:
            return Response({'error': 'StreamPlatform not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StreamPlatformSerializer(
            streamplatform,  context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        streamplatform = StreamPlatform.objects.get(pk=pk)
        serializer = StreamPlatformSerializer(streamplatform, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        streamplatform = StreamPlatform.objects.get(pk=pk)
        streamplatform.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class WatchListGV(generics.ListAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    pagination_class = WatchListPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['title', 'platform__name']
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['^title', 'platform__name']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['avg_rating']

class WatchListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        watchlists = Watchlist.objects.all()
        serializer = WatchlistSerializer(watchlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class WatchDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            watchlist = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response({'error': 'Watchlist not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WatchlistSerializer(watchlist)
        return Response(serializer.data)
    
    def put(self, request, pk):
        watchlist = Watchlist.objects.get(pk=pk)
        serializer = WatchlistSerializer(watchlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        watchlist = Watchlist.objects.get(pk=pk)
        watchlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




    

# @api_view(['GET','POST'])
# def Watchlist_list(request):
#     if request.method == 'GET':
#         Watchlists = Watchlist.objects.all()
#         serializer = WatchlistSerializer(Watchlists, many=True)
#         return Response(serializer.data)
    
#     if request.method == 'POST':
#         serializer = WatchlistSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)


# @api_view(['GET','PUT','DELETE'])
# def Watchlist_details(request, id):
#     if request.method == 'GET':
#         try:
#             Watchlist = Watchlist.objects.get(pk=id)
#         except Watchlist.DoesNotExist:
#             return Response({'error': 'Watchlist not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = WatchlistSerializer(Watchlist)
#         return Response(serializer.data)
    
#     if request.method == 'PUT':
#         Watchlist = Watchlist.objects.get(pk=id)
#         serializer = WatchlistSerializer(Watchlist, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     if request.method == 'DELETE':
#         Watchlist = Watchlist.objects.get(pk=id)
#         Watchlist.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)