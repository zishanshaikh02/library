
# from datetime import datetime
# from rest_framework import generics, status
# from rest_framework.response import Response
# from .models import Book, Member, Transaction
# from .serializers import BookSerializer, MemberSerializer, TransactionSerializer

# class BookIssuanceView(generics.CreateAPIView):
#     serializer_class = TransactionSerializer

#     def create(self, request, *args, **kwargs):
#         book_id = request.data.get('book')
#         member_id = request.data.get('member')
#         issue_date = datetime.now().date()  # Get the current date as the issue date

#         try:
#             book = Book.objects.get(id=book_id)
#             member = Member.objects.get(id=member_id)

#             # Check if the member's outstanding debt is below Rs. 500
#             if member.outstanding_debt > 500:
#                 return Response({"message": "Member's outstanding debt exceeds Rs. 500"}, status=status.HTTP_400_BAD_REQUEST)

#             # Update the stock of the book
#             if book.stock > 0:
#                 book.stock -= 1
#                 book.save()
#             else:
#                 return Response({"message": "Book is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

#             # Create a transaction for book issuance
#             transaction = Transaction(book=book, member=member, issue_date=issue_date)
#             transaction.save()

#             return Response({"message": "Book issued successfully"}, status=status.HTTP_201_CREATED)
#         except Book.DoesNotExist:
#             return Response({"message": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Member.DoesNotExist:
#             return Response({"message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        

# class BookReturnView(generics.CreateAPIView):
#     serializer_class = TransactionSerializer

#     def create(self, request, *args, **kwargs):
#         book_id = request.data.get('book')
#         member_id = request.data.get('member')
#         return_date = datetime.now().date()  # Get the current date as the return date

#         try:
#             book = Book.objects.get(id=book_id)
#             member = Member.objects.get(id=member_id)

#             # Find the corresponding transaction for book return
#             try:
#                 transaction = Transaction.objects.get(book=book, member=member, return_date__isnull=True)
#             except Transaction.DoesNotExist:
#                 return Response({"message": "Transaction not found or book was not issued to this member"}, status=status.HTTP_404_NOT_FOUND)

#             # Calculate rent fee (for example, Rs. 10 per day)
#             days_rented = (return_date - transaction.issue_date).days
#             rent_fee = days_rented * 10  # Adjust this as per your pricing

#             # Update the transaction with return date and rent fee
#             transaction.return_date = return_date
#             transaction.rent_fee = rent_fee
#             transaction.save()

#             # Update member's outstanding debt
#             member.outstanding_debt += rent_fee
#             member.save()

#             # Update the stock of the book
#             book.stock += 1
#             book.save()

#             return Response({"message": "Book returned successfully", "rent_fee": rent_fee}, status=status.HTTP_200_OK)
#         except Book.DoesNotExist:
#             return Response({"message": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Member.DoesNotExist:
#             return Response({"message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        
from rest_framework import viewsets
from .models import Book, Member, Transaction
from .serializers import BookSerializer, MemberSerializer, TransactionSerializer
from django.shortcuts import render, redirect, get_object_or_404

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


import requests
import json
from .models import Book

def fetch_and_save_books_from_api(api_url):
    # Make a GET request to the API to fetch the data
    response = requests.get(api_url)

    if response.status_code == 200:
        try:
            # Parse the JSON response
            data = json.loads(response.text)

            # Assuming the books are contained in a "message" key
            books_data = data.get("message", [])

            for book_data in books_data:
                isbn = book_data.get('isbn', '0000000000')
                
                # Check if a record with the same ISBN already exists
                if not Book.objects.filter(isbn=isbn).exists():
                    # Create a new Book instance and populate its fields from the API data
                    book = Book(
                        title=book_data.get('title', 'Unknown'),
                        authors=book_data.get('authors', 'Unknown'),
                        isbn=isbn,
                        publisher=book_data.get('publisher', 'Unknown'),
                        page=book_data.get('num_pages', 0),
                        stock=0  # You can set this to 0 or another default value
                    )

                    # Save the book to the database
                    book.save()
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
    else:
        print(f"Failed to fetch data from the API. Status code: {response.status_code}")


# Usage example
api_url = "https://frappe.io/api/method/frappe-library?page=2&title=and"  # Replace with the actual API URL
fetch_and_save_books_from_api(api_url)

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import Book, Member, Transaction
from .serializers import BookSerializer, MemberSerializer, TransactionSerializer
from django.utils import timezone
from rest_framework.views import APIView
from django.db.models import Q

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class IssueBookViewSet(viewsets.ViewSet):
    def create(self, request):
        book_id = request.data.get('book_id')
        member_id = request.data.get('member_id')
        book = get_object_or_404(Book, pk=book_id)
        member = get_object_or_404(Member, pk=member_id)
        if book.is_available() and not member.has_exceeded_debt_limit():
            transaction = Transaction(book=book, member=member, issue_date=timezone.now().date())
            transaction.save()
            book.decrease_stock()
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Handle errors (e.g., not enough stock or debt limit exceeded)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ReturnBookViewSet(viewsets.ViewSet):
    def create(self, request):
        transaction_id = request.data.get('transaction_id')
        transaction = get_object_or_404(Transaction, pk=transaction_id)
        if not transaction.is_overdue():
            rent_fee = transaction.calculate_rent_fee()
            transaction.rent_fee = rent_fee
            transaction.return_date = timezone.now().date()
            transaction.save()
            transaction.book.increase_stock()
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Handle overdue book scenario
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class BookSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')

        if query:
            books = Book.objects.filter(
                Q(title__icontains=query) | Q(authors__icontains=query)
            )
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
