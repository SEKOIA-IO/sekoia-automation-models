from sekoia_automation_models.ocsf.device import OperatingSystem, OSTypeId
from sekoia_automation_models.ocsf.software import (
    Fingerprint,
    FingerprintAlgorithmId,
    FingerprintAlgorithmStr,
    SoftwareEnrichmentObject,
    SoftwarePackage,
)


def test_operating_system_keeps_provided_fields():
    os = OperatingSystem(name="Ubuntu", type_id=OSTypeId.LINUX)
    assert os.name == "Ubuntu"
    assert os.type_id == OSTypeId.LINUX


def test_fingerprint_syncs_algorithm_from_id():
    # Fingerprint carries a model_validator that fills the string enum from the id
    fp = Fingerprint(algorithm_id=FingerprintAlgorithmId.SHA256, value="abc")
    assert fp.algorithm == FingerprintAlgorithmStr.SHA256


def test_software_enrichment_object_nests_os():
    obj = SoftwareEnrichmentObject.model_validate(
        {
            "name": "vim",
            "version": "9.0",
            "os": {"name": "Ubuntu", "type_id": OSTypeId.LINUX},
        }
    )
    assert obj.name == "vim"
    assert obj.os is not None
    assert obj.os.type_id == OSTypeId.LINUX


def test_public_schema_is_generatable():
    # Guards against unresolved forward references across the vendored modules
    SoftwareEnrichmentObject.model_json_schema()


def test_software_objects_carry_a_purl():
    obj = SoftwareEnrichmentObject.model_validate(
        {"name": "vim", "version": "9.0", "purl": "pkg:deb/ubuntu/vim@9.0?arch=amd64"}
    )
    assert obj.purl == "pkg:deb/ubuntu/vim@9.0?arch=amd64"
    package = SoftwarePackage(name="vim", version="9.0", purl="pkg:deb/ubuntu/vim@9.0")
    assert package.purl == "pkg:deb/ubuntu/vim@9.0"
    assert SoftwarePackage(name="vim", version="9.0").purl is None
