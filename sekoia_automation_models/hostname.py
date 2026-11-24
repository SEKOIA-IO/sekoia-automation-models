import re

import tldextract

HOSTNAME_REGEX = re.compile(rb"[a-z0-9-_.]+")
LETTER_REGEX = re.compile(rb"[a-z]")

# Bundled public suffix list only: nothing is fetched at runtime
_extract = tldextract.TLDExtract(
    suffix_list_urls=(), cache_dir=None, fallback_to_snapshot=True
)


def split_hostname(value: str | None) -> tuple[str | None, str | None]:
    """
    Split a name into the `(hostname, domain)` pair the asset management API accepts.

    A fully qualified name is split on its first label. Returns `(None, None)` when no
    usable hostname can be derived: the caller skips the device.
    """
    if not value:
        return None, None

    name = value.strip().lower()
    domain = None
    if "." in name and _extract(name).suffix:
        name, _, domain = name.partition(".")

    try:
        # The idna codec also rejects empty labels and labels over 63 characters
        encoded = name.encode("idna")
    except UnicodeError:
        return None, None

    if not HOSTNAME_REGEX.fullmatch(encoded) or not LETTER_REGEX.search(encoded):
        return None, None

    return name, domain or None


_LABEL = rb"[a-z0-9]([a-z0-9-]*[a-z0-9])?"
FQDN_REGEX = re.compile(rb"%s(\.%s)+" % (_LABEL, _LABEL))
_MAX_FQDN_LENGTH = 253


def _fqdn_part(value: str | None) -> str | None:
    """The part in lower case, without spaces or trailing dot, in IDNA (`xn--`) form"""
    part = (value or "").strip().lower().removesuffix(".")
    try:
        return part.encode("idna").decode()
    except UnicodeError:
        return None


def build_fqdn(hostname: str | None, domain: str | None) -> str | None:
    """
    Return the fully qualified name of a device from its hostname and domain.

    The name is in lower case, and a hostname that already ends with the domain is kept
    as it is. Returns `None` when no reliable FQDN can be built: a missing part, a
    NetBIOS domain (no dot, such as `CORP`), a hostname qualified with another domain,
    or a name that is not a valid DNS name. The caller leaves the FQDN out. A non-ASCII
    name is returned in its IDNA (`xn--`) form.
    """
    host, dom = _fqdn_part(hostname), _fqdn_part(domain)
    if not host or not dom or "." not in dom:
        return None

    if host.endswith(f".{dom}"):
        fqdn = host
    elif "." in host:
        return None
    else:
        fqdn = f"{host}.{dom}"

    if len(fqdn) > _MAX_FQDN_LENGTH or not FQDN_REGEX.fullmatch(fqdn.encode()):
        return None
    return fqdn
