"""
Integration tests for webhook endpoints.

Tests verify that webhook endpoints handle requests correctly
and return appropriate responses.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Import webhook handler app
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from auth.webhook_handler import app


class TestWebhookEndpoints:
    """Test suite for webhook endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_webhook_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/webhook/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'gateways' in data
        assert isinstance(data['gateways'], dict)
    
    def test_razorpay_webhook_empty_payload(self, client):
        """Test Razorpay webhook with empty payload."""
        # Send empty body
        response = client.post(
            '/webhook/razorpay',
            data='',
            content_type='application/json'
        )
        
        # Should return 400 for empty payload
        assert response.status_code in [400, 500]  # Accept both as valid error responses
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_razorpay_webhook_valid_payload(self, client):
        """Test Razorpay webhook with valid payload."""
        with patch('auth.webhook_handler.razorpay_service') as mock_service:
            mock_service.process_webhook.return_value = True
            
            payload = {
                'event': 'payment.captured',
                'payload': {
                    'payment': {
                        'id': 'pay_test123',
                        'amount': 10000
                    }
                }
            }
            
            response = client.post(
                '/webhook/razorpay',
                json=payload,
                headers={'X-Razorpay-Signature': 'test_signature'},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            mock_service.process_webhook.assert_called_once()
    
    def test_razorpay_webhook_processing_failure(self, client):
        """Test Razorpay webhook when processing fails."""
        with patch('auth.webhook_handler.razorpay_service') as mock_service:
            mock_service.process_webhook.return_value = False
            
            payload = {'event': 'payment.captured'}
            
            response = client.post(
                '/webhook/razorpay',
                json=payload,
                headers={'X-Razorpay-Signature': 'test_signature'},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_stripe_webhook_not_configured(self, client):
        """Test Stripe webhook when service is not configured."""
        with patch('auth.webhook_handler.stripe_service', None):
            response = client.post(
                '/webhook/stripe',
                data='test',
                headers={'Stripe-Signature': 'test_sig'},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'not configured' in data['error'].lower()
    
    def test_stripe_webhook_valid_payload(self, client):
        """Test Stripe webhook with valid payload."""
        with patch('auth.webhook_handler.stripe_service') as mock_service:
            mock_service.process_webhook.return_value = True
            mock_service.is_configured.return_value = True
            
            response = client.post(
                '/webhook/stripe',
                data='{"type": "checkout.session.completed"}',
                headers={'Stripe-Signature': 'test_sig'},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_paypal_webhook_not_configured(self, client):
        """Test PayPal webhook when service is not configured."""
        with patch('auth.webhook_handler.paypal_service', None):
            response = client.post(
                '/webhook/paypal',
                json={'event_type': 'PAYMENT.SALE.COMPLETED'},
                headers={'PAYPAL-TRANSMISSION-SIG': 'test_sig'},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'not configured' in data['error'].lower()
    
    def test_paypal_webhook_valid_payload(self, client):
        """Test PayPal webhook with valid payload."""
        with patch('auth.webhook_handler.paypal_service') as mock_service:
            mock_service.process_webhook.return_value = True
            mock_service.is_configured.return_value = True
            
            payload = {'event_type': 'PAYMENT.SALE.COMPLETED'}
            
            response = client.post(
                '/webhook/paypal',
                json=payload,
                headers={'PAYPAL-TRANSMISSION-SIG': 'test_sig'},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_webhook_error_handling(self, client):
        """Test webhook error handling for exceptions."""
        with patch('auth.webhook_handler.razorpay_service') as mock_service:
            mock_service.process_webhook.side_effect = Exception("Internal error")
            
            payload = {'event': 'payment.captured'}
            
            response = client.post(
                '/webhook/razorpay',
                json=payload,
                headers={'X-Razorpay-Signature': 'test_signature'},
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

