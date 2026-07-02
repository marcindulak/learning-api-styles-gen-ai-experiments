@status-done
Feature: NFR-002 Service requests can be encrypted or unencrypted
  The service can serve requests over plain HTTP or over TLS-encrypted
  HTTPS, controlled by the TLS_ENABLE environment variable.

  Scenario: Service serves unencrypted HTTP requests when TLS is disabled
    Given the service is running with the environment variable "TLS_ENABLE" set to "0"
    When a client sends a GET request to "http://localhost:8000/api/health"
    Then the response status code is 200

  Scenario: Service serves TLS-encrypted requests when TLS is enabled
    Given the service is running with the environment variable "TLS_ENABLE" set to "1"
    And a self-signed TLS certificate has been generated in the container
    When a client sends a GET request to "https://localhost:8000/api/health" accepting the self-signed certificate
    Then the response status code is 200
    And the connection is encrypted with TLS version 1.2 or higher

  Scenario: TLS certificate and key are stored in the configured directories
    Given the service is running with the environment variable "TLS_ENABLE" set to "1"
    Then a certificate file exists in the directory given by the environment variable "APP_TLS_CERTS_DIR"
    And a private key file exists in the directory given by the environment variable "APP_TLS_PRICATE_DIR"
