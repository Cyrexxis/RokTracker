from pathlib import Path
import json
from roktracker.kingdom.types.additional_data import AdditionalData as KingdomAddData
from roktracker.kingdom.types.governor_data import GovernorData as KingdomGovData
from roktracker.utils.types.batch_scanner.additional_data import AdditionalData
from roktracker.utils.types.batch_scanner.batch_type import BatchStatus
from roktracker.utils.types.batch_scanner.governor_data import GovernorData
from roktracker.utils.types.full_config import FullConfig
from roktracker.utils.types.scan_preset import ScanPreset


full_config_schema = FullConfig.model_json_schema(mode="serialization")
scan_preset_schema = ScanPreset.model_json_schema(mode="serialization")
kingdom_governor_data_schema = KingdomGovData.model_json_schema(mode="serialization")
kingdom_additional_data_schema = KingdomAddData.model_json_schema(mode="serialization")
batch_governor_data_schema = GovernorData.model_json_schema(mode="serialization")
batch_additional_data_schema = AdditionalData.model_json_schema(mode="serialization")
batch_type_schema = BatchStatus.model_json_schema(mode="serialization")


Path("./schema").mkdir(parents=True, exist_ok=True)
with open("./schema/full_config.json", "w") as f:
    f.write(json.dumps(full_config_schema, indent=2))

with open("./schema/scan_preset.json", "w") as f:
    f.write(json.dumps(scan_preset_schema, indent=2))

with open("./schema/kingdom_governor_data.json", "w") as f:
    f.write(json.dumps(kingdom_governor_data_schema, indent=2))

with open("./schema/kingdom_additional_data.json", "w") as f:
    f.write(json.dumps(kingdom_additional_data_schema, indent=2))

with open("./schema/batch_governor_data.json", "w") as f:
    f.write(json.dumps(batch_governor_data_schema, indent=2))

with open("./schema/batch_additional_data.json", "w") as f:
    f.write(json.dumps(batch_additional_data_schema, indent=2))

with open("./schema/batch_type.json", "w") as f:
    f.write(json.dumps(batch_type_schema, indent=2))
