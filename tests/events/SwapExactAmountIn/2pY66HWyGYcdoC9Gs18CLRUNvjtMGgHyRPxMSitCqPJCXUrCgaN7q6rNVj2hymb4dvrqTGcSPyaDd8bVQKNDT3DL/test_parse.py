#!/usr/bin/env python3
"""
Anchor IDL Parser

Parses an Anchor IDL JSON and provides:
- instruction discriminator → instruction schema
- event discriminator → event name
- type registry for defined structs
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
import base64
from abstract_utilities import *

    

# ─────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────

def disc_bytes_to_hex(disc: List[int]) -> str:
    """Convert Anchor discriminator array to hex string."""
    return bytes(disc).hex()


def normalize_arg_type(t: Any) -> str:
    """Normalize Anchor arg type into a readable string."""
    if isinstance(t, str):
        return t

    if isinstance(t, dict):
        if "defined" in t:
            return f"defined::{t['defined']['name']}"

        if "vec" in t:
            return f"vec<{normalize_arg_type(t['vec'])}>"

        if "array" in t:
            base, size = t["array"]
            return f"{base}[{size}]"

    return "unknown"


# ─────────────────────────────────────────────────────────────
# Registry Builders
# ─────────────────────────────────────────────────────────────

def build_instruction_registry(idl: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Builds:
      discriminator_hex -> instruction schema
    """
    registry = {}

    for ix in idl.get("instructions", []):
        disc_hex = disc_bytes_to_hex(ix["discriminator"])
        registry[disc_hex] = {
            "name": ix["name"],
            "docs": ix.get("docs", []),
            "accounts": ix.get("accounts", []),
            "args": ix.get("args", []),
        }

    return registry


def build_event_registry(idl: Dict[str, Any]) -> Dict[str, str]:
    """
    Builds:
      discriminator_hex -> event name
    """
    registry = {}

    for ev in idl.get("events", []):
        disc_hex = disc_bytes_to_hex(ev["discriminator"])
        registry[disc_hex] = ev["name"]

    return registry


def build_account_registry(idl: Dict[str, Any]) -> Dict[str, str]:
    """
    Builds:
      discriminator_hex -> account name
    """
    registry = {}

    for acc in idl.get("accounts", []):
        disc_hex = disc_bytes_to_hex(acc["discriminator"])
        registry[disc_hex] = acc["name"]

    return registry


def build_type_registry(idl: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds:
      type_name -> type schema
    """
    return {
        t["name"]: t["type"]
        for t in idl.get("types", [])
    }


# ─────────────────────────────────────────────────────────────
# Resolution Helpers
# ─────────────────────────────────────────────────────────────

def resolve_instruction_from_bytes(
    instruction_data: bytes,
    instruction_registry: Dict[str, Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Resolve instruction schema from raw instruction bytes.
    """
    if len(instruction_data) < 8:
        return None

    disc_hex = instruction_data[:8].hex()
    return instruction_registry.get(disc_hex)


def instruction_arg_schema(ix_schema: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Returns ordered arg schema with normalized types.
    """
    return [
        {
            "name": arg["name"],
            "type": normalize_arg_type(arg["type"]),
        }
        for arg in ix_schema.get("args", [])
    ]


def is_anchor_instruction(ix_schema: Optional[Dict[str, Any]]) -> bool:
    """
    Deterministic Anchor instruction check.
    """
    return (
        ix_schema is not None
        and "name" in ix_schema
        and "args" in ix_schema
    )


# ─────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────
from typing import Dict, Any, List
from pprint import pprint
import json


def normalize_instruction(ix: Dict[str, Any]) -> Dict[str, Any]:
    args = {}
    for name, spec in (ix.get("args") or {}).items():
        args[name] = {
            "type": spec["type"],
            "value": spec["value"]
        }

    return {
        "id": ix["id"],
        "index": ix["index"],
        "instruction": ix["instruction"],
        "discriminator": (
            ix.get("args", {}).get("discriminator", {}).get("value")
            if ix.get("args") else None
        ),
        "args": args,
        "anchor_event": ix.get("anchor_event"),
    }


def parse_instruction_trace(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_instruction(ix) for ix in trace]

import json
from typing import Dict, Any, List


def normalize_metadata(idl: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": idl.get("name"),
        "version": idl.get("version"),
        "spec": idl.get("spec", idl.get("version")),
        "description": idl.get("description", "Created with Anchor"),
    }


def normalize_instruction(ix: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": ix["name"],
        "docs": ix.get("docs", []),
        "discriminator": ix.get("discriminator"),
        "accounts": ix.get("accounts", []),
        "args": ix.get("args", []),
    }


def normalize_account(acc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": acc["name"],
        "discriminator": acc.get("discriminator"),
    }


def normalize_event(ev: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": ev["name"],
        "discriminator": ev.get("discriminator"),
    }


def normalize_error(err: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "code": err["code"],
        "name": err["name"],
        "msg": err.get("msg"),
    }


def normalize_type(ty: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": ty["name"],
        "type": ty["type"],
    }


def build_canonical_idl(
    idl: Dict[str, Any],
    program_address: str,
) -> Dict[str, Any]:

    return {
        "address": program_address,
        "metadata": normalize_metadata(idl),
        "instructions": [
            normalize_instruction(ix)
            for ix in idl.get("instructions", [])
        ],
        "accounts": [
            normalize_account(acc)
            for acc in idl.get("accounts", [])
        ],
        "events": [
            normalize_event(ev)
            for ev in idl.get("events", [])
        ],
        "errors": [
            normalize_error(err)
            for err in idl.get("errors", [])
        ],
        "types": [
            normalize_type(ty)
            for ty in idl.get("types", [])
        ],
    }


if __name__ == "__main__":
    # ---- INPUTS ----
    IDL_PATH = "/home/flerb/Documents/pythonTools/modules/src/modules/abstract_solcatcher/tests/events/SwapExactAmountIn/2pY66HWyGYcdoC9Gs18CLRUNvjtMGgHyRPxMSitCqPJCXUrCgaN7q6rNVj2hymb4dvrqTGcSPyaDd8bVQKNDT3DL/instructions.json"

    PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

    with open(IDL_PATH, "r") as f:
        raw_idl = json.load(f)

    canonical = build_canonical_idl(raw_idl, PROGRAM_ID)

    print(json.dumps(canonical, indent=2))




