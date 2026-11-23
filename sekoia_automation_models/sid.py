import re

_DOMAIN_ACCOUNT_SID = re.compile(r"S-1-5-21-(\d+)-(\d+)-(\d+)-(\d+)")
_ENTRA_SID = re.compile(r"S-1-12-1-(\d+)-(\d+)-(\d+)-(\d+)")

_MAX_SUB_AUTHORITY = 2**32 - 1
# Below 1000, the relative ID names a built-in account or group (500 Administrator,
# 501 Guest, 512 Domain Admins...), shared by every domain under the same name
_FIRST_ACCOUNT_RID = 1000


def normalize_sid(value: str | None) -> str | None:
    """
    Return the SID of an account the asset management API can match on, in upper case.

    Only a domain account (`S-1-5-21-…` with a relative ID from 1000) or an Entra ID
    object (`S-1-12-1-…`) is kept. Returns `None` for anything else: an empty value, a
    placeholder such as `Unknown`, a GUID or vendor ID, a well-known SID (`S-1-5-18`,
    `S-1-5-32-544`…) or a built-in account. The caller leaves the SID out.

    A SID does not tell a domain account from a local account of a machine: keep it to
    values read from a directory.
    """
    if not value:
        return None

    sid = value.strip().upper()
    if match := _DOMAIN_ACCOUNT_SID.fullmatch(sid):
        if int(match.group(4)) < _FIRST_ACCOUNT_RID:
            return None
    elif not (match := _ENTRA_SID.fullmatch(sid)):
        return None

    if any(int(part) > _MAX_SUB_AUTHORITY for part in match.groups()):
        return None
    return sid
