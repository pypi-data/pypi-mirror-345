from vertibit_osi_image_generator.verti_file_config_aux.file_config import load_config_schema, load_verti_config, apply_defaults, validate_config


def load_and_validate_config(image_config_path='verti-osi.yaml', config_file='config.json'):
    config_schema_json = load_config_schema(config_file=config_file)
    provided_config = load_verti_config(config_path=image_config_path)

    config_with_defaults = apply_defaults(
        config=provided_config, schema=config_schema_json)
    config = validate_config(
        config=config_with_defaults, schema=config_schema_json)

    return config
