#!/usr/bin/env python3

import tempfile
import gallery_dvk.config
import metadata_magic.file_tools
from os.path import abspath, exists, join

def test_get_config():
    """
    Tests the get_config function
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test getting config from valid JSON
        config_file = abspath(join(temp_dir, "config.json"))
        config = {"some":"things", "to":"test"}
        metadata_magic.file_tools.write_json_file(config_file, config)
        assert exists(config_file)
        read_config = gallery_dvk.config.get_config([config_file])
        assert read_config["some"] == "things"
        assert read_config["to"] == "test"
        # Test getting config info with no valid files
        text_file = abspath(join(temp_dir, "text.json"))
        metadata_magic.file_tools.write_text_file(text_file, "text.txt")
        assert exists(text_file)
        read_config = gallery_dvk.config.get_config(["non/existant.json", text_file])
        assert read_config == {}
        # Test getting config info with JSON in the list
        read_config = gallery_dvk.config.get_config(["non/existant.json", text_file, config_file])
        assert read_config["some"] == "things"
        assert read_config["to"] == "test"

