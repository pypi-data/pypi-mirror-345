import json

def load_config(filepath):
    with open(filepath, 'r') as f:
        config = json.load(f)

    # Validaciones básicas
    if 'meta' not in config or 'macros' not in config:
        raise ValueError("El archivo de configuración no es válido: falta 'meta' o 'macros'.")

    return config['meta'], config['macros']
