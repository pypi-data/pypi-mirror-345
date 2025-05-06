import logging
import tempfile
from pathlib import Path

from commons.network import IPV4_LOOPBACK
from pydantic_core import SchemaValidator

TEMP_FOLDER: Path = Path(tempfile.gettempdir())


import unittest
from pathlib import Path
from pydantic import BaseModel
from webserver.config import Settings, env


class TestSettings(unittest.TestCase):
    @staticmethod
    def check_schema(model: BaseModel):
        schema_validator = SchemaValidator(schema=model.__pydantic_core_schema__)
        return schema_validator.validate_python(model.__dict__)

    def test_default_settings(self):
        # Test default values
        settings = Settings()
        self.assertEqual(settings.APP_NAME, "fastapi.webserver")
        self.assertEqual(settings.ENVIRONMENT, "local")
        self.assertEqual(settings.RESOURCES_FOLDER, env.root())
        self.assertEqual(settings.HTTP_ROOT_PATH, '/')
        self.assertEqual(settings.STATIC_FOLDER, "")
        self.assertEqual(settings.HOST, IPV4_LOOPBACK)
        self.assertEqual(settings.PORT, 8000)
        self.assertEqual(settings.ENABLE_SSL, False)
        self.assertEqual(settings.SSL_CERTIFICATE, "")
        self.assertEqual(settings.SSL_PRIVATE_KEY, "")
        self.assertEqual(settings.CORS_ORIGINS, [])
        self.assertEqual(settings.TEMPLATES_FOLDER, "")
        self.assertEqual(settings.SUPPORTED_LOCALES, [])
        self.assertEqual(settings.MODULES, [])
        self.assertEqual(settings.DB_ENGINE, "")
        self.assertEqual(settings.DB_SERVER, "")
        self.assertEqual(settings.DB_PORT, None)
        self.assertEqual(settings.DB_USER, None)
        self.assertEqual(settings.DB_PASSWORD, None)
        self.assertEqual(settings.DB_NAME, "")
        self.assertEqual(settings.SMTP_TLS, True)
        self.assertEqual(settings.SMTP_SSL, False)
        self.assertEqual(settings.SMTP_PORT, 587)
        self.assertEqual(settings.SMTP_HOST, None)
        self.assertEqual(settings.SMTP_USER, None)
        self.assertEqual(settings.SMTP_PASSWORD, None)
        self.assertEqual(settings.EMAILS_FROM_EMAIL, None)
        self.assertEqual(settings.EMAILS_FROM_NAME, settings.APP_NAME)

    def test_resources_folder_validation_success(self):
        # Test successful validation of RESOURCES_FOLDER
        settings = Settings()
        valid_path = str(Path(__file__).parent)
        settings.RESOURCES_FOLDER = valid_path
        self.assertEqual(settings.RESOURCES_FOLDER, valid_path)

    def test_resources_folder_validation_failure(self):
        # Test failure validation of RESOURCES_FOLDER
        settings = Settings()
        invalid_path = "/invalid/path"
        with self.assertRaises(ValueError) as context:
            settings.RESOURCES_FOLDER = invalid_path
            self.check_schema(settings)
        self.assertIn(f"'{invalid_path}' does not exists.", str(context.exception))

    def test_log_config_success(self):
        settings = Settings()

        for k, v in {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
            # keys as int
            logging.DEBUG: logging.DEBUG,
            logging.INFO: logging.INFO,
            logging.WARNING: logging.WARNING,
            logging.ERROR: logging.ERROR
        }.items():
            settings.LOG_LEVEL = k
            settings = self.check_schema(settings)
            self.assertEqual(settings.LOG_LEVEL, v)

    def test_log_config_failure(self):
        settings = Settings()
        with self.assertRaises(ValueError) as context:
            settings.LOG_LEVEL = 100
            self.check_schema(settings)
        self.assertIn("Log level must be between 0 and 50. "
                      "See https://docs.python.org/3/library/logging.html#logging-levels", str(context.exception))
        with self.assertRaises(ValueError) as context:
            settings.LOG_LEVEL = "INVALID"
            self.check_schema(settings)
        self.assertIn("Log level is invalid.", str(context.exception))

    def test_ssl_certificate_validation_success(self):
        # Test successful validation of SSL_CERTIFICATE
        settings = Settings()
        valid_path = str(Path(__file__).parent)
        settings.SSL_CERTIFICATE = valid_path
        self.assertEqual(settings.SSL_CERTIFICATE, valid_path)

    def test_ssl_certificate_validation_failure(self):
        # Test failure validation of SSL_CERTIFICATE
        settings = Settings()
        invalid_path = "/invalid/path"
        with self.assertRaises(ValueError) as context:
            settings.SSL_CERTIFICATE = invalid_path
            self.check_schema(settings)
        self.assertIn(f"'{invalid_path}' does not exists.", str(context.exception))

    def test_ssl_private_key_validation_success(self):
        # Test successful validation of SSL_PRIVATE_KEY
        settings = Settings()
        valid_path = str(Path(__file__).parent)
        settings.SSL_PRIVATE_KEY = valid_path
        self.assertEqual(settings.SSL_PRIVATE_KEY, valid_path)

    def test_ssl_private_key_validation_failure(self):
        # Test failure validation of SSL_PRIVATE_KEY
        settings = Settings()
        invalid_path = "/invalid/path"
        with self.assertRaises(ValueError) as context:
            settings.SSL_PRIVATE_KEY = invalid_path
            self.check_schema(settings)
        self.assertIn(f"'{invalid_path}' does not exists.", str(context.exception))

    def test_base_url_with_ssl(self):
        # Test base_url computation with SSL enabled
        settings = Settings()
        settings.ENABLE_SSL = True
        settings.HOST = "127.0.0.1"
        settings.PORT = 8443
        self.assertEqual(settings.base_url, "https://127.0.0.1:8443/")

    def test_base_url_without_ssl(self):
        # Test base_url computation without SSL
        settings = Settings()
        settings.ENABLE_SSL = False
        settings.HOST = "localhost"
        settings.PORT = 8080
        self.assertEqual(settings.base_url, "http://localhost:8080/")

    def test_enable_ssl_computed_field(self):
        # Test enable_ssl computed field
        settings = Settings()
        settings.SSL_CERTIFICATE = str(Path(__file__).parent)
        settings.SSL_PRIVATE_KEY = str(Path(__file__).parent)
        self.assertTrue(settings.enable_ssl)

    def test_http_static_enabled_computed_field(self):
        # Test http_static_enabled computed field
        settings = Settings()
        settings.RESOURCES_FOLDER = str(Path(__file__).parent)
        settings.STATIC_FOLDER = "static"
        self.assertTrue(settings.http_static_enabled)

    def test_templates_enabled_computed_field(self):
        # Test templates_enabled computed field
        settings = Settings()
        settings.RESOURCES_FOLDER = str(Path(__file__).parent)
        settings.TEMPLATES_FOLDER = "templates"
        self.assertTrue(settings.templates_enabled)

    def test_has_database_computed_field(self):
        # Test has_database computed field
        settings = Settings()
        settings.DB_ENGINE = "sqlite"
        settings.DB_NAME = "test.db"
        self.assertTrue(settings.has_database)

    def test_emails_enabled_computed_field(self):
        # Test emails_enabled computed field
        settings = Settings()
        settings.SMTP_HOST = "smtp.example.com"
        settings.EMAILS_FROM_EMAIL = "test@example.com"
        settings.SMTP_USER = "test@example.com"
        settings.SMTP_PASSWORD = "123456789abc"
        self.assertTrue(settings.emails_enabled)

    def test_locale_config_computed_field(self):
        # Test locale_config computed field
        settings = Settings()
        settings.SUPPORTED_LOCALES = ["en", "fr"]
        self.assertIsNotNone(settings.locale_config)

    def test_database_adapter_computed_field(self):
        # Test database_adapter computed field
        settings = Settings()
        settings.DB_ENGINE = "sqlite"
        settings.DB_NAME = "test.db"
        self.assertIsNotNone(settings.database_adapter)

    def test_cache_database_adapter_computed_field(self):
        # Test cache_database_adapter computed field
        settings = Settings()
        settings.RESOURCES_FOLDER = str(Path(__file__).parent)
        self.assertIsNotNone(settings.cache_database_adapter)

    def test_smtp_config_computed_field(self):
        # Test smtp_config computed field
        settings = Settings()
        settings.SMTP_HOST = "smtp.example.com"
        settings.EMAILS_FROM_EMAIL = "test@example.com"
        settings.SMTP_USER = "test@example.com"
        settings.SMTP_PASSWORD = "123456789abc"
        self.assertIsNotNone(settings.smtp_config)
