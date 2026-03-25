"""
CloudEvent signing and verification using JWS.

Provides utilities for creating and validating signed CloudEvents
using JSON Web Signatures (JWS) with RS256 algorithm.
"""

import json
from typing import Any

from cloudevents.http import CloudEvent, to_json
from jwcrypto import jwk, jws
from jwcrypto.common import json_decode, json_encode


class CloudEventHandler:
    """Handle CloudEvent signing and verification."""
    
    def __init__(self, signing_key_pem: str, verification_key_pem: str):
        """
        Initialize CloudEvent handler.
        
        Args:
            signing_key_pem: Private key in PEM format for signing
            verification_key_pem: Public key in PEM format for verification
        """
        self.signing_key = jwk.JWK.from_pem(signing_key_pem.encode())
        self.verification_key = jwk.JWK.from_pem(verification_key_pem.encode())
    
    def sign_event(self, event: CloudEvent) -> str:
        """
        Sign a CloudEvent and return JWS compact serialization.
        
        Args:
            event: CloudEvent to sign
            
        Returns:
            JWS token (compact serialization)
        """
        # Serialize CloudEvent to JSON
        event_json = to_json(event)
        
        # Create JWS token
        token = jws.JWS(event_json)
        token.add_signature(
            self.signing_key,
            alg="RS256",
            protected=json_encode({"alg": "RS256", "typ": "JWT"}),
        )
        
        return token.serialize(compact=True)
    
    def verify_and_extract(self, jws_token: str) -> CloudEvent:
        """
        Verify JWS signature and extract CloudEvent.
        
        Args:
            jws_token: JWS token in compact serialization
            
        Returns:
            Verified CloudEvent
            
        Raises:
            ValueError: If signature verification fails
        """
        try:
            # Create JWS object from token
            token = jws.JWS()
            token.deserialize(jws_token)
            
            # Verify signature
            token.verify(self.verification_key)
            
            # Extract payload
            payload = token.payload.decode("utf-8")
            event_dict = json.loads(payload)
            
            # Reconstruct CloudEvent
            return CloudEvent(event_dict)
            
        except Exception as e:
            raise ValueError(f"CloudEvent verification failed: {e}") from e
    
    def create_event(
        self,
        event_type: str,
        source: str,
        data: dict[str, Any],
        subject: str | None = None,
    ) -> CloudEvent:
        """
        Create a new CloudEvent.
        
        Args:
            event_type: Event type (e.g., 'com.example.order.created')
            source: Event source (e.g., 'https://example.com/orders')
            data: Event data payload
            subject: Optional subject
            
        Returns:
            CloudEvent instance
        """
        attributes = {
            "type": event_type,
            "source": source,
        }
        
        if subject:
            attributes["subject"] = subject
        
        return CloudEvent(attributes, data)
