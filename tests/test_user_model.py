import pytest
from pydantic import ValidationError

from sekoia_automation_models.ocsf.group import Group
from sekoia_automation_models.ocsf.organization import Organization
from sekoia_automation_models.ocsf.risk_level import RiskLevelId, RiskLevelStr
from sekoia_automation_models.ocsf.user import (
    Account,
    AccountTypeId,
    AccountTypeStr,
    LdapPerson,
    User,
    UserDataObject,
    UserEnrichmentObject,
    UserOCSFModel,
    UserTypeId,
    UserTypeStr,
)


def test_user_data_object_all_optional():
    obj = UserDataObject()
    assert obj.is_enabled is None
    assert obj.last_logon is None
    assert obj.bad_password_count is None
    assert obj.number_of_logons is None
    assert obj.last_time_password_change is None
    assert obj.external_device is None


def test_user_data_object_with_all_fields():
    obj = UserDataObject(
        is_enabled=True,
        last_logon="2024-01-15T08:00:00Z",
        bad_password_count=3,
        number_of_logons=42,
        last_time_password_change=1700000000.0,
        external_device="YubiKey 5",
    )
    assert obj.is_enabled is True
    assert obj.last_logon == "2024-01-15T08:00:00Z"
    assert obj.bad_password_count == 3
    assert obj.number_of_logons == 42
    assert obj.last_time_password_change == 1700000000.0
    assert obj.external_device == "YubiKey 5"


def test_user_enrichment_object_all_optional():
    obj = UserEnrichmentObject()
    assert obj.name is None
    assert obj.value is None
    assert obj.data is None


def test_user_enrichment_object_with_nested_data():
    obj = UserEnrichmentObject(
        name="logon_info",
        value="active",
        data=UserDataObject(is_enabled=True, number_of_logons=10),
    )
    assert obj.name == "logon_info"
    assert obj.value == "active"
    assert obj.data is not None
    assert obj.data.is_enabled is True
    assert obj.data.number_of_logons == 10


def test_account_type_id_values():
    assert AccountTypeId.UNKNOWN == 0
    assert AccountTypeId.LDAP_ACCOUNT == 1
    assert AccountTypeId.WINDOWS_ACCOUNT == 2
    assert AccountTypeId.AWS_ACCOUNT == 10
    assert AccountTypeId.EMAIL_ACCOUNT == 18
    assert AccountTypeId.OTHER == 99


def test_account_type_str_values():
    assert AccountTypeStr.LDAP_ACCOUNT == "LDAP Account"
    assert AccountTypeStr.AZURE_AD_ACCOUNT == "Azure AD Account"
    assert AccountTypeStr.GOOGLE_WORKSPACE == "Google Workspace"
    assert AccountTypeStr.OTHER == "Other"


def test_user_type_id_values():
    assert UserTypeId.UNKNOWN == 0
    assert UserTypeId.USER == 1
    assert UserTypeId.ADMIN == 2
    assert UserTypeId.SYSTEM == 3
    assert UserTypeId.SERVICE == 4


def test_user_type_str_values():
    assert UserTypeStr.USER == "User"
    assert UserTypeStr.ADMIN == "Admin"
    assert UserTypeStr.SYSTEM == "System"
    assert UserTypeStr.SERVICE == "Service"


def test_account_required_fields():
    account = Account(
        name="john@example.com",
        type_id=AccountTypeId.LDAP_ACCOUNT,
        type=AccountTypeStr.LDAP_ACCOUNT,
    )
    assert account.name == "john@example.com"
    assert account.type_id == AccountTypeId.LDAP_ACCOUNT
    assert account.type == AccountTypeStr.LDAP_ACCOUNT
    assert account.uid is None


def test_account_with_uid():
    account = Account(
        name="john@example.com",
        type_id=AccountTypeId.EMAIL_ACCOUNT,
        type=AccountTypeStr.EMAIL_ACCOUNT,
        uid="acc-001",
    )
    assert account.uid == "acc-001"


def test_account_missing_required_fields_raises():
    with pytest.raises(ValidationError):
        Account(name="john@example.com")  # type: ignore[call-arg]


def test_ldap_person_all_optional():
    ldap = LdapPerson()
    assert ldap.job_title is None
    assert ldap.department is None
    assert ldap.employee_uid is None
    assert ldap.given_name is None
    assert ldap.surname is None
    assert ldap.office_location is None


def test_ldap_person_with_all_fields():
    ldap = LdapPerson(
        job_title="Managing Consultant, Incident Response",
        department="Incident Response",
        employee_uid="EMP123",
        given_name="John",
        surname="Doe",
        office_location="New York, NY",
    )
    assert ldap.job_title == "Managing Consultant, Incident Response"
    assert ldap.department == "Incident Response"
    assert ldap.employee_uid == "EMP123"
    assert ldap.given_name == "John"
    assert ldap.surname == "Doe"
    assert ldap.office_location == "New York, NY"


def test_user_required_fields():
    user = User(name="john.doe@example.com", uid="uid-1")
    assert user.name == "john.doe@example.com"
    assert user.uid == "uid-1"


def test_user_all_optional_fields_default_to_none():
    user = User(name="jane.doe@example.com", uid="uid-2")
    assert user.has_mfa is None
    assert user.account is None
    assert user.groups is None
    assert user.full_name is None
    assert user.email_addr is None
    assert user.display_name is None
    assert user.domain is None
    assert user.forward_addr is None
    assert user.risk_level is None
    assert user.risk_level_id is None
    assert user.risk_score is None
    assert user.type_id is None
    assert user.type is None
    assert user.uid_alt is None
    assert user.org is None
    assert user.ldap_person is None


def test_user_with_all_fields():
    user = User(
        name="john.doe@example.com",
        uid="uid-3",
        has_mfa=True,
        account=Account(
            name="john@corp.com",
            type_id=AccountTypeId.LDAP_ACCOUNT,
            type=AccountTypeStr.LDAP_ACCOUNT,
            uid="acc-1",
        ),
        groups=[Group(name="admins", uid="grp-1")],
        full_name="John Doe",
        email_addr="john.doe@example.com",
        display_name="John D.",
        domain="corp.example.com",
        forward_addr="jd@alias.example.com",
        risk_level=RiskLevelStr.HIGH,
        risk_level_id=RiskLevelId.HIGH,
        risk_score=80,
        type_id=UserTypeId.ADMIN,
        type=UserTypeStr.ADMIN,
        uid_alt="john.doe",
        org=Organization(name="Acme Corp", ou_name="Security", uid="org-1"),
        ldap_person=LdapPerson(job_title="SOC Analyst", department="Security"),
    )
    assert user.has_mfa is True
    assert user.account is not None and user.account.uid == "acc-1"
    assert user.groups is not None and user.groups[0].name == "admins"
    assert user.full_name == "John Doe"
    assert user.email_addr == "john.doe@example.com"
    assert user.display_name == "John D."
    assert user.domain == "corp.example.com"
    assert user.forward_addr == "jd@alias.example.com"
    assert user.risk_level == RiskLevelStr.HIGH
    assert user.risk_level_id == RiskLevelId.HIGH
    assert user.risk_score == 80
    assert user.type_id == UserTypeId.ADMIN
    assert user.type == UserTypeStr.ADMIN
    assert user.uid_alt == "john.doe"
    assert user.org is not None and user.org.name == "Acme Corp"
    assert user.ldap_person is not None and user.ldap_person.job_title == "SOC Analyst"


def test_user_missing_name_raises():
    with pytest.raises(ValidationError):
        User(uid="uid-4")  # type: ignore[call-arg]


def test_user_missing_uid_raises():
    with pytest.raises(ValidationError):
        User(name="john.doe@example.com")  # type: ignore[call-arg]


def test_user_accepts_ldap_person():
    user = User(
        name="john.doe@example.com",
        uid="uid-1",
        ldap_person=LdapPerson(
            job_title="Managing Consultant, Incident Response",
            department="Incident Response",
        ),
    )

    assert user.ldap_person is not None
    assert user.ldap_person.job_title == "Managing Consultant, Incident Response"
    assert user.ldap_person.department == "Incident Response"


def test_user_ldap_person_is_optional():
    user = User(name="jane.doe@example.com", uid="uid-2")

    assert user.ldap_person is None


def test_ldap_person_serializes_only_set_fields():
    user = User(
        name="john.doe@example.com",
        uid="uid-3",
        ldap_person=LdapPerson(job_title="SOC Analyst", department="Security"),
    )

    dumped = user.model_dump(exclude_none=True)

    assert dumped["ldap_person"] == {
        "job_title": "SOC Analyst",
        "department": "Security",
    }


def test_ldap_person_accepts_extended_fields():
    ldap_person = LdapPerson(
        job_title="SOC Analyst",
        department="Security",
        employee_uid="EMP123",
        given_name="John",
        surname="Doe",
        office_location="New York, NY",
    )

    assert ldap_person.employee_uid == "EMP123"
    assert ldap_person.given_name == "John"
    assert ldap_person.surname == "Doe"
    assert ldap_person.office_location == "New York, NY"


def _base_user_ocsf_payload() -> dict:
    """Minimal valid payload for UserOCSFModel."""
    return {
        "activity_id": 1,
        "activity_name": "Create",
        "category_name": "Identity & Access Management",
        "category_uid": 3,
        "class_name": "User Inventory Info",
        "class_uid": 5002,
        "type_name": "User Inventory Info: Create",
        "type_uid": 500201,
        "time": 1700000000.0,
        "metadata": {
            "product": {
                "name": "TestProduct",
                "vendor_name": "TestCorp",
                "version": "1.0",
            },
            "version": "1.5.0",
        },
        "user": {"name": "john.doe@example.com", "uid": "uid-1"},
    }


def test_user_ocsf_model_minimal():
    model = UserOCSFModel.model_validate(_base_user_ocsf_payload())
    assert model.user.name == "john.doe@example.com"
    assert model.user.uid == "uid-1"
    assert model.enrichments is None


def test_user_ocsf_model_with_enrichments():
    payload = _base_user_ocsf_payload()
    payload["enrichments"] = [
        {
            "name": "logon_info",
            "value": "active",
            "data": {"is_enabled": True, "number_of_logons": 5},
        }
    ]
    model = UserOCSFModel.model_validate(payload)
    assert model.enrichments is not None
    assert len(model.enrichments) == 1
    assert model.enrichments[0].name == "logon_info"
    assert model.enrichments[0].data is not None
    assert model.enrichments[0].data.is_enabled is True
    assert model.enrichments[0].data.number_of_logons == 5


def test_user_ocsf_model_missing_user_raises():
    payload = _base_user_ocsf_payload()
    del payload["user"]
    with pytest.raises(ValidationError):
        UserOCSFModel.model_validate(payload)


# ---------------------------------------------------------------------------
# User — risk_score / risk_level / risk_level_id
# ---------------------------------------------------------------------------


def test_user_risk_fields_default_to_none():
    user = User(name="jane@example.com", uid="uid-10")
    assert user.risk_score is None
    assert user.risk_level is None
    assert user.risk_level_id is None


def test_user_risk_score_set():
    user = User(name="jane@example.com", uid="uid-11", risk_score=55)
    assert user.risk_score == 55


def test_user_risk_level_set():
    user = User(name="jane@example.com", uid="uid-12", risk_level=RiskLevelStr.MEDIUM)
    assert user.risk_level == RiskLevelStr.MEDIUM


def test_user_risk_level_id_set():
    user = User(name="jane@example.com", uid="uid-13", risk_level_id=RiskLevelId.MEDIUM)
    assert user.risk_level_id == RiskLevelId.MEDIUM


def test_user_all_risk_fields_together():
    user = User(
        name="jane@example.com",
        uid="uid-14",
        risk_score=90,
        risk_level=RiskLevelStr.CRITICAL,
        risk_level_id=RiskLevelId.CRITICAL,
    )
    assert user.risk_score == 90
    assert user.risk_level == RiskLevelStr.CRITICAL
    assert user.risk_level_id == RiskLevelId.CRITICAL


def test_user_risk_level_all_enum_values():
    for level_str, level_id in [
        (RiskLevelStr.INFO, RiskLevelId.INFO),
        (RiskLevelStr.LOW, RiskLevelId.LOW),
        (RiskLevelStr.MEDIUM, RiskLevelId.MEDIUM),
        (RiskLevelStr.HIGH, RiskLevelId.HIGH),
        (RiskLevelStr.CRITICAL, RiskLevelId.CRITICAL),
        (RiskLevelStr.OTHER, RiskLevelId.OTHER),
    ]:
        user = User(
            name="jane@example.com",
            uid="uid-enum",
            risk_level=level_str,
            risk_level_id=level_id,
        )
        assert user.risk_level == level_str
        assert user.risk_level_id == level_id
