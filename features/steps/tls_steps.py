"""Steps for TLS-encrypted and unencrypted service modes (NFR-002).

The scenarios run inside the "django-app" container, in the same
container as the served application. scripts/startup.sh supervises the
server process and re-reads the TLS mode (TLS_ENABLE, overridable via
RUN_DIR/tls_enable) whenever the server process exits, so these steps
switch modes by writing the override file and killing the pid in
RUN_DIR/server.pid. Every switch registers a cleanup restoring the
container's default mode, so the other features always see the plain
HTTP service they expect.
"""
import os
import re
import signal
import socket
import ssl
import subprocess
import time
from pathlib import Path
from urllib.parse import urlsplit

import parse
import requests
from behave import given, register_type, then, when


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)

RUN_DIR = Path("/tmp/wfs")
MODE_FILE = RUN_DIR / "tls_enable"
PID_FILE = RUN_DIR / "server.pid"
SERVICE_HOST = "localhost"
SERVICE_PORT = 8000


def certificate_path():
    return Path(os.environ["APP_TLS_CERTS_DIR"]) / "wfs.crt"


def effective_tls_mode():
    if MODE_FILE.exists():
        return MODE_FILE.read_text().strip()
    return os.environ.get("TLS_ENABLE", "0")


def health_check(tls_mode, timeout=2):
    if tls_mode == "1":
        url = f"https://{SERVICE_HOST}:{SERVICE_PORT}/api/health"
        verify = str(certificate_path())
    else:
        url = f"http://{SERVICE_HOST}:{SERVICE_PORT}/api/health"
        verify = True
    return requests.get(url, timeout=timeout, verify=verify)


def server_answers(tls_mode):
    # A plain-HTTP request to a TLS socket (and vice versa) fails the
    # handshake, so a 200 proves the server runs in the wanted mode.
    try:
        return health_check(tls_mode).status_code == 200
    except (requests.RequestException, OSError):
        return False


def restart_server():
    os.kill(int(PID_FILE.read_text()), signal.SIGTERM)


def wait_for_mode(tls_mode, attempts=60):
    if tls_mode == "1":
        wait_for_certificate()
    for _ in range(attempts):
        if server_answers(tls_mode):
            return
        time.sleep(1)
    raise AssertionError(
        f"service did not come up with TLS mode {tls_mode} "
        f"after {attempts} seconds"
    )


def wait_for_certificate(attempts=30):
    for _ in range(attempts):
        if certificate_path().is_file():
            return
        time.sleep(1)
    raise AssertionError(f"no certificate appeared at {certificate_path()}")


def restore_default_mode():
    default = os.environ.get("TLS_ENABLE", "0")
    MODE_FILE.unlink(missing_ok=True)
    restart_server()
    wait_for_mode(default)


def ensure_tls_mode(context, value):
    if effective_tls_mode() == value and server_answers(value):
        return
    MODE_FILE.write_text(value)
    restart_server()
    wait_for_mode(value)
    context.add_cleanup(restore_default_mode)


@given(
    'the service is running with the environment variable "{variable:Q}" '
    'set to "{value:Q}"'
)
def step_service_running_with_env(context, variable, value):
    assert variable == "TLS_ENABLE", (
        f'only "TLS_ENABLE" controls the service mode, got "{variable}"'
    )
    ensure_tls_mode(context, value)


@given("a self-signed TLS certificate has been generated in the container")
def step_self_signed_certificate_generated(context):
    wait_for_certificate()
    fields = subprocess.run(
        ["openssl", "x509", "-in", str(certificate_path()),
         "-noout", "-subject", "-issuer"],
        capture_output=True, text=True, check=True,
    ).stdout
    subject, issuer = (line.split("=", 1)[1] for line in fields.splitlines())
    assert subject == issuer, (
        f"certificate is not self-signed: subject={subject} issuer={issuer}"
    )


@when(
    'a client sends a GET request to "{url:Q}" '
    "accepting the self-signed certificate"
)
def step_get_request_accepting_certificate(context, url):
    context.response = requests.get(
        url, timeout=10, verify=str(certificate_path())
    )
    context.tls_version = negotiated_tls_version(url)


def negotiated_tls_version(url):
    parts = urlsplit(url)
    tls_context = ssl.create_default_context(cafile=str(certificate_path()))
    with socket.create_connection(
        (parts.hostname, parts.port or 443), timeout=10
    ) as raw_socket:
        with tls_context.wrap_socket(
            raw_socket, server_hostname=parts.hostname
        ) as tls_socket:
            return tls_socket.version()


@then("the connection is encrypted with TLS version 1.2 or higher")
def step_connection_tls_version(context):
    version = context.tls_version
    match = re.fullmatch(r"TLSv(\d+)\.(\d+)", version)
    assert match, f"unexpected TLS protocol version: {version}"
    major, minor = int(match.group(1)), int(match.group(2))
    assert (major, minor) >= (1, 2), (
        f"connection uses {version}, expected TLS 1.2 or higher"
    )


@then(
    'a certificate file exists in the directory given by the '
    'environment variable "{variable:Q}"'
)
def step_certificate_file_exists(context, variable):
    assert_tls_file_exists(variable, "*.crt")


@then(
    'a private key file exists in the directory given by the '
    'environment variable "{variable:Q}"'
)
def step_private_key_file_exists(context, variable):
    assert_tls_file_exists(variable, "*.key")


def assert_tls_file_exists(variable, pattern):
    directory = os.environ.get(variable)
    assert directory, f'environment variable "{variable}" is not set'
    matches = list(Path(directory).glob(pattern))
    assert matches, f"no {pattern} file found in {directory}"
