from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Note, WaitlistEmail
from rest_framework import generics
from .serializers import UserSerializer, NoteSerializer, WaitlistEmailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.balance_serializers import (
    BalanceGetRequestSerializer,
    BalanceGetResponseSerializer
)
from rest_framework.authentication import TokenAuthentication  # Or any other authentication class you use
from .serializers import (
    ItemRemoveRequestSerializer,
    ItemRemoveResponseSerializer,
    ItemWebhookUpdateRequestSerializer,
    ItemWebhookUpdateResponseSerializer,
    ItemPublicTokenExchangeRequestSerializer,
    ItemPublicTokenExchangeResponseSerializer,
    ItemAccessTokenInvalidateRequestSerializer,
    ItemAccessTokenInvalidateResponseSerializer,
    TransactionsSyncRequestSerializer,
    TransactionsSyncResponseSerializer,
    LinkTokenCreateRequestSerializer,
    LinkTokenCreateResponseSerializer,
    ErrorSerializer,
)
from plaid import Client
from plaid.errors import PlaidError
from .serializers import UserGetRequestSerializer, UserGetResponseSerializer
import os

# Initialize Plaid client (Replace with your actual Plaid credentials)
plaid_client = Client(
    client_id=os.environ.get('PLAID_CLIENT_ID'),
    secret=os.environ.get('PLAID_SECRET'),
    environment=os.environ.get('PLAID_ENVIRONMENT', 'sandbox')
)
# Create your views here.
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(author=self.request.user)
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors) #why not raise serializers.SerializerError?

class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Note.objects.filter(author=self.request.user)

class AddToWaitlist(generics.CreateAPIView):
    queryset = WaitlistEmail.objects.all()
    serializer_class = WaitlistEmailSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        # check if valid email
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return HttpResponseBadRequest(serializer.errors)
        # check if duplicate
        email = serializer.validated_data['email']
        if WaitlistEmail.objects.filter(email=email).exists():
            return HttpResponseBadRequest("duplicate")
        # save
        serializer.save()
        return HttpResponse(status=201)

# Balance Views

class BalanceGetView(APIView):
    """
    View to handle /accounts/balance/get requests.
    """
    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = BalanceGetRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Process the request using Plaid's API (pseudo-code)
            # response_data = plaid_client.Accounts.balance.get(**serializer.validated_data)
            # For the purpose of this example, we'll mock response_data
            response_data = {
                "accounts": [...],  # Replace with actual account data
                "item": {...},      # Replace with actual item data
                "request_id": "unique-request-id"
            }
            # Serialize the response data
            response_serializer = BalanceGetResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Users Views

class UserGetView(APIView):
    """
    View to handle /users/get requests.
    """
    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = UserGetRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Process the request using Plaid's API (pseudo-code)
            # response_data = plaid_client.Users.get(**serializer.validated_data)
            # For the purpose of this example, we'll mock response_data
            response_data = {
                "user": {
                    "names": [
                        {
                            "full_name": "John Doe",
                            "first_name": "John",
                            "last_name": "Doe",
                            "middle_name": None,
                            "suffix": None,
                            "prefix": None
                        }
                    ],
                    "emails": [
                        {
                            "data": "john.doe@example.com",
                            "primary": True,
                            "type": "personal"
                        }
                    ],
                    "phone_numbers": [
                        {
                            "data": "+1234567890",
                            "primary": True,
                            "type": "mobile"
                        }
                    ],
                    "addresses": [
                        {
                            "data": {
                                "street": "123 Main St",
                                "city": "Anytown",
                                "region": "CA",
                                "postal_code": "12345",
                                "country": "US"
                            },
                            "primary": True,
                            "type": "home"
                        }
                    ]
                },
                "request_id": "unique-request-id",
                "error": None
            }
            # Serialize the response data
            response_serializer = UserGetResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Items views

class ItemRemoveView(APIView):
    """
    View to handle /item/remove requests.
    """
    # Uncomment the following lines if you want to enforce authentication
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = ItemRemoveRequestSerializer(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data['access_token']
            try:
                # Call Plaid's /item/remove endpoint
                response = plaid_client.Item.remove(access_token)
                # Serialize the response data
                response_serializer = ItemRemoveResponseSerializer(data=response)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    # Handle serialization errors
                    return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PlaidError as e:
                # Handle Plaid errors
                error_data = e.to_dict()
                error_serializer = ErrorSerializer(data=error_data)
                if error_serializer.is_valid():
                    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'error': 'An unknown error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemWebhookUpdateView(APIView):
    """
    View to handle /item/webhook/update requests.
    """
    # Uncomment the following lines if you want to enforce authentication
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = ItemWebhookUpdateRequestSerializer(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data['access_token']
            webhook = serializer.validated_data['webhook']
            try:
                # Call Plaid's /item/webhook/update endpoint
                response = plaid_client.Item.webhook_update(access_token, webhook)
                # Serialize the response data
                response_serializer = ItemWebhookUpdateResponseSerializer(data=response)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PlaidError as e:
                # Handle Plaid errors
                error_data = e.to_dict()
                error_serializer = ErrorSerializer(data=error_data)
                if error_serializer.is_valid():
                    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'error': 'An unknown error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemPublicTokenExchangeView(APIView):
    """
    View to handle /item/public_token/exchange requests.
    """
    # Uncomment the following lines if you want to enforce authentication
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = ItemPublicTokenExchangeRequestSerializer(data=request.data)
        if serializer.is_valid():
            public_token = serializer.validated_data['public_token']
            try:
                # Call Plaid's /item/public_token/exchange endpoint
                response = plaid_client.Item.public_token.exchange(public_token)
                # Serialize the response data
                response_serializer = ItemPublicTokenExchangeResponseSerializer(data=response)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PlaidError as e:
                # Handle Plaid errors
                error_data = e.to_dict()
                error_serializer = ErrorSerializer(data=error_data)
                if error_serializer.is_valid():
                    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'error': 'An unknown error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemAccessTokenInvalidateView(APIView):
    """
    View to handle /item/access_token/invalidate requests.
    """
    # Uncomment the following lines if you want to enforce authentication
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = ItemAccessTokenInvalidateRequestSerializer(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data['access_token']
            try:
                # Call Plaid's /item/access_token/invalidate endpoint
                response = plaid_client.Item.access_token.invalidate(access_token)
                # Serialize the response data
                response_serializer = ItemAccessTokenInvalidateResponseSerializer(data=response)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PlaidError as e:
                # Handle Plaid errors
                error_data = e.to_dict()
                error_serializer = ErrorSerializer(data=error_data)
                if error_serializer.is_valid():
                    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'error': 'An unknown error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Transactions Sync Views

class TransactionsSyncView(APIView):
    """
    View to handle /transactions/sync requests.
    """
    # Uncomment the following lines if you want to enforce authentication
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = TransactionsSyncRequestSerializer(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data['access_token']
            cursor = serializer.validated_data.get('cursor')
            count = serializer.validated_data.get('count')
            options = serializer.validated_data.get('options', {})
            try:
                # Prepare options for Plaid API call
                plaid_options = {}
                if options.get('include_personal_finance_category'):
                    plaid_options['include_personal_finance_category'] = options['include_personal_finance_category']
                if options.get('include_original_description'):
                    plaid_options['include_original_description'] = options['include_original_description']

                # Call Plaid's /transactions/sync endpoint
                response = plaid_client.Transactions.sync(
                    access_token,
                    cursor=cursor,
                    count=count,
                    options=plaid_options
                )

                # Serialize the response data
                response_serializer = TransactionsSyncResponseSerializer(data=response)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    # Handle serialization errors
                    return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PlaidError as e:
                # Handle Plaid errors
                error_data = e.to_dict()
                error_serializer = ErrorSerializer(data=error_data)
                if error_serializer.is_valid():
                    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'error': 'An unknown error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
#LinkTokenCreate Views

class LinkTokenCreateView(APIView):
    """
    View to handle /link/token/create requests.
    """
    # Uncomment the following lines if you want to enforce authentication
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deserialize and validate the incoming request data
        serializer = LinkTokenCreateRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Prepare data for Plaid API call
                link_token_request_data = serializer.validated_data
                # Flatten the 'user' dictionary
                link_token_request_data['user'] = link_token_request_data['user']
                # Remove any None values (Plaid API may not accept nulls)
                link_token_request_data = {
                    k: v for k, v in link_token_request_data.items() if v is not None
                }
                # Call Plaid's /link/token/create endpoint
                response = plaid_client.LinkToken.create(link_token_request_data)
                # Serialize the response data
                response_serializer = LinkTokenCreateResponseSerializer(data=response)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    # Handle serialization errors
                    return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PlaidError as e:
                # Handle Plaid errors
                error_data = e.to_dict()
                error_serializer = ErrorSerializer(data=error_data)
                if error_serializer.is_valid():
                    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'error': 'An unknown error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
