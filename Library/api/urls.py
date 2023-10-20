# from django.urls import path
# from .views import BookListCreateView, BookDetailView, MemberListCreateView, MemberDetailView, TransactionListCreateView, TransactionDetailView

# urlpatterns = [
#     path('books/', BookListCreateView.as_view(), name='book-list-create'),
#     path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),

#     path('members/', MemberListCreateView.as_view(), name='member-list-create'),
#     path('members/<int:pk>/', MemberDetailView.as_view(), name='member-detail'),

#     path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
#     path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
# ]
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import BookViewSet, MemberViewSet, TransactionViewSet,BookSearchView
from . import views

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'members', MemberViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'issue-book', views.IssueBookViewSet, basename='issue-book')
router.register(r'return-book', views.ReturnBookViewSet, basename='return-book')
# router.register(r'search', views.BookSearchView, basename='search-book')



urlpatterns = [
   path('', include(router.urls)),
   path('search/', BookSearchView.as_view(), name='search-books'),

    # path('issue-book/', views.BookIssuanceView.as_view(), name='issue-book'),
    # path('return-book/', views.BookReturnView.as_view(), name='return-book'),
    #  path('import-books/', views.import_books_from_frappe_api, name='import-books'),
    # Add more URLs for other operations
]

