from typing import get_args

from sekoia_automation_models.connector import (
    AssetItem,
    AssetList,
    DefaultAssetConnectorConfiguration,
)
from sekoia_automation_models.ocsf.device import DeviceOCSFModel
from sekoia_automation_models.ocsf.software import SoftwareOCSFModel
from sekoia_automation_models.ocsf.user import UserOCSFModel
from sekoia_automation_models.ocsf.vulnerability import VulnerabilityOCSFModel


def test_asset_item_unions_the_ocsf_models():
    assert set(get_args(AssetItem)) == {
        VulnerabilityOCSFModel,
        DeviceOCSFModel,
        UserOCSFModel,
        SoftwareOCSFModel,
    }


def test_asset_list_defaults_to_empty_items():
    asset_list = AssetList(version=1)
    assert asset_list.version == 1
    assert asset_list.items == []


def test_default_configuration_applies_defaults():
    config = DefaultAssetConnectorConfiguration(
        sekoia_base_url=None, sekoia_api_key="key"
    )
    assert config.frequency == 10800
    assert config.batch_size == 100
