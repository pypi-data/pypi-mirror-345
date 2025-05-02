Behaviour json
==============

Here we detail the json-schema for the custom json based file format needed to import data into Antelop from a NWB file.

.. code-block:: python

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "specification": {"type": "string", "const": "antelop-behaviour"},
            "version": {"type": "string"},
            "reference_point": {"type": "string"},
            "features": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "source": {
                            "type": "object",
                            "properties": {
                                "source_type": {
                                    "type": "string",
                                    "enum": [
                                        "acquisition",
                                        "stimulus",
                                        "processing",
                                        "deeplabcut",
                                    ],
                                },
                                "module": {"type": "string"},
                                "video": {"type": "string"},
                            },
                            "required": ["source_type"],
                        },
                        "ownership": {
                            "type": "object",
                            "properties": {
                                "ownership": {
                                    "type": "string",
                                    "enum": ["world", "self"],
                                },
                                "animal": {"type": "integer"},
                            },
                            "required": ["ownership"],
                        },
                        "data_type": {
                            "type": "string",
                            "enum": ["digital", "analog", "interval", "kinematics"],
                        },
                        "coordinates": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {"type": "number"},
                        },
                        "description": {"type": "string"},
                    },
                    "required": ["name", "source", "data_type", "description"],
                },
            },
            "videos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "format": {"type": "string", "enum": ["avi", "mp4", "mov"]},
                        "reference_point": {"type": "string"},
                    },
                    "required": ["name", "description", "format"],
                },
            },
        },
        "required": ["specification", "version", "reference_point", "features"],
    }
