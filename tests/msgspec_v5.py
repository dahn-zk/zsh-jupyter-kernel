import re

from jsonschema import Draft4Validator, ValidationError

protocol_version = (5, 1)

# These fragments will be wrapped in the boilerplate for a valid JSON schema.
# We also add a default 'required' containing all keys.
schema_fragments = {}


def get_msg_content_validator(msg_type, version_minor):
    frag = schema_fragments[msg_type]
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": f"{msg_type} message contents schema",
        "type": "object",
        "properties": {},
        "additionalProperties": version_minor > protocol_version[1],
    }
    schema.update(frag)
    if "required" not in schema:
        # Require all keys by default
        schema["required"] = sorted(schema["properties"].keys())

    return Draft4Validator(schema)


header_part = {
    "type": "object",
    "properties": {
        "msg_id": {"type": "string"},
        "username": {"type": "string"},
        "session": {"type": "string"},
        # TODO - this is parsed to a datetime before we get it:
        "date": {},  # {"type": "string"},
        "msg_type": {"type": "string"},
        "version": {"type": "string"},
    },
    "required": ["msg_id", "username", "session", "date", "msg_type", "version"],
}

msg_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Jupyter message structure schema",
    "type": "object",
    "properties": {
        "header": header_part,
        "parent_header": {"type": "object"},
        "metadata": {"type": "object"},
        "content": {"type": "object"},  # Checked separately
        "buffers": {"type": "array"},
    },
    "required": ["header", "parent_header", "metadata", "content"],
}
msg_structure_validator = Draft4Validator(msg_schema)


def get_error_reply_validator(version_minor):
    return Draft4Validator(
        {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "description": "Jupyter 'error' reply schema",
            "type": "object",
            "properties": {
                "status": {"const": "error"},
                "ename": {"type": "string"},
                "evalue": {"type": "string"},
                "traceback": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["status", "ename", "evalue", "traceback"],
            "additionalProperties": version_minor > protocol_version[1],
        }
    )


def get_abort_reply_validator(version_minor):
    return Draft4Validator(
        {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "description": "Jupyter 'abort' reply schema",
            "type": "object",
            "properties": {
                "status": {"const": "error"},
                "ename": {"type": "string"},
                "evalue": {"type": "string"},
                "traceback": {"type": "list", "items": {"type": "string"}},
            },
            "required": ["status", "ename", "evalue", "traceback"],
            "additionalProperties": version_minor > protocol_version[1],
        }
    )


reply_msgs_using_status = {
    "execute_reply",
    "inspect_reply",
    "complete_reply",
    "history_reply",
    "connect_reply",
    "comm_info_reply",
    "kernel_info_reply",
    "shutdown_reply",
    "interrupt_reply",
}


def validate_message(msg, msg_type=None, parent_id=None):
    msg_structure_validator.validate(msg)

    msg_version_s = msg["header"]["version"]
    m = re.match(r"(\d+)\.(\d+)", msg_version_s)
    if not m:
        raise ValidationError("Version {} not like 'x.y'")
    version_minor = int(m.group(2))

    if msg_type is not None:
        if msg["header"]["msg_type"] != msg_type:
            raise ValidationError(
                "Message type {!r} != {!r}".format(msg["header"]["msg_type"], msg_type)
            )
    else:
        msg_type = msg["header"]["msg_type"]

    # Check for unexpected fields, unless it's a newer protocol version
    if version_minor <= protocol_version[1]:
        unx_top = set(msg) - set(msg_schema["properties"])
        if unx_top:
            raise ValidationError(f"Unexpected keys: {unx_top}")

        unx_header = set(msg["header"]) - set(header_part["properties"])
        if unx_header:
            raise ValidationError(f"Unexpected keys in header: {unx_header}")

    # Check the parent id
    if "reply" in msg_type and parent_id and msg["parent_header"]["msg_id"] != parent_id:
        raise ValidationError("Parent header does not match expected")

    if msg_type in reply_msgs_using_status:
        # Most _reply messages have common 'error' and 'abort' structures
        try:
            status = msg["content"]["status"]
        except KeyError as e:
            raise ValidationError(str(e))
        if status == "error":
            content_vdor = get_error_reply_validator(version_minor)
        elif status == "abort":
            content_vdor = get_abort_reply_validator(version_minor)
        elif status == "ok":
            content_vdor = get_msg_content_validator(msg_type, version_minor)
        else:
            raise ValidationError(f"status {status!r} should be ok/error/abort")
    else:
        content_vdor = get_msg_content_validator(msg_type, version_minor)

    content_vdor.validate(msg["content"])


# Shell messages ----------------------------------------------

schema_fragments["execute_request"] = {
    "properties": {
        "code": {"type": "string"},
        "silent": {"type": "boolean"},
        "store_history": {"type": "boolean"},
        "user_expressions": {"type": "object"},
        "allow_stdin": {"type": "boolean"},
        "stop_on_error": {"type": "boolean"},
    }
}

schema_fragments["execute_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
        "execution_count": {"type": "number"},
        "payload": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"source": {"type": "string"}},
                "additionalProperties": True,
            },
        },
        "user_expressions": {"type": "object"},
    },
    "required": ["status", "execution_count"],
}

schema_fragments["inspect_request"] = {
    "properties": {
        "code": {"type": "string"},
        "cursor_pos": {"type": "number"},
        "detail_level": {"enum": [0, 1]},
    }
}

schema_fragments["inspect_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
        "found": {"type": "boolean"},
        "data": {"type": "object"},
        "metadata": {"type": "object"},
    }
}

schema_fragments["complete_request"] = {
    "properties": {
        "code": {"type": "string"},
        "cursor_pos": {"type": "number"},
    }
}

schema_fragments["complete_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
        "matches": {"type": "array", "items": {"type": "string"}},
        "cursor_start": {"type": "number"},
        "cursor_end": {"type": "number"},
        "metadata": {"type": "object"},
    }
}

schema_fragments["history_request"] = {
    "properties": {
        "output": {"type": "boolean"},
        "raw": {"type": "boolean"},
        "hist_access_type": {"enum": ["range", "tail", "search"]},
        "session": {"type": "number"},
        "start": {"type": "number"},
        "stop": {"type": "number"},
        "n": {"type": "number"},
        "pattern": {"type": "string"},
        "unique": {"type": "boolean"},
    },
    "required": ["output", "raw", "hist_access_type"],
}

schema_fragments["history_reply"] = {
    "properties": {
        "status": {"const": "ok"},
        "history": {"type": "array", "items": {"minItems": 3, "maxItems": 3}},
    }
}

schema_fragments["is_complete_request"] = {
    "properties": {
        "code": {"type": "string"},
    }
}

schema_fragments["is_complete_reply"] = {
    "properties": {
        "status": {"enum": ["complete", "incomplete", "invalid", "unknown"]},
        "indent": {"type": "string"},
    },
    "required": ["status"],
}

# NB connect_request is deprecated
schema_fragments["connect_request"] = {"properties": {}}

schema_fragments["connect_reply"] = {
    "properties": {
        "shell_port": {"type": "number"},
        "iopub_port": {"type": "number"},
        "stdin_port": {"type": "number"},
        "hb_port": {"type": "number"},
        "control_port": {"type": "number"},
    }
}

schema_fragments["comm_info_request"] = {
    "properties": {
        "target_name": {"type": "string"},
    },
    "required": [],
}

schema_fragments["comm_info_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
        "comms": {"type": "object"},
    }
}

schema_fragments["kernel_info_request"] = {"properties": {}}

schema_fragments["kernel_info_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
        "protocol_version": {"type": "string"},
        "implementation": {"type": "string"},
        "implementation_version": {"type": "string"},
        "language_info": {"type": "object"},
        "banner": {"type": "string"},
        "debugger": {"type": "boolean"},
        "help_links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"text": {"type": "string"}, "url": {"type": "string"}},
            },
        },
    },
    "required": ["status", "protocol_version", "implementation", "language_info", "banner"],
}

schema_fragments["shutdown_request"] = {
    "properties": {
        "restart": {"type": "boolean"},
    }
}

schema_fragments["shutdown_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
        "restart": {"type": "boolean"},
    }
}

schema_fragments["interrupt_request"] = {"properties": {}}
schema_fragments["interrupt_reply"] = {
    "properties": {
        # statuses 'error' and 'abort' change the structure, so check separately
        "status": {"const": "ok"},
    }
}

# IOPub messages ----------------------------------------------

mime_data = {
    "type": "object",
    "patternProperties": {r"^[\w\-\+\.]+/[\w\-\+\.]+$": {}},
    "additionalProperties": False,
}

schema_fragments["stream"] = {
    "properties": {
        "name": {"enum": ["stdout", "stderr"]},
        "text": {"type": "string"},
    }
}

schema_fragments["display_data"] = {
    "properties": {
        "data": mime_data,
        "metadata": {"type": "object"},
        "transient": {"type": "object"},
    },
    "required": ["data", "metadata"],
}

schema_fragments["update_display_data"] = {
    "properties": {
        "data": mime_data,
        "metadata": {"type": "object"},
        "transient": {"type": "object"},
    }
}

schema_fragments["execute_result"] = {
    "properties": {
        "execution_count": {"type": "number"},
        "data": mime_data,
        "metadata": {"type": "object"},
        "transient": {"type": "object"},
    },
    "required": ["execution_count", "data", "metadata"],
}

schema_fragments["clear_output"] = {
    "properties": {
        "wait": {"type": "boolean"},
    }
}

schema_fragments["execute_input"] = {
    "properties": {
        "code": {"type": "string"},
        "execution_count": {"type": "number"},
    }
}

schema_fragments["error"] = {
    "properties": {
        "ename": {"type": "string"},
        "evalue": {"type": "string"},
        "traceback": {"type": "array", "items": {"type": "string"}},
    }
}

schema_fragments["status"] = {
    "properties": {
        "execution_state": {"enum": ["busy", "idle", "starting"]},
    }
}

# Stdin messages ---------------------------------------------

schema_fragments["input_request"] = {
    "properties": {
        "prompt": {"type": "string"},
        "password": {"type": "number"},
    }
}

schema_fragments["input_reply"] = {
    "properties": {
        "value": {"type": "string"},
    }
}
