"""
Tests for API documentation endpoints.
"""
import os
import yaml
from django.test import TestCase, Client


class APIDocumentationTestCase(TestCase):
    """Test API documentation endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_schema_endpoint_accessible(self):
        """Test that OpenAPI schema endpoint is accessible."""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('openapi', response.json())

    def test_swagger_ui_endpoint_accessible(self):
        """Test that Swagger UI endpoint is accessible."""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('swagger-ui', response.content.decode('utf-8').lower())

    def test_redoc_endpoint_accessible(self):
        """Test that ReDoc endpoint is accessible."""
        response = self.client.get('/api/docs/redoc/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('redoc', content.lower())

    def test_schema_contains_title(self):
        """Test that schema contains API title."""
        response = self.client.get('/api/schema/')
        schema = response.json()
        self.assertIn('info', schema)
        self.assertIn('title', schema['info'])

    def test_schema_contains_paths(self):
        """Test that schema contains API paths."""
        response = self.client.get('/api/schema/')
        schema = response.json()
        self.assertIn('paths', schema)
        # Verify at least some endpoints are documented
        self.assertGreater(len(schema['paths']), 0)

    def test_schema_documents_cities_endpoint(self):
        """Test that schema documents cities endpoint."""
        response = self.client.get('/api/schema/')
        schema = response.json()
        paths = schema.get('paths', {})
        # Look for cities endpoint
        cities_endpoints = [p for p in paths.keys() if 'cities' in p]
        self.assertGreater(len(cities_endpoints), 0)

    def test_asyncapi_file_exists(self):
        """Test that AsyncAPI spec file exists."""
        asyncapi_path = '/vagrant/app/docs/asyncapi.yaml'
        self.assertTrue(os.path.exists(asyncapi_path))

    def test_asyncapi_file_is_valid_yaml(self):
        """Test that AsyncAPI spec is valid YAML."""
        asyncapi_path = '/vagrant/app/docs/asyncapi.yaml'
        try:
            with open(asyncapi_path, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.fail(f'AsyncAPI file is not valid YAML: {e}')

    def test_asyncapi_contains_required_keys(self):
        """Test that AsyncAPI spec contains required 2.6 keys."""
        asyncapi_path = '/vagrant/app/docs/asyncapi.yaml'
        with open(asyncapi_path, 'r') as f:
            spec = yaml.safe_load(f)

        # Required AsyncAPI 2.6 fields
        self.assertIn('asyncapi', spec)
        self.assertIn('info', spec)
        self.assertIn('channels', spec)
        self.assertIn('components', spec)

        # Verify version format
        self.assertEqual(spec['asyncapi'], '2.6.0')

    def test_asyncapi_documents_alerts_channels(self):
        """Test that AsyncAPI documents WebSocket alert channels."""
        asyncapi_path = '/vagrant/app/docs/asyncapi.yaml'
        with open(asyncapi_path, 'r') as f:
            spec = yaml.safe_load(f)

        channels = spec.get('channels', {})
        # Should have both general and city-specific channels
        self.assertIn('/ws/alerts/', channels)
        self.assertIn('/ws/alerts/{city_uuid}', channels)

    def test_asyncapi_contains_message_schemas(self):
        """Test that AsyncAPI contains message schemas."""
        asyncapi_path = '/vagrant/app/docs/asyncapi.yaml'
        with open(asyncapi_path, 'r') as f:
            spec = yaml.safe_load(f)

        components = spec.get('components', {})
        messages = components.get('messages', {})
        self.assertIn('WeatherAlert', messages)

        # Verify message schema properties
        alert_message = messages['WeatherAlert']
        self.assertIn('payload', alert_message)
        payload = alert_message['payload']
        self.assertIn('properties', payload)
        properties = payload['properties']
        self.assertIn('type', properties)
        self.assertIn('city', properties)
        self.assertIn('alert_type', properties)
        self.assertIn('severity', properties)

    def test_asyncapi_has_server_info(self):
        """Test that AsyncAPI includes server information."""
        asyncapi_path = '/vagrant/app/docs/asyncapi.yaml'
        with open(asyncapi_path, 'r') as f:
            spec = yaml.safe_load(f)

        self.assertIn('servers', spec)
        servers = spec['servers']
        # Should have development and production servers
        self.assertIn('development', servers)
        self.assertIn('production', servers)


class TLSDocumentationTestCase(TestCase):
    """Test that documentation files are in place for TLS."""

    def test_generate_certs_script_exists(self):
        """Test that certificate generation script exists."""
        cert_script = '/vagrant/app/scripts/generate_certs.sh'
        self.assertTrue(os.path.exists(cert_script))

    def test_generate_certs_script_is_executable(self):
        """Test that certificate generation script is executable."""
        cert_script = '/vagrant/app/scripts/generate_certs.sh'
        import stat
        st = os.stat(cert_script)
        is_executable = bool(st.st_mode & stat.S_IXUSR)
        self.assertTrue(is_executable)

    def test_docs_directory_exists(self):
        """Test that docs directory exists."""
        docs_dir = '/vagrant/app/docs'
        self.assertTrue(os.path.isdir(docs_dir))
