import pytest

from sekoia_automation_models.identifiers import (
    CATALOG,
    USER_FIELD_GROUPS,
    Identifier,
    account_identifiers,
    email_identifiers,
    host_identifiers,
    sid_identifiers,
)

I = Identifier  # noqa: E741


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "S-1-5-21-1500703765-3354019915-535386580-1662",
            "s-1-5-21-1500703765-3354019915-535386580-1662",
        ),
        (
            "  s-1-12-1-1234567890-1098765432-2345678901-3456789012 ",
            "s-1-12-1-1234567890-1098765432-2345678901-3456789012",
        ),
        (["S-1-5-21-1-2-3-1000"], "s-1-5-21-1-2-3-1000"),
    ],
)
def test_an_account_sid_is_kept_in_lower_case(value, expected):
    assert sid_identifiers(value) == [I("sid", expected)]


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        12,
        {"a": 1},
        ["S-1-5-21-1-2-3-1000", "S-1-5-21-1-2-3-1001"],
        "S-1-5-18",
        "S-1-5-32-544",
        "S-1-5-21-1-2-3-500",
        "S-1-5-90-0-1",
        "0b6f5a3e-8e2c-4b1a-9d1f-2a3b4c5d6e7f",
        "jdoe@corp.example",
        "unknown",
    ],
)
def test_anything_else_is_no_sid(value):
    assert sid_identifiers(value) == []


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" John.Doe@Corp.Example ", I("email", "john.doe@corp.example")),
        ("support@corp.example", I("email", "support@corp.example", generic=True)),
        ("No-Reply@corp.example", I("email", "no-reply@corp.example", generic=True)),
    ],
)
def test_an_email_is_kept_in_lower_case_and_a_shared_mailbox_is_generic(
    value, expected
):
    assert email_identifiers(value) == [expected]


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        3,
        "jdoe",
        "jdoe@corp",
        "@",
        "a@b.c d",
        "srv-01$@corp.example",
        "service-123@gcp-sa-logging.iam.gserviceaccount.com",
        "x@system.gserviceaccount.com",
        "a" * 250 + "@corp.example",
    ],
)
def test_a_value_that_is_no_person_mailbox_is_no_email(value):
    assert email_identifiers(value) == []


@pytest.mark.parametrize(
    ("name", "domain", "expected"),
    [
        ("SRV-01", None, [I("hostname", "srv-01")]),
        (" srv-01. ", None, [I("hostname", "srv-01")]),
        (
            "SRV-01.corp.fr",
            None,
            [
                I("fqdn", "srv-01.corp.fr"),
                I("hostname", "srv-01"),
                I("hostname", "srv-01.corp.fr", legacy=True),
            ],
        ),
        (
            "srv-01.corp.local",
            None,
            [
                I("fqdn", "srv-01.corp.local"),
                I("hostname", "srv-01"),
                I("hostname", "srv-01.corp.local", legacy=True),
            ],
        ),
        (
            "macbook-de-jean.local",
            None,
            [
                I("hostname", "macbook-de-jean"),
                I("hostname", "macbook-de-jean.local", legacy=True),
            ],
        ),
        (
            "srv_01.corp.fr",
            None,
            [I("hostname", "srv_01"), I("hostname", "srv_01.corp.fr", legacy=True)],
        ),
        (
            "srv-01",
            "Corp.Example.",
            [I("fqdn", "srv-01.corp.example"), I("hostname", "srv-01")],
        ),
        ("srv-01", "CORP", [I("hostname", "srv-01")]),
        ("srv-01", "unknown", [I("hostname", "srv-01")]),
        ("srv-01", 12, [I("hostname", "srv-01")]),
        (
            "srv-01.corp.fr",
            "other.example",
            [
                I("fqdn", "srv-01.corp.fr"),
                I("hostname", "srv-01"),
                I("hostname", "srv-01.corp.fr", legacy=True),
            ],
        ),
        ("MÜNCHEN-PC", None, [I("hostname", "münchen-pc")]),
        (["srv-01"], None, [I("hostname", "srv-01")]),
    ],
)
def test_a_host_name_gives_its_short_name_and_its_full_name(name, domain, expected):
    assert host_identifiers(name, domain) == expected


@pytest.mark.parametrize(
    "name",
    [
        None,
        "",
        7,
        ["a", "b"],
        "unknown",
        "N/A",
        "-",
        "localhost",
        "localhost.localdomain",
        "ip6-loopback",
        "10.0.0.1",
        "::1",
        "fe80::1",
        "12345",
        "10.corp.fr",
        "srv 01",
        "srv/01",
        "unknown.corp.fr",
        "localhost.corp.fr",
        ".",
        "..",
        ".corp.fr",
        "srv-01..corp.fr",
        "a" * 256,
        "a" * 64 + ".corp.fr",
    ],
)
def test_a_value_that_names_no_machine_gives_nothing(name):
    assert host_identifiers(name) == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("JDoe", [I("username", "jdoe")]),
        (" jdoe ", [I("username", "jdoe")]),
        (
            "CORP\\JDoe",
            [I("username", "jdoe"), I("username", "corp\\jdoe", legacy=True)],
        ),
        ("John.Doe@Corp.Example", [I("email", "john.doe@corp.example")]),
        ("support@corp.example", [I("email", "support@corp.example", generic=True)]),
        ("José", [I("username", "josé")]),
        ("jean dupont", [I("username", "jean dupont")]),
        ("jdoe@corp", [I("username", "jdoe@corp")]),
        (["jdoe"], [I("username", "jdoe")]),
    ],
)
def test_a_login_gives_a_username_or_an_email(name, expected):
    assert account_identifiers(name) == expected


@pytest.mark.parametrize(
    "name",
    [
        None,
        "",
        5,
        ["a", "b"],
        "unknown",
        "(null)",
        "-",
        "12345",
        "SRV-01$",
        "CORP\\SRV-01$",
        "srv-01$@corp.example",
        "Administrator",
        "CORP\\administrator",
        "root",
        "SYSTEM",
        "krbtgt",
        "DefaultAccount",
        "backup",
        "DWM-1",
        "UMFD-0",
        "sshd_4521",
        "lenovo_tmp_ab12",
        "defaultuser0",
        "S-1-5-21-1-2-3-1001",
        "urn:forms:anonymous#abc",
        "login at 12:30:45",
        "user 10.0.0.1",
        "service-123@gcp-sa-logging.iam.gserviceaccount.com",
        "CORP\\",
        "\\",
        "a" * 256,
    ],
)
def test_a_value_that_names_no_person_account_gives_nothing(name):
    assert account_identifiers(name) == []


@pytest.mark.parametrize(
    "value",
    ["a" * 1_000_000, "1:" * 500_000, "a." * 500_000, "12:" * 400_000],
)
def test_a_megabyte_of_input_is_refused_by_every_function(value):
    assert sid_identifiers(value) == []
    assert email_identifiers(value) == []
    assert host_identifiers(value) == []
    assert account_identifiers(value) == []


@pytest.mark.parametrize(
    ("function", "raw"),
    [
        (host_identifiers, "SRV-01.corp.fr"),
        (host_identifiers, "srv-01"),
        (account_identifiers, "CORP\\JDoe"),
        (account_identifiers, "John.Doe@Corp.Example"),
        (email_identifiers, "John.Doe@Corp.Example"),
        (sid_identifiers, "S-1-5-21-1-2-3-1000"),
    ],
)
def test_a_normalized_value_comes_back_unchanged_and_without_a_previous_form(
    function, raw
):
    for identifier in function(raw):
        if identifier.legacy:
            continue
        again = [
            found
            for found in function(identifier.value)
            if found.type == identifier.type
        ]
        assert again == [identifier]


def test_the_catalogue_describes_the_five_types():
    assert set(CATALOG) == {"hostname", "fqdn", "username", "email", "sid"}
    assert {name for name, kind in CATALOG.items() if kind.strong} == {
        "fqdn",
        "email",
        "sid",
    }
    assert {name for name, kind in CATALOG.items() if not kind.creates_asset} == {
        "fqdn",
        "sid",
    }
    assert {kind.asset_type for kind in CATALOG.values()} == {"host", "account"}
    assert all(name == kind.name for name, kind in CATALOG.items())


def test_every_identifier_a_function_returns_has_its_type_in_the_catalogue():
    produced = (
        host_identifiers("srv-01.corp.fr")
        + account_identifiers("CORP\\jdoe")
        + account_identifiers("jdoe@corp.example")
        + sid_identifiers("S-1-5-21-1-2-3-1000")
    )
    assert {identifier.type for identifier in produced} == set(CATALOG)


def test_the_fields_of_an_account_identifier_cover_every_user_field_group():
    assert CATALOG["sid"].ecs_fields == tuple(
        f"{group}.id" for group in USER_FIELD_GROUPS
    )
    assert "source.user.name" in CATALOG["username"].ecs_fields
    assert "user.full_name" in CATALOG["username"].ecs_fields
    assert "user.target.email" in CATALOG["email"].ecs_fields
    assert "user.name" in CATALOG["email"].ecs_fields


@pytest.mark.parametrize(
    "value",
    [
        "srv\ud800",
        "a\ud800@corp.example",
        "jdoe\x07",
        "jean\tdupont",
        "jean\ndupont",
        "srv$@a\nb",
        "lenovo_tmp_a\nb",
    ],
)
def test_a_value_holding_a_control_character_or_a_lone_surrogate_gives_nothing(value):
    assert host_identifiers(value) == []
    assert account_identifiers(value) == []
    assert email_identifiers(value) == []
    assert sid_identifiers(value) == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("srv​01", [I("hostname", "srv01")]),
        ("﻿SRV-01", [I("hostname", "srv-01")]),
        ("\uff33\uff32\uff36-01", [I("hostname", "srv-01")]),
        ("\u017frv", [I("hostname", "srv")]),
        ("\u212a9", [I("hostname", "k9")]),
        ("Straße-PC", [I("hostname", "strasse-pc")]),
        (
            "srv.corp\u3002fr",
            [
                I("fqdn", "srv.corp.fr"),
                I("hostname", "srv"),
                I("hostname", "srv.corp.fr", legacy=True),
            ],
        ),
        (
            "srv.10.0.0.1",
            [I("hostname", "srv"), I("hostname", "srv.10.0.0.1", legacy=True)],
        ),
    ],
)
def test_a_host_name_is_stored_in_the_form_it_was_checked_in(name, expected):
    assert host_identifiers(name) == expected


@pytest.mark.parametrize(
    "name", ["٣٤٥", "٣٤.corp.fr", "srv-01..", "a.b..", "fe80::1%eth0"]
)
def test_a_host_name_without_a_letter_or_with_an_empty_label_gives_nothing(name):
    assert host_identifiers(name) == []


@pytest.mark.parametrize(
    "domain", ["10.0.0.1", "local", ".corp.fr", "corp..fr", "corp.fr-"]
)
def test_a_domain_that_is_no_dns_domain_gives_no_fqdn(domain):
    assert host_identifiers("srv", domain) == [I("hostname", "srv")]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (
            "CORP\\ jdoe",
            [I("username", "jdoe"), I("username", "corp\\ jdoe", legacy=True)],
        ),
        (
            "a\\b\\jdoe",
            [I("username", "jdoe"), I("username", "a\\b\\jdoe", legacy=True)],
        ),
        ("CORP\\jdoe@corp.example", [I("email", "jdoe@corp.example")]),
        ("jdoe@corp.local", [I("email", "jdoe@corp.local")]),
        ("jdoe@corp.example.", [I("username", "jdoe@corp.example.")]),
        ("ro​ot2", [I("username", "root2")]),
        ("﻿jdoe", [I("username", "jdoe")]),
    ],
)
def test_a_login_is_read_after_its_domain_prefix_and_without_invisible_characters(
    name, expected
):
    assert account_identifiers(name) == expected


@pytest.mark.parametrize(
    "name",
    [
        "CORP\\ root",
        "ADMINISTRATOR​",
        "ro​ot",
        "SYSTÈME",
        "S-1-12-1-1-2-3-4",
        "S-1-5-32-544",
        "CORP\\jdoe\\",
    ],
)
def test_a_shared_account_or_a_sid_written_another_way_is_still_no_username(name):
    assert account_identifiers(name) == []


@pytest.mark.parametrize(
    "value",
    [
        "mailto:jdoe@corp.example",
        "jdoe@corp..example",
        "jdoe@10.0.0.12",
        "a@b.cd-",
        "corp\\jdoe@corp.example",
    ],
)
def test_an_address_with_a_malformed_mailbox_or_domain_is_no_email(value):
    assert email_identifiers(value) == []


@pytest.mark.parametrize(
    "value",
    [
        "a" * 2048,
        "1:" * 1024,
        "a." * 1024,
        "12:" * 682,
        "a@" + "b." * 1000 + "cd",
        "s-1-" + "1-" * 1000,
        "\\" * 2048,
    ],
)
def test_the_longest_accepted_input_is_answered(value):
    for function in (
        host_identifiers,
        account_identifiers,
        email_identifiers,
        sid_identifiers,
    ):
        assert isinstance(function(value), list)
