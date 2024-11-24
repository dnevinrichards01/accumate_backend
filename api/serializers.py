from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, WaitlistEmail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# Import your models if needed
from .models import Note, WaitlistEmail, Budget

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        #print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
    
class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'author']
        extra_kwargs = {'author': {'read_only': True}}

class WaitlistEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = WaitlistEmail
        fields = ['email']
        extra_kwargs = {'email': {'write_only': True}}

    def validate_email(self, email):
        try: 
            validate_email(email)
            return email
        except: 
            raise ValidationError()


#Teymur:

# Plaid Error Serializer
class ErrorSerializer(serializers.Serializer):
    """
    Generic serializer for handling Plaid API errors.
    """
    error_type = serializers.CharField(help_text="The broad categorization of the error.")
    error_code = serializers.CharField(help_text="The particular error code.")
    error_message = serializers.CharField(help_text="A developer-friendly error message.")
    display_message = serializers.CharField(allow_null=True, help_text="A user-friendly error message.")
    request_id = serializers.CharField(help_text="A unique identifier for the request, used for troubleshooting.")
    suggested_action = serializers.CharField(allow_null=True, help_text="Suggested steps for resolving the error.")
    status_code = serializers.IntegerField(help_text="The HTTP status code associated with the error.")

# Plaid Balance Serializers
class BalanceGetRequestOptionsSerializer(serializers.Serializer):
    """
    Serializer for the 'options' field in the BalanceGetRequest.
    """
    account_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of account IDs to retrieve balances for."
    )
    min_last_updated_datetime = serializers.DateTimeField(
        required=False,
        help_text="Filter to accounts updated after this datetime."
    )

class BalanceGetRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /accounts/balance/get endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token associated with the Item data is being requested for."
    )
    options = BalanceGetRequestOptionsSerializer(
        required=False,
        help_text="Additional options to filter the balance request."
    )

class AccountBalancesSerializer(serializers.Serializer):
    """
    Serializer for the 'balances' field within an account.
    """
    available = serializers.FloatField(
        allow_null=True,
        help_text="The available balance for the account."
    )
    current = serializers.FloatField(
        help_text="The current balance for the account."
    )
    limit = serializers.FloatField(
        allow_null=True,
        help_text="For credit-type accounts, the credit limit."
    )
    iso_currency_code = serializers.CharField(
        allow_null=True,
        max_length=3,
        help_text="The ISO-4217 currency code of the balance."
    )
    unofficial_currency_code = serializers.CharField(
        allow_null=True,
        max_length=3,
        help_text="The unofficial currency code associated with the balance."
    )

class AccountSerializer(serializers.Serializer):
    """
    Serializer for an individual account object.
    """
    ACCOUNT_TYPES = (
        ('brokerage', 'brokerage'),
        ('credit', 'credit'),
        ('depository', 'depository'),
        ('loan', 'loan'),
        ('investment', 'investment'),
        ('other', 'other'),
    )
    VERIFICATION_STATUSES = (
        ('pending_automatic_verification', 'pending_automatic_verification'),
        ('pending_manual_verification', 'pending_manual_verification'),
        ('manually_verified', 'manually_verified'),
        ('verification_expired', 'verification_expired'),
    )

    account_id = serializers.CharField(
        help_text="A unique ID identifying the account."
    )
    balances = AccountBalancesSerializer(
        help_text="The balances for the account."
    )
    mask = serializers.CharField(
        required=False,
        help_text="The last 2-4 digits of the account number."
    )
    name = serializers.CharField(
        help_text="The name of the account."
    )
    official_name = serializers.CharField(
        required=False,
        help_text="The official name of the account."
    )
    subtype = serializers.CharField(
        required=False,
        help_text="The account subtype."
    )
    type = serializers.ChoiceField(
        choices=ACCOUNT_TYPES,
        help_text="The account type."
    )
    verification_status = serializers.ChoiceField(
        choices=VERIFICATION_STATUSES,
        required=False,
        allow_null=True,
        help_text="The verification status of the account."
    )

class ItemSerializer(serializers.Serializer):
    """
    Serializer for the 'item' field in the response.
    """
    UPDATE_TYPES = (
        ('background', 'background'),
        ('user_present_required', 'user_present_required'),
    )

    available_products = serializers.ListField(
        child=serializers.CharField(),
        help_text="Products available for the Item."
    )
    billed_products = serializers.ListField(
        child=serializers.CharField(),
        help_text="Products billed for the Item."
    )
    consent_expiration_time = serializers.DateTimeField(
        allow_null=True,
        help_text="Time when the Item's consent will expire."
    )
    error = ErrorSerializer(
        allow_null=True,
        help_text="Error object containing error details, if any."
    )
    institution_id = serializers.CharField(
        allow_null=True,
        help_text="The Plaid institution ID associated with the Item."
    )
    item_id = serializers.CharField(
        help_text="A unique ID identifying the Item."
    )
    update_type = serializers.ChoiceField(
        choices=UPDATE_TYPES,
        help_text="The type of update for the Item."
    )
    webhook = serializers.CharField(
        allow_null=True,
        help_text="The webhook URL associated with the Item."
    )

class BalanceGetResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /accounts/balance/get endpoint.
    """
    accounts = AccountSerializer(
        many=True,
        help_text="List of accounts associated with the Item."
    )
    item = ItemSerializer(
        help_text="Information about the Item."
    )
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )

# Plaid Webhook Serializer
class WebhookSerializer(serializers.Serializer):
    """
    Serializer for Plaid link webhooks.
    """
    WEBHOOK_TYPES = (
        ('ITEM', 'ITEM'),
        ('TRANSACTIONS', 'TRANSACTIONS'),
        ('INVESTMENTS_TRANSACTIONS', 'INVESTMENTS_TRANSACTIONS'),
        ('ASSETS', 'ASSETS'),
        ('AUTH', 'AUTH'),
        ('HOLDINGS', 'HOLDINGS'),
        ('IDENTITY', 'IDENTITY'),
        ('INCOME', 'INCOME'),
        ('LIABILITIES', 'LIABILITIES'),
        ('PAYMENT_INITIATION', 'PAYMENT_INITIATION'),
        ('TRANSFERS', 'TRANSFERS'),
    )

    webhook_type = serializers.ChoiceField(
        choices=WEBHOOK_TYPES,
        help_text="The type of webhook."
    )
    webhook_code = serializers.CharField(
        help_text="The code representing the webhook event."
    )
    item_id = serializers.CharField(
        help_text="The ID of the Item associated with the webhook."
    )
    error = ErrorSerializer(
        required=False,
        allow_null=True,
        help_text="Error object containing error details, if any."
    )
    account_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of account IDs affected by the webhook."
    )
    new_transactions = serializers.IntegerField(
        required=False,
        help_text="Number of new transactions available."
    )
    removed_transactions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of transaction IDs that have been removed."
    )
    reset_transactions = serializers.IntegerField(
        required=False,
        help_text="Indicates a reset of transactions."
    )
    # Additional fields can be added as needed based on webhook_code

    def validate(self, data):
        """
        Custom validation to ensure required fields are present based on webhook_code.
        """
        webhook_code = data.get('webhook_code')
        # Add validation logic based on webhook_code if necessary
        return data


# Plaid Item Serializers except for item/get

class ItemSerializer(serializers.Serializer):
    """
    Serializer for the 'item' field in Plaid responses.
    """
    # Define fields as per Plaid's Item object
    available_products = serializers.ListField(
        child=serializers.CharField(),
        help_text="Products available for the Item."
    )
    billed_products = serializers.ListField(
        child=serializers.CharField(),
        help_text="Products billed for the Item."
    )
    consent_expiration_time = serializers.DateTimeField(
        allow_null=True,
        help_text="Time when the Item's consent will expire."
    )
    error = ErrorSerializer(
        allow_null=True,
        help_text="Error object containing error details, if any."
    )
    institution_id = serializers.CharField(
        allow_null=True,
        help_text="The Plaid institution ID associated with the Item."
    )
    item_id = serializers.CharField(
        help_text="A unique ID identifying the Item."
    )
    update_type = serializers.CharField(
        help_text="The type of update for the Item."
    )
    webhook = serializers.CharField(
        allow_null=True,
        help_text="The webhook URL associated with the Item."
    )

class ItemRemoveRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /item/remove endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token associated with the Item to be removed."
    )

class ItemRemoveResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /item/remove endpoint.
    """
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )
    removed = serializers.BooleanField(
        help_text="Indicates if the Item was successfully removed."
    )

class ItemWebhookUpdateRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /item/webhook/update endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token associated with the Item to be updated."
    )
    webhook = serializers.URLField(
        help_text="The new webhook URL to associate with the Item."
    )

class ItemWebhookUpdateResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /item/webhook/update endpoint.
    """
    item = ItemSerializer(
        help_text="The updated Item information."
    )
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )

class ItemPublicTokenExchangeRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /item/public_token/exchange endpoint.
    """
    public_token = serializers.CharField(
        help_text="The public token to exchange for an access token."
    )

class ItemPublicTokenExchangeResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /item/public_token/exchange endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token that can be used for making API calls."
    )
    item_id = serializers.CharField(
        help_text="The Item ID associated with the access token."
    )
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )

class ItemAccessTokenInvalidateRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /item/access_token/invalidate endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token to invalidate."
    )

class ItemAccessTokenInvalidateResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /item/access_token/invalidate endpoint.
    """
    new_access_token = serializers.CharField(
        help_text="A new access token that can be used for making API calls."
    )
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )


# Plaid User Serializers
class UserGetRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /users/get endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token associated with the Item data is being requested for."
    )

class UserNameSerializer(serializers.Serializer):
    """
    Serializer for a user's name information.
    """
    full_name = serializers.CharField(allow_null=True, help_text="Full name of the user.")
    first_name = serializers.CharField(allow_null=True, help_text="First name of the user.")
    last_name = serializers.CharField(allow_null=True, help_text="Last name of the user.")
    middle_name = serializers.CharField(allow_null=True, help_text="Middle name of the user.")
    suffix = serializers.CharField(allow_null=True, help_text="Suffix of the user's name (e.g., Jr., Sr.).")
    prefix = serializers.CharField(allow_null=True, help_text="Prefix of the user's name (e.g., Mr., Ms.).")

class UserEmailSerializer(serializers.Serializer):
    """
    Serializer for a user's email information.
    """
    data = serializers.EmailField(allow_null=True, help_text="Email address of the user.")
    primary = serializers.BooleanField(help_text="Indicates if this is the primary email address.")
    type = serializers.CharField(allow_null=True, help_text="Type of email (e.g., 'work', 'personal').")

class UserPhoneNumberSerializer(serializers.Serializer):
    """
    Serializer for a user's phone number information.
    """
    data = serializers.CharField(allow_null=True, help_text="Phone number of the user.")
    primary = serializers.BooleanField(help_text="Indicates if this is the primary phone number.")
    type = serializers.CharField(allow_null=True, help_text="Type of phone number (e.g., 'mobile', 'home').")

class UserAddressDataSerializer(serializers.Serializer):
    """
    Serializer for the address data within a user's address.
    """
    street = serializers.CharField(allow_null=True, help_text="Street address.")
    city = serializers.CharField(allow_null=True, help_text="City.")
    region = serializers.CharField(allow_null=True, help_text="State or region.")
    postal_code = serializers.CharField(allow_null=True, help_text="Postal code.")
    country = serializers.CharField(allow_null=True, help_text="Country.")

class UserAddressSerializer(serializers.Serializer):
    """
    Serializer for a user's address information.
    """
    data = UserAddressDataSerializer(allow_null=True, help_text="Detailed address information.")
    primary = serializers.BooleanField(help_text="Indicates if this is the primary address.")
    type = serializers.CharField(allow_null=True, help_text="Type of address (e.g., 'home', 'work').")

class UserIdentitySerializer(serializers.Serializer):
    """
    Serializer for the user's identity information.
    """
    names = serializers.ListField(
        child=UserNameSerializer(),
        help_text="List of names associated with the user."
    )
    emails = serializers.ListField(
        child=UserEmailSerializer(),
        help_text="List of email addresses associated with the user."
    )
    phone_numbers = serializers.ListField(
        child=UserPhoneNumberSerializer(),
        help_text="List of phone numbers associated with the user."
    )
    addresses = serializers.ListField(
        child=UserAddressSerializer(),
        help_text="List of addresses associated with the user."
    )

class UserGetResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /users/get endpoint.
    """
    user = UserIdentitySerializer(help_text="User identity information.")
    request_id = serializers.CharField(help_text="A unique identifier for the request, used for troubleshooting.")
    error = ErrorSerializer(allow_null=True, help_text="Error object containing error details, if any.")

# Plaid Transaction Sync Serializers

class TransactionsSyncRequestOptionsSerializer(serializers.Serializer):
    """
    Serializer for the 'options' field in the TransactionsSyncRequest.
    """
    include_personal_finance_category = serializers.BooleanField(
        required=False,
        help_text="Include personal finance category data."
    )
    include_original_description = serializers.BooleanField(
        required=False,
        help_text="Include original description data."
    )

class TransactionsSyncRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /transactions/sync endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token associated with the Item data is being requested for."
    )
    cursor = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Cursor value representing the last update the client has received for the given Item."
    )
    count = serializers.IntegerField(
        required=False,
        help_text="The number of transactions to fetch."
    )
    options = TransactionsSyncRequestOptionsSerializer(
        required=False,
        help_text="Additional options to filter the transactions sync request."
    )

class PaymentMetaSerializer(serializers.Serializer):
    """
    Serializer for the payment meta information of a transaction.
    """
    by_order_of = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The party that ordered payment."
    )
    payee = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The entity being paid."
    )
    payer = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The entity paying."
    )
    payment_method = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Method of payment."
    )
    payment_processor = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Payment processor used."
    )
    ppd_id = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="ACH PPD ID."
    )
    reason = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Reason for payment."
    )
    reference_number = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Payment reference number."
    )

class LocationSerializer(serializers.Serializer):
    """
    Serializer for the location information of a transaction.
    """
    address = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Street address where transaction occurred."
    )
    city = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="City where transaction occurred."
    )
    region = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="State or region where transaction occurred."
    )
    postal_code = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Postal code where transaction occurred."
    )
    country = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Country where transaction occurred."
    )
    lat = serializers.FloatField(
        allow_null=True,
        required=False,
        help_text="Latitude coordinates of transaction location."
    )
    lon = serializers.FloatField(
        allow_null=True,
        required=False,
        help_text="Longitude coordinates of transaction location."
    )
    store_number = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Store number where transaction occurred."
    )

class PersonalFinanceCategorySerializer(serializers.Serializer):
    """
    Serializer for personal finance category information.
    """
    primary = serializers.CharField(
        help_text="The primary personal finance category."
    )
    detailed = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The detailed personal finance category."
    )

class MerchantSerializer(serializers.Serializer):
    """
    Serializer for merchant information.
    """
    name = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The merchant name."
    )
    id = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The merchant ID."
    )

class TransactionCodeSerializer(serializers.Serializer):
    """
    Serializer for transaction code information.
    """
    code = serializers.CharField(
        help_text="The transaction code."
    )
    description = serializers.CharField(
        help_text="The transaction code description."
    )

class SubtransactionSerializer(serializers.Serializer):
    """
    Serializer for subtransactions within a transaction.
    """
    transaction_id = serializers.CharField(
        help_text="The unique ID of the subtransaction."
    )
    amount = serializers.FloatField(
        help_text="The amount of the subtransaction."
    )
    description = serializers.CharField(
        help_text="Description of the subtransaction."
    )
    category = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of categories for the subtransaction."
    )
    category_id = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="ID of the category."
    )

PAYMENT_CHANNEL_CHOICES = (
    ('online', 'online'),
    ('in store', 'in store'),
    ('other', 'other'),
)

TRANSACTION_TYPE_CHOICES = (
    ('digital', 'digital'),
    ('place', 'place'),
    ('special', 'special'),
    ('unresolved', 'unresolved'),
)

class TransactionSerializer(serializers.Serializer):
    """
    Serializer for transaction objects.
    """
    transaction_id = serializers.CharField(
        help_text="The unique ID of the transaction."
    )
    account_id = serializers.CharField(
        help_text="The ID of the account associated with this transaction."
    )
    amount = serializers.FloatField(
        help_text="The settled value of the transaction."
    )
    iso_currency_code = serializers.CharField(
        allow_null=True,
        required=False,
        max_length=3,
        help_text="The ISO-4217 currency code of the transaction."
    )
    unofficial_currency_code = serializers.CharField(
        allow_null=True,
        required=False,
        max_length=3,
        help_text="The unofficial currency code associated with the transaction."
    )
    date = serializers.DateField(
        help_text="The date the transaction was posted."
    )
    authorized_date = serializers.DateField(
        allow_null=True,
        required=False,
        help_text="The date the transaction was authorized."
    )
    pending = serializers.BooleanField(
        help_text="Indicates if the transaction is pending or posted."
    )
    pending_transaction_id = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The ID of the posted transaction corresponding to a pending transaction."
    )
    account_owner = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The account owner."
    )
    merchant_name = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The merchant name."
    )
    name = serializers.CharField(
        help_text="The transaction name."
    )
    original_description = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The original description of the transaction."
    )
    payment_channel = serializers.ChoiceField(
        choices=PAYMENT_CHANNEL_CHOICES,
        help_text="The payment channel of the transaction."
    )
    payment_meta = PaymentMetaSerializer(
        allow_null=True,
        required=False,
        help_text="Additional payment meta information."
    )
    location = LocationSerializer(
        allow_null=True,
        required=False,
        help_text="Location information about the transaction."
    )
    category = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="A hierarchical array of categories."
    )
    category_id = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="The ID of the category."
    )
    transaction_type = serializers.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="The type of transaction."
    )
    personal_finance_category = PersonalFinanceCategorySerializer(
        allow_null=True,
        required=False,
        help_text="The personal finance category of the transaction."
    )
    merchant = MerchantSerializer(
        allow_null=True,
        required=False,
        help_text="Merchant information."
    )
    transaction_code = TransactionCodeSerializer(
        allow_null=True,
        required=False,
        help_text="Transaction code information."
    )
    subtransactions = SubtransactionSerializer(
        many=True,
        required=False,
        help_text="An array of subtransactions associated with this transaction."
    )

class RemovedTransactionSerializer(serializers.Serializer):
    """
    Serializer for removed transaction objects.
    """
    transaction_id = serializers.CharField(
        help_text="The unique ID of the removed transaction."
    )
    account_id = serializers.CharField(
        help_text="The ID of the account associated with the removed transaction."
    )

class TransactionsSyncResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /transactions/sync endpoint.
    """
    added = TransactionSerializer(
        many=True,
        help_text="Transactions that have been added since the last sync."
    )
    modified = TransactionSerializer(
        many=True,
        help_text="Transactions that have been modified since the last sync."
    )
    removed = RemovedTransactionSerializer(
        many=True,
        help_text="Transactions that have been removed since the last sync."
    )
    next_cursor = serializers.CharField(
        help_text="The cursor value to use in the next request to receive updates."
    )
    has_more = serializers.BooleanField(
        help_text="Indicates whether more updates are available."
    )
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )

# Plaid LinkTokenCreate Serializers 

class LinkTokenCreateRequestUserSerializer(serializers.Serializer):
    """
    Serializer for the 'user' field in the LinkTokenCreateRequest.
    """
    client_user_id = serializers.CharField(
        help_text="A unique ID representing the end user. Used for logging and analytics."
    )
    legal_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="The user's full legal name."
    )
    email_address = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text="The user's email address."
    )
    phone_number = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="The user's phone number."
    )
    ssn = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="The user's Social Security Number."
    )
    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="The user's date of birth."
    )
    # Additional optional fields can be added here as needed.

class LinkTokenCreateRequestAccountFiltersSerializer(serializers.Serializer):
    """
    Serializer for the 'account_filters' field in the LinkTokenCreateRequest.
    """
    depository = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        required=False,
        help_text="Filters for depository accounts."
    )
    credit = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        required=False,
        help_text="Filters for credit accounts."
    )
    # Add other account types if needed.

class LinkTokenCreateRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /link/token/create endpoint.
    """
    client_name = serializers.CharField(
        help_text="The name of your application."
    )
    language = serializers.CharField(
        help_text="The language that Link should be displayed in."
    )
    country_codes = serializers.ListField(
        child=serializers.CharField(max_length=2),
        help_text="List of country codes supported by your application."
    )
    user = LinkTokenCreateRequestUserSerializer(
        help_text="An object containing information about the end user."
    )
    products = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of Plaid products to use."
    )
    webhook = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="The webhook URL to receive notifications."
    )
    link_customization_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="The name of the customization to apply to Link."
    )
    account_filters = LinkTokenCreateRequestAccountFiltersSerializer(
        required=False,
        allow_null=True,
        help_text="Filters to apply to the accounts shown in Link."
    )
    access_token = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="An access token associated with an Item to modify."
    )
    redirect_uri = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="The redirect URI to be used upon completion of the Link flow."
    )
    android_package_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="The Android package name to redirect to upon completion."
    )
    # Additional optional fields can be added here as needed.

class LinkTokenCreateResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data received from /link/token/create endpoint.
    """
    link_token = serializers.CharField(
        help_text="A link_token that can be used to initialize Link."
    )
    expiration = serializers.DateTimeField(
        help_text="The expiration time of the link_token."
    )
    request_id = serializers.CharField(
        help_text="A unique identifier for the request, used for troubleshooting."
    )