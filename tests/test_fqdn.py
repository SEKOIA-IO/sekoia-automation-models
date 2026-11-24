import pytest

from sekoia_automation_models.hostname import build_fqdn


@pytest.mark.parametrize(
    ("hostname", "domain", "expected"),
    [
        ("WS-01", "corp.example.fr", "ws-01.corp.example.fr"),
        (" ws-01 ", " Corp.Example.FR. ", "ws-01.corp.example.fr"),
        ("ws-01.corp.example.fr", "corp.example.fr", "ws-01.corp.example.fr"),
        ("ws-01.corp.example.fr.", "corp.example.fr", "ws-01.corp.example.fr"),
        ("ws-01", "corp.local", "ws-01.corp.local"),
        ("café", "corp.example.fr", "xn--caf-dma.corp.example.fr"),
    ],
)
def test_build_fqdn(hostname, domain, expected):
    assert build_fqdn(hostname, domain) == expected


@pytest.mark.parametrize(
    ("hostname", "domain"),
    [
        (None, "corp.example.fr"),
        ("", "corp.example.fr"),
        ("ws-01", None),
        ("ws-01", ""),
        ("ws-01", "."),
        ("ws-01", "CORP"),
        ("ws-01.other.fr", "corp.example.fr"),
        ("ws-01", "corp..example.fr"),
        ("srv_01", "corp.example.fr"),
        ("ws 01", "corp.example.fr"),
        ("a" * 64, "corp.example.fr"),
    ],
)
def test_build_fqdn_unreliable(hostname, domain):
    assert build_fqdn(hostname, domain) is None
