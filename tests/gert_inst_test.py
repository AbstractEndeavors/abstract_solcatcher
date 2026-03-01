from abstract_webtools import *
from abstract_utilities import *
from bs4 import BeautifulSoup
import re
import json

ARG_BLOCK_RE = re.compile(r"\(\{\s*(.*?)\s*\}\)", re.DOTALL)

def parse_instruction(div):
    out = {
        "program": None,
        "instruction": None,
        "args_raw": None,
        "args": None,
        "anchor_event": None,
    }

    # ── Program ─────────────────────────────────────────────
    a = div.select_one("a[href^='/account/']")
    if a:
        out["program"] = a.get_text(strip=True)

    # ── Instruction name (.sell, .route_v2, etc.) ───────────
    instr = div.select_one("div.not-italic.text-neutral7")
    if instr:
        out["instruction"] = instr.get_text(strip=True).lstrip(".")

    # ── Argument / discriminator block (TEXT, not JSON) ────
    text = div.get_text(" ", strip=True)

    m = ARG_BLOCK_RE.search(text)
    if m:
        raw = m.group(1)
        out["args_raw"] = raw
        out["args"] = normalize_args(raw)

    # ── Anchor event (name + data) ──────────────────────────
    if '"name":' in text and '"data":' in text:
        out["anchor_event"] = extract_anchor_event(text)

    return out
from bs4 import BeautifulSoup

def get_instruction_rows(html: str):
    soup = BeautifulSoup(html, "lxml")

    tree = soup.find("div", attrs={"role": "tree"})
    if not tree:
        raise RuntimeError("instruction tree not found")

    rows = tree.find_all(
        "div",
        id=lambda v: isinstance(v, str) and v.startswith("ins-action")
    )
    return rows
def extract_instruction_header(row):
    # index: "3.1.2"
    idx_div = row.find("div", string=lambda s: s and s.strip()[0].isdigit())
    index = idx_div.get_text(strip=True) if idx_div else None

    # instruction name: ".buy", ".transfer", ".Unknown"
    instr_div = row.find(
        "div",
        string=lambda s: isinstance(s, str) and s.strip().startswith(".")
    )
    instruction = instr_div.get_text(strip=True)[1:] if instr_div else None

    return index, instruction
import re

FIELD_RE = re.compile(
    r'"([^"]+)"\s*:\s*\{\s*"type"\s*:\s*"([^"]+)"\s*,\s*"data"\s*:\s*"?(.*?)"?\s*\}'
)

import re

TYPED_ARG_BLOCK_RE = re.compile(
    r'\(\{\s*(.*?)\s*\}\)', 
    re.DOTALL
)

TYPED_FIELD_RE = re.compile(
    r'"([^"]+)"\s*:\s*\{\s*"type"\s*:\s*"([^"]+)"\s*,\s*"data"\s*:\s*"?(.*?)"?\s*\}',
    re.DOTALL
)

def parse_typed_args(row):
    text = row.get_text(" ", strip=True)

    # Find the ({ ... }) block
    m = TYPED_ARG_BLOCK_RE.search(text)
    if not m:
        return None

    body = m.group(1)
    args = {}

    for name, typ, val in TYPED_FIELD_RE.findall(body):
        # normalize value
        if typ in ("u8", "u16", "u32", "u64", "i64", "u128"):
            try:
                val = int(val)
            except ValueError:
                pass
        elif typ == "bool":
            val = val.lower() == "true"

        args[name] = {
            "type": typ,
            "value": val
        }

    return args or None
ANCHOR_EVENT_RE = re.compile(
    r'"name"\s*:\s*"([^"]+)"\s*,\s*"data"\s*:\s*\{(.*?)\}\s*\}',
    re.DOTALL
)

def parse_anchor_event(row):
    text = row.get_text(" ", strip=True)

    m = ANCHOR_EVENT_RE.search(text)
    if not m:
        return None

    name = m.group(1)
    body = m.group(2)

    fields = re.findall(
        r'"([^"]+)"\s*:\s*(true|false|"[^"]*"|\d+)',
        body
    )

    data = {}
    for k, v in fields:
        if v in ("true", "false"):
            v = v == "true"
        elif v.isdigit():
            v = int(v)
        else:
            v = v.strip('"')
        data[k] = v

    return {
        "event": name,
        "data": data
    }
def parse_instruction_row(row):
    index, instruction = extract_instruction_header(row)

    return {
        "id": row.get("id"),
        "index": index,
        "instruction": instruction,
        "args": parse_typed_args(row),
        "anchor_event": parse_anchor_event(row),
    }
def parse_instruction_tree(html: str):
    rows = get_instruction_rows(html)
    return [parse_instruction_row(r) for r in rows]
def get_soup_code(file_path):
    source_code = read_from_file(file_path)
    soup_mgr = soupManager(source_code=source_code)
    return soup_mgr
def get_source_code(file_path):
    return read_from_file(file_path)
def get_instructions_tree(file_path):

    html = get_source_code(file_path)
    return parse_instruction_tree(html)
