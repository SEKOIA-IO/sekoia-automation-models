"""
Asset identifiers: one way to write a raw value as the identifier of a machine or an
account.

Every function returns the identifiers of a value, strongest first, and an empty list
when the value identifies nothing. It never raises, whatever the type of the value.
Values are in lower case and in their Unicode compatibility form (NFKC), without
invisible format characters; a value holding a control character is refused. An
identifier marked `legacy` is the form the value had before these rules: it is only
there to find assets stored under it.
"""

import ipaddress
import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

from sekoia_automation_models.sid import normalize_sid

PLACEHOLDERS = frozenset(
    {
        "not-found",
        "not-available",
        "not available",
        "none",
        "<unknown>",
        "unknown",
        "unset",
        "n/a",
        "nan",
        "null",
        "(null)",
        "undefined",
        "empty",
        "-",
    }
)

LOOPBACK_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "localhost4",
        "localhost4.localdomain4",
        "localhost6",
        "localhost6.localdomain6",
        "ip6-localhost",
        "ip6-loopback",
    }
)

PSEUDO_DOMAINS = frozenset({"local", "localdomain", "lan", "home"})

GENERIC_MAILBOXES = frozenset(
    {
        "admin",
        "administrator",
        "contact",
        "helpdesk",
        "info",
        "it",
        "no-reply",
        "noreply",
        "postmaster",
        "root",
        "security",
        "support",
    }
)

SHARED_USERNAMES = frozenset(
    {
        "root",
        "system",
        "système",
        "admin",
        "administrator",
        "administrateur",
        "service local",
        "local service",
        "service réseau",
        "network service",
        "anonymous logon",
        "app",
        "test",
        "defaultapppool",
        "www-data",
        "application",
        "anonymous",
        "postgres",
        "nobody",
        "user",
        "mysql",
        "backup",
        "guest",
        "invité",
        "defaultaccount",
        "wdagutilityaccount",
        "iusr",
        "krbtgt",
        "info",
        "mail",
        "postfix",
        "scanner",
        "oracle",
        "sshd",
        "mssqlserver",
        "service",
        "ftp",
        "noreply",
        "linux",
        "ubuntu",
        "debian",
        "centos",
        "redhat",
        "windows",
    }
)

USER_FIELD_GROUPS = (
    "user",
    "client.user",
    "destination.user",
    "process.attested_user",
    "process.real_user",
    "process.saved_user",
    "process.user",
    "server.user",
    "source.user",
    "user.changes",
    "user.effective",
    "user.target",
)

_MAX_RAW_LENGTH = 2048
_MAX_NAME_BYTES = 255
_MAX_FQDN_LENGTH = 253
_MAX_EMAIL_LENGTH = 254

_REFUSED_CATEGORIES = frozenset({"Cc", "Cs", "Co", "Cn"})
_MAILBOX_FORBIDDEN = frozenset('\\:/<>()[],;"')

_EMAIL = re.compile(r"[^@\s]+(?<!\$)@[^@\s]+\.\w[\w-]+")
_CLOUD_SERVICE_ACCOUNT = re.compile(
    r"(service-\d+@gcp-sa-[a-z0-9-]+\.iam|[^@]+@system)\.gserviceaccount\.com"
)
_HOSTNAME = re.compile(rb"[a-z0-9-_.]+")
_LABEL = rb"[a-z0-9]([a-z0-9-]*[a-z0-9])?"
_FQDN = re.compile(rb"%s(\.%s)+" % (_LABEL, _LABEL))
_MACHINE_ACCOUNT = re.compile(r"\$(@.*)?$")
_EPHEMERAL_ACCOUNT = re.compile(
    r"dwm-\d+|umfd-\d+|sshd_\d+|lenovo_tmp_.*|defaultuser\d+|s-1-\d+(-\d+)+"
    r"|urn:forms:(anonymous|external|coauthor)#.*"
)
_TIME_OR_IP = re.compile(r"\d{2}:\d{2}:\d{2}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


@dataclass(frozen=True)
class Identifier:
    """
    One identifier of an asset.

    `generic` marks a real value shared by many objects, such as the `support`
    mailbox: it never proves that two assets are the same. `legacy` marks the previous
    form of a value.
    """

    type: str
    value: str
    generic: bool = False
    legacy: bool = False


@dataclass(frozen=True)
class IdentifierType:
    """
    What a type of identifier is: the asset it belongs to, whether it is strong
    evidence, whether an event may create an asset from it, and the connector (OCSF)
    and event (ECS) fields it is read from.
    """

    name: str
    asset_type: Literal["host", "account"]
    strong: bool
    creates_asset: bool
    ocsf_fields: tuple[str, ...]
    ecs_fields: tuple[str, ...]


def _user_fields(*names: str) -> tuple[str, ...]:
    return tuple(f"{group}.{name}" for name in names for group in USER_FIELD_GROUPS)


CATALOG: Mapping[str, IdentifierType] = MappingProxyType(
    {
        kind.name: kind
        for kind in (
            IdentifierType(
                name="hostname",
                asset_type="host",
                strong=False,
                creates_asset=True,
                ocsf_fields=("device.hostname",),
                ecs_fields=("host.name", "host.hostname"),
            ),
            IdentifierType(
                name="fqdn",
                asset_type="host",
                strong=True,
                creates_asset=False,
                ocsf_fields=("device.hostname", "device.domain"),
                ecs_fields=("host.name", "host.hostname"),
            ),
            IdentifierType(
                name="username",
                asset_type="account",
                strong=False,
                creates_asset=True,
                ocsf_fields=("user.name",),
                ecs_fields=_user_fields("name", "full_name"),
            ),
            IdentifierType(
                name="email",
                asset_type="account",
                strong=True,
                creates_asset=True,
                ocsf_fields=("user.email_addr", "user.name"),
                ecs_fields=_user_fields("email", "name", "full_name"),
            ),
            IdentifierType(
                name="sid",
                asset_type="account",
                strong=True,
                creates_asset=False,
                ocsf_fields=("user.account.uid",),
                ecs_fields=_user_fields("id"),
            ),
        )
    }
)


def _clean(value: object) -> str | None:
    if isinstance(value, list | tuple):
        if len(value) != 1:
            return None
        value = value[0]
    if not isinstance(value, str) or len(value) > _MAX_RAW_LENGTH:
        return None
    text = unicodedata.normalize("NFKC", value.replace("\x00", ""))
    categories = {unicodedata.category(character) for character in text}
    if categories & _REFUSED_CATEGORIES:
        return None
    if "Cf" in categories:
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return unicodedata.normalize("NFKC", text.strip().lower()) or None


def _is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def _dns_form(name: str) -> str | None:
    """The name as its labels are compared in DNS, or None when a label is not valid."""
    name = name.replace("\u3002", ".")
    if "" in name.split("."):
        return None
    try:
        encoded = name.encode("idna")
        if not _HOSTNAME.fullmatch(encoded):
            return None
        return encoded.decode("idna")
    except UnicodeError:
        return None


def _is_short_hostname(label: str) -> bool:
    return (
        label not in PLACEHOLDERS
        and label not in LOOPBACK_HOSTNAMES
        and any(character.isalpha() for character in label)
    )


def _is_dns_name(name: str) -> bool:
    try:
        encoded = name.encode("idna")
    except UnicodeError:
        return False
    return (
        len(name) <= _MAX_FQDN_LENGTH
        and bool(_FQDN.fullmatch(encoded))
        and not name.rpartition(".")[2].isdigit()
    )


def _is_fqdn(name: str) -> bool:
    return _is_dns_name(name) and name.partition(".")[2] not in PSEUDO_DOMAINS


def _qualified(hostname: str, domain: object) -> str | None:
    cleaned = _clean(domain)
    if cleaned is None:
        return None
    suffix = _dns_form(cleaned.removesuffix("."))
    if suffix is None or "." not in suffix:
        return None
    fqdn = f"{hostname}.{suffix}"
    return fqdn if _is_fqdn(fqdn) else None


def host_identifiers(name: object, domain: object = None) -> list[Identifier]:
    """
    Return the identifiers of a machine from its name, and from its domain when the
    name is short.

    A dotted name is split at its first dot, whatever its suffix: `SRV-01.corp.local`
    gives the FQDN `srv-01.corp.local`, the hostname `srv-01`, then the whole name as
    the legacy hostname. A short name gives its hostname, and its FQDN when `domain`
    is a DNS domain (`CORP` is not). A one-label pseudo domain such as `.local` gives
    no FQDN.

    The name is returned as DNS compares it (`Straße-PC` gives `strasse-pc`).

    Returns an empty list for a placeholder such as `unknown`, a loopback name, an IP
    address, a name over 255 bytes, a name with an empty label or without a letter in
    its first label, or a name holding anything but letters, digits, `-`, `_` and `.`.
    """
    cleaned = _clean(name)
    if cleaned is None:
        return []
    cleaned = cleaned.removesuffix(".")
    if (
        len(cleaned.encode()) > _MAX_NAME_BYTES
        or cleaned in PLACEHOLDERS
        or cleaned in LOOPBACK_HOSTNAMES
        or _is_ip_address(cleaned)
    ):
        return []
    value = _dns_form(cleaned)
    if value is None:
        return []
    hostname, _, rest = value.partition(".")
    if not _is_short_hostname(hostname):
        return []
    if not rest:
        fqdn = _qualified(hostname, domain)
        found = [Identifier("fqdn", fqdn)] if fqdn else []
        return [*found, Identifier("hostname", hostname)]
    return [
        *([Identifier("fqdn", value)] if _is_fqdn(value) else []),
        Identifier("hostname", hostname),
        Identifier("hostname", value, legacy=True),
    ]


def email_identifiers(value: object) -> list[Identifier]:
    """
    Return the email of a person or of a shared mailbox, generic for a shared one
    (`support@…`).

    Returns an empty list for anything that is not a mailbox and a DNS domain around
    one `@`, a machine account (`name$@domain`), a cloud service account, a mailbox
    holding one of `\\ : / < > ( ) [ ] , ; "`, or an address over 254 characters.
    """
    email = _clean(value)
    if email is None or len(email) > _MAX_EMAIL_LENGTH or not _EMAIL.fullmatch(email):
        return []
    mailbox, _, domain = email.partition("@")
    if (
        _CLOUD_SERVICE_ACCOUNT.fullmatch(email)
        or not _MAILBOX_FORBIDDEN.isdisjoint(mailbox)
        or not _is_dns_name(domain)
    ):
        return []
    return [
        Identifier("email", email, generic=email.partition("@")[0] in GENERIC_MAILBOXES)
    ]


def account_identifiers(name: object) -> list[Identifier]:
    """
    Return the identifiers of an account from its login.

    The `DOMAIN\\` prefix is removed first. An email-shaped login then gives an email
    and no username. Any other login gives a username, then the whole value as the
    legacy username when a prefix was removed.

    Returns an empty list for a placeholder, a machine account (`NAME$`), a shared or
    built-in account such as `administrator`, a temporary account such as `sshd_1234`,
    a SID, a value without a letter, over 255 bytes, or holding a time or an IP
    address.
    """
    value = _clean(name)
    if value is None or len(value.encode()) > _MAX_NAME_BYTES:
        return []
    login = value.rpartition("\\")[2].strip()
    if emails := email_identifiers(login):
        return emails
    if (
        login in PLACEHOLDERS
        or login in SHARED_USERNAMES
        or not any(character.isalpha() for character in login)
        or _MACHINE_ACCOUNT.search(login)
        or _EPHEMERAL_ACCOUNT.fullmatch(login)
        or _CLOUD_SERVICE_ACCOUNT.fullmatch(login)
        or _TIME_OR_IP.search(login)
    ):
        return []
    username = Identifier("username", login)
    if login == value:
        return [username]
    return [username, Identifier("username", value, legacy=True)]


def sid_identifiers(value: object) -> list[Identifier]:
    """
    Return the SID of a domain account or of an Entra ID object, the rule of
    `normalize_sid`.

    Returns an empty list for anything else: a well-known SID, a built-in account, a
    GUID.
    """
    sid = normalize_sid(_clean(value))
    return [Identifier("sid", sid.lower())] if sid else []
