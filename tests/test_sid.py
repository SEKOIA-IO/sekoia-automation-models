import pytest

from sekoia_automation_models.sid import normalize_sid


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "S-1-5-21-1500703765-3354019915-535386580-1662",
            "S-1-5-21-1500703765-3354019915-535386580-1662",
        ),
        (
            "  s-1-5-21-1500703765-3354019915-535386580-1000 ",
            "S-1-5-21-1500703765-3354019915-535386580-1000",
        ),
        (
            "S-1-12-1-1234567890-1098765432-2345678901-3456789012",
            "S-1-12-1-1234567890-1098765432-2345678901-3456789012",
        ),
    ],
)
def test_normalize_sid_keeps_an_account_sid(value, expected):
    assert normalize_sid(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "Unknown",
        # GUIDs and vendor IDs sent where a SID is expected
        "0b6f5a3e-8e2c-4b1a-9d1f-2a3b4c5d6e7f",
        "{0B6F5A3E-8E2C-4B1A-9D1F-2A3B4C5D6E7F}",
        "a1b2c3d4e5f60718293a4b5c6d7e8f90",
        # Well-known SIDs, the same in every domain
        "S-1-5-18",
        "S-1-5-32-544",
        "S-1-1-0",
        # Built-in accounts and groups of a domain
        "S-1-5-21-1500703765-3354019915-535386580-500",
        "S-1-5-21-1500703765-3354019915-535386580-512",
        "S-1-5-21-1500703765-3354019915-535386580-999",
        # Malformed
        "S-1-5-21-1500703765-3354019915-1662",
        "S-1-5-21-1500703765-3354019915-535386580-1662-1",
        "S-1-5-21-4294967296-3354019915-535386580-1662",
        "S-1-12-1-1234567890-1098765432-2345678901",
        "user@example.com",
    ],
)
def test_normalize_sid_rejects_anything_else(value):
    assert normalize_sid(value) is None
