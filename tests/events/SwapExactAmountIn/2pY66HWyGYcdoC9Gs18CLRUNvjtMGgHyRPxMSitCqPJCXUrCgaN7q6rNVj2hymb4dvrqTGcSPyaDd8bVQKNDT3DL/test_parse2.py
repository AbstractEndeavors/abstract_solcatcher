import json
import base64
import hashlib
from abstract_utilities import *
from abstract_solcatcher import *
from borsh_construct import (
    CStruct, U8, U16, U32, U64, U128, I128, Bool
)

# -------------------------------------------------
# Borsh type map (Anchor-compatible)
# -------------------------------------------------

BORSH_TYPES = {
    "u8": U8,
    "u16": U16,
    "u32": U32,
    "u64": U64,
    "u128": U128,
    "i128": I128,
    "bool": Bool,
}

def get_parsed_log(idx,parsed_logs):
    descriminator_text = None
    parsed_logs_ = parsed_logs.copy()
    idx_ints = idx.split('.')
    for i,idx_int in enumerate(idx_ints):
        if i != 0:
            parsed_logs_ = parsed_logs_.get('children')

        idx_curr = int(idx_int)-1
        parsed_logs_ = parsed_logs_[idx_curr]
        logs = parsed_logs_.get('logs')
        if logs:
            descriminator_text = logs[0]
        
    return parsed_logs_,descriminator_text
# -------------------------------------------------
# Helpers
# -------------------------------------------------

def event_discriminator(event_name: str) -> bytes:
    return hashlib.sha256(f"event:{event_name}".encode()).digest()[:8]


def build_borsh_schema(fields):
    items = []
    for f in fields:
        ty = f["type"]
        if isinstance(ty, str):
            items.append((f["name"], BORSH_TYPES[ty]))
        else:
            raise NotImplementedError(f"Unsupported type: {ty}")
    return CStruct(*items)


# -------------------------------------------------
# Build event registry from IDL JSON
# -------------------------------------------------

def build_event_registry(idl_json):
    registry = {}

    # Accept either a single IDL or a list of IDLs
    idls = idl_json if isinstance(idl_json, list) else [idl_json]

    for idl in idls:
        for ev in idl.get("events", []):
            disc = event_discriminator(ev["name"]).hex()

            registry[disc] = {
                "name": ev["name"],
                "schema": build_borsh_schema(ev["fields"]),
                "idl_name": idl.get("name"),
                "program_id": idl.get("metadata", {}).get("address"),
            }

    return registry

# -------------------------------------------------
# Decode event payload
# -------------------------------------------------

def decode_event(call_json, event_registry):
    raw = base64.b64decode(call_json["b64"])

    disc = raw[:8].hex()
    payload = raw[8:]

    if disc not in event_registry:
        raise KeyError(f"Unknown event discriminator: {disc}")

    entry = event_registry[disc]
    decoded = entry["schema"].parse(payload)

    return {
        "program_id": call_json["program_id"],
        "event": entry["name"],
        "discriminator": disc,
        "decoded": dict(decoded),
    }


def build_instruction_registry(instructions_json):
    registry = {}

    for ins in instructions_json:
        name = ins["instruction"]

        args = ins.get("args") or {}
        disc = None

        # discriminator may or may not exist
        if "discriminator" in args:
            disc_val = args["discriminator"]["value"]
            disc_type = args["discriminator"]["type"]
            disc = {
                "type": disc_type,
                "value": disc_val,
            }

        registry[ins["id"]] = {
            "instruction": name,
            "index": ins["index"],
            "discriminator": disc,
            "args": {
                k: v["type"]
                for k, v in args.items()
                if k != "discriminator"
            },
            "anchor_event": ins.get("anchor_event"),
        }

    return registry
# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    IDL_PATH = "instructions.json"
    CALL_PATH = "call.json"
    abs_dir = get_caller_dir()
    signature = os.path.basename(abs_dir)
    event_dir = os.path.dirname(abs_dir)
    anchor_event = os.path.basename(event_dir)
    logdata = fetch_any_combo(columnNames='*', tableName='logdata', searchColumn='signature',searchValue=signature)
    parsed_logs = logdata[0].get('parsed_logs')
    instructions = safe_load_from_json(IDL_PATH)
    for instruction in instructions:
        idx = instruction.get('index')
        parsed_log,descriminator_text = get_parsed_log(idx,parsed_logs)
        instruction['program_id'] = parsed_log.get('program_id')
        instruction['descriminator_text'] = descriminator_text
        print(f"descriminator_text == {descriminator_text}")
        if descriminator_text and anchor_event.lower() in descriminator_text.lower():
            
            input(instruction)



    registry = build_instruction_registry(instructions)

    print(json.dumps(registry, indent=2))
