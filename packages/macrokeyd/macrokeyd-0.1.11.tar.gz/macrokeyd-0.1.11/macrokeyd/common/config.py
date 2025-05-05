import json
import os

class ConfigLoader:
    def __init__(self, filepath=None):
        self.filepath = filepath or self.get_default_config_path()
        self.ensure_exists()
        self.meta = None
        self.macros = None
        self.load_and_validate()

    def ensure_exists(self):
        if not os.path.exists(self.filepath):
            default_config = {
                "meta": {
                    "target_device_name": "TuTeclado"
                },
                "macros": {
                    "KEY_A": {
                        "action": "text",
                        "value": "Texto por defecto"
                    },
                    "KEY_B": {
                        "action": "command",
                        "value": "echo Comando por defecto"
                    }
                }
            }
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w') as f:
                json.dump(default_config, f, indent=4)

    def load_and_validate(self):
        with open(self.filepath, 'r') as f:
            config = json.load(f)

        self.validate(config)

        self.meta = config['meta']
        self.macros = config['macros']

    def validate(self, config):
        if 'meta' not in config:
            raise ValueError("El archivo de configuración no es válido: falta 'meta'.")

        if 'macros' not in config:
            raise ValueError("El archivo de configuración no es válido: falta 'macros'.")

        if 'target_device_name' not in config['meta']:
            raise ValueError("El archivo de configuración no es válido: falta 'target_device_name' en 'meta'.")

    @staticmethod
    def get_default_config_path():
        xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return os.path.join(xdg_data_home, "macrokeyd", "default.json")

    def get_target_device_name(self):
        return self.meta.get('target_device_name')

    def get_macros(self):
        return self.macros
