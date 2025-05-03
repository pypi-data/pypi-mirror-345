#!/usr/bin/env python
"""
Tests for FastJango middleware functionality.
"""

import os
import sys
import asyncio
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path if script is run from tests directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FastJango middleware components
from fastapi import FastAPI, Request, Response
from fastjango.middleware.cors import CORSMiddleware
from fastjango.middleware.security import SecurityMiddleware
from fastjango.http import HttpResponse


class TestMiddleware:
    """A test middleware for unit testing."""
    
    def __init__(self, app, option=None):
        self.app = app
        self.option = option
        self.calls = []
    
    async def __call__(self, scope, receive, send):
        self.calls.append(("enter", scope["path"]))
        
        # Modify request
        if scope.get("path") == "/modified":
            scope["modified_by_middleware"] = True
        
        # Call the next middleware or endpoint
        await self.app(scope, receive, send)
        
        self.calls.append(("exit", scope["path"]))


class MiddlewareTest(unittest.TestCase):
    """Test suite for middleware functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = FastAPI()
        
        @self.app.get("/")
        async def index():
            return {"message": "Hello World"}
        
        @self.app.get("/modified")
        async def modified(request: Request):
            is_modified = getattr(request.scope, "modified_by_middleware", False)
            return {"modified": is_modified}
    
    def test_middleware_execution(self):
        """Test that middleware is executed in the correct order."""
        test_middleware = TestMiddleware(self.app)
        app_with_middleware = TestMiddleware(test_middleware)
        
        # Create mock scope, receive, and send
        scope = {"type": "http", "path": "/"}
        receive = MagicMock()
        send = MagicMock()
        
        # Run the middleware chain
        asyncio.run(app_with_middleware(scope, receive, send))
        
        # Check the call order
        expected_calls = [
            ("enter", "/"),  # Outer middleware enters
            ("enter", "/"),  # Inner middleware enters
            ("exit", "/"),   # Inner middleware exits
            ("exit", "/")    # Outer middleware exits
        ]
        self.assertEqual(app_with_middleware.calls + test_middleware.calls, expected_calls)
    
    def test_middleware_modifies_request(self):
        """Test that middleware can modify the request."""
        # Add the test middleware to the app
        self.app.add_middleware(TestMiddleware)
        
        # Create test client
        from fastapi.testclient import TestClient
        client = TestClient(self.app)
        
        # Make request to the modified endpoint
        response = client.get("/modified")
        
        # The middleware should have set modified_by_middleware=True
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"modified": True})


class CORSMiddlewareTest(unittest.TestCase):
    """Test suite for CORS middleware."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = FastAPI()
        
        @self.app.get("/")
        async def index():
            return {"message": "Hello World"}
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://example.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["X-Custom"],
        )
        
        # Create test client
        from fastapi.testclient import TestClient
        self.client = TestClient(self.app)
    
    def test_cors_headers_preflight(self):
        """Test CORS headers are added to preflight requests."""
        response = self.client.options(
            "/",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Custom",
            },
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://example.com")
        self.assertEqual(response.headers["access-control-allow-credentials"], "true")
        self.assertEqual(response.headers["access-control-allow-methods"], "GET,POST")
        self.assertEqual(response.headers["access-control-allow-headers"], "X-Custom")
    
    def test_cors_headers_simple_request(self):
        """Test CORS headers are added to simple requests."""
        response = self.client.get("/", headers={"Origin": "https://example.com"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://example.com")
        self.assertEqual(response.headers["access-control-allow-credentials"], "true")


class SecurityMiddlewareTest(unittest.TestCase):
    """Test suite for security middleware."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = FastAPI()
        
        @self.app.get("/")
        async def index():
            return {"message": "Hello World"}
        
        # Add security middleware
        self.app.add_middleware(
            SecurityMiddleware,
            enable_hsts=True,
            hsts_max_age=31536000,
            enable_xss_protection=True,
        )
        
        # Create test client
        from fastapi.testclient import TestClient
        self.client = TestClient(self.app)
    
    def test_security_headers(self):
        """Test security headers are added to responses."""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["strict-transport-security"],
            f"max-age=31536000; includeSubDomains"
        )
        self.assertEqual(response.headers["x-xss-protection"], "1; mode=block")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")


def run_tests():
    """Run the middleware tests."""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests() 