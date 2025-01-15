from django.core.exceptions import ValidationError
from rest_framework import serializers
from .errorSerializer import ErrorSerializer


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

# item/get

class ItemGetResponseStatusTransactionsSerializer(serializers.Serializer):
    """
    Serializer for the transactions field in ItemGetResponseStatusSerializer
    """
    lastSuccessfulUpdate = serializers.DateTimeField()
    lastFailedUpdate = serializers.DateTimeField()

class ItemGetResponseStatusLastWebhookSerializer(serializers.Serializer):
    """
    Serializer for the last_webhook field in ItemGetResponseStatusSerializer
    """
    sentAt = serializers.DateTimeField()
    codSent = serializers.CharField()

class ItemGetResponseStatusSerializer(serializers.Serializer):
    """
    Serializer for the status field in ItemGetResponseSerializer
    """
    transactions = ItemGetResponseStatusTransactionsSerializer(
        allow_null=True,
        help_text="last successful and failed transactions update for the Item"
    )
    lastWebhook = ItemGetResponseStatusLastWebhookSerializer(
        allow_null=True,
        help_text="last webhook fired for the Item"
    )

class ItemGetRequestSerializer(serializers.Serializer):
    """
    Serializer for the request data sent to /item/get endpoint.
    """
    access_token = serializers.CharField(
        help_text="The access token associated with the Item to be updated."
    )

class ItemGetResponseSerializer(serializers.Serializer):
    """
    Serializer for the response data sent to /item/get endpoint.
    """
    item = ItemSerializer(
        allow_null=True,
        help_text="Metadata about the Item"
    )
    status = ItemGetResponseStatusSerializer(
        allow_null=True,
        help_text="the last successful and failed transactions update for the Item"
    )
    requestId = serializers.CharField(
        help_text = "unique identifier for the request"
    )

# item/remove requests

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

# item/webhook/update

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


# /item/public_token/exchange

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


# /item/access_token/invalidate

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


