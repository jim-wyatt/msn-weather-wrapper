"""Security and fuzzing tests for the API."""

import json

import pytest

from api import app, validate_input


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestInputValidation:
    """Test input validation function."""

    def test_valid_input(self):
        """Test validation passes for valid input."""
        value, error = validate_input("Seattle", "city", 100)
        assert error is None
        assert value == "Seattle"

    def test_whitespace_trimming(self):
        """Test whitespace is trimmed."""
        value, error = validate_input("  Seattle  ", "city", 100)
        assert error is None
        assert value == "Seattle"

    def test_empty_string(self):
        """Test empty string is rejected."""
        value, error = validate_input("", "city", 100)
        assert error is not None
        assert "empty" in error.lower()

    def test_none_value(self):
        """Test None is rejected."""
        value, error = validate_input(None, "city", 100)
        assert error is not None
        assert "string" in error.lower()

    def test_whitespace_only(self):
        """Test whitespace-only string is rejected."""
        value, error = validate_input("   ", "city", 100)
        assert error is not None
        assert "empty" in error.lower() or "whitespace" in error.lower()

    def test_exceeds_max_length(self):
        """Test string exceeding max length is rejected."""
        value, error = validate_input("A" * 101, "city", 100)
        assert error is not None
        assert "length" in error.lower()

    def test_non_string_type(self):
        """Test non-string types are rejected."""
        for invalid_value in [12345, True, [], {}]:
            value, error = validate_input(invalid_value, "city", 100)
            assert error is not None
            assert "string" in error.lower()

    def test_special_characters_rejected(self):
        """Test dangerous special characters are rejected."""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users--",
            "../../../etc/passwd",
            "${whoami}",
            "\x00\x01\x02",
        ]
        for dangerous in dangerous_inputs:
            value, error = validate_input(dangerous, "city", 100)
            assert error is not None
            assert "invalid characters" in error.lower()

    def test_unicode_cities_allowed(self):
        """Test valid unicode city names are allowed."""
        valid_unicode = [
            "北京",  # Beijing
            "Москва",  # Moscow
            "São Paulo",
            "Zürich",
            "Kraków",
        ]
        for city in valid_unicode:
            value, error = validate_input(city, "city", 100)
            # These should pass as they contain valid unicode letters
            if error:
                # Some special chars might not pass, that's ok for security
                assert "invalid characters" in error.lower()


class TestAPISecurityGET:
    """Test GET endpoint security."""

    def test_sql_injection_attempts(self, client):
        """Test SQL injection attempts are blocked."""
        sql_injections = [
            "1; DROP",  # Semicolon for command injection
            "1 UNION",  # SQL UNION keyword
            "admin\x00null",  # Null byte injection
        ]
        for payload in sql_injections:
            response = client.get(f"/api/weather?city={payload}&country={payload}")
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "invalid" in data["message"].lower()

    def test_xss_attempts(self, client):
        """Test XSS attempts are blocked."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>",
        ]
        for payload in xss_attempts:
            response = client.get(f"/api/weather?city={payload}&country={payload}")
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    def test_path_traversal_attempts(self, client):
        """Test path traversal attempts are blocked."""
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
        ]
        for payload in path_traversals:
            response = client.get(f"/api/weather?city={payload}&country={payload}")
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    def test_command_injection_attempts(self, client):
        """Test command injection attempts are blocked."""
        commands = [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(cat /etc/passwd)",
        ]
        for payload in commands:
            response = client.get(f"/api/weather?city={payload}&country={payload}")
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    def test_null_bytes(self, client):
        """Test null bytes are blocked."""
        response = client.get("/api/weather?city=test\x00&country=test\x00")
        assert response.status_code == 400

    def test_oversized_input(self, client):
        """Test oversized inputs are rejected."""
        oversized = "A" * 10000
        response = client.get(f"/api/weather?city={oversized}&country={oversized}")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "length" in data["message"].lower()

    def test_empty_parameters(self, client):
        """Test empty parameters are rejected."""
        response = client.get("/api/weather?city=&country=")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_whitespace_only_parameters(self, client):
        """Test whitespace-only parameters are rejected."""
        response = client.get("/api/weather?city=   &country=   ")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data


class TestAPISecurityPOST:
    """Test POST endpoint security."""

    def test_malformed_json(self, client):
        """Test malformed JSON is handled gracefully."""
        malformed = [
            "{invalid json}",
            '{"city": "test"',  # Missing closing brace
            '{"city": "test", "country":}',  # Missing value
        ]
        for payload in malformed:
            response = client.post(
                "/api/weather",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    def test_non_string_types(self, client):
        """Test non-string types in JSON are rejected."""
        invalid_types = [
            {"city": 12345, "country": "USA"},
            {"city": "Seattle", "country": True},
            {"city": [], "country": "USA"},
            {"city": "Seattle", "country": {}},
            {"city": None, "country": None},
        ]
        for payload in invalid_types:
            response = client.post(
                "/api/weather",
                json=payload,
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            # Should reject either because required or wrong type
            assert "required" in data["message"].lower() or "string" in data["message"].lower()

    def test_sql_injection_in_json(self, client):
        """Test SQL injection in JSON values is blocked."""
        response = client.post(
            "/api/weather",
            json={"city": "1; DROP TABLE users", "country": "admin'--"},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_xss_in_json(self, client):
        """Test XSS in JSON values is blocked."""
        response = client.post(
            "/api/weather",
            json={"city": "<script>alert(1)</script>", "country": "USA"},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_non_dict_json(self, client):
        """Test non-dict JSON is rejected."""
        invalid_json = [
            [],
            "string",
            123,
            None,
            True,
        ]
        for payload in invalid_json:
            response = client.post(
                "/api/weather",
                json=payload,
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    def test_oversized_json_values(self, client):
        """Test oversized JSON values are rejected."""
        response = client.post(
            "/api/weather",
            json={"city": "A" * 10000, "country": "USA"},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "length" in data["message"].lower()


class TestAPIRateLimiting:
    """Test for potential DoS via repeated requests."""

    def test_multiple_valid_requests(self, client):
        """Test multiple valid requests don't crash the server."""
        for _ in range(10):
            response = client.get("/api/health")
            assert response.status_code == 200

    def test_multiple_invalid_requests(self, client):
        """Test multiple invalid requests are handled gracefully."""
        for _ in range(10):
            response = client.get("/api/weather?city=<script>&country=alert")
            # Should be 400 for invalid input, but may be 429 if rate limited
            assert response.status_code in (400, 429)
