from abstract_utilities import *

def normalize_anchor_idl(raw_idl: dict) -> dict:
    """
    Converts a raw on-chain Anchor IDL into a registry-compatible IDL.
    """

    out = {
        "version": raw_idl.get("version", "0.1.0"),
        "name": raw_idl.get("name", "unknown"),
        "instructions": [],
        "accounts": raw_idl.get("accounts", []),
        "events": raw_idl.get("events", []),
        "errors": raw_idl.get("errors", []),
        "types": raw_idl.get("types", []),
        "metadata": raw_idl.get("metadata", {})
    }

    for ix in raw_idl.get("instructions", []):
        inst = dict(ix)

        # normalize discriminator → byte array
        disc = ix.get("discriminator")
        if isinstance(disc, str):
            inst["discriminator"] = list(bytes.fromhex(disc))
        elif isinstance(disc, bytes):
            inst["discriminator"] = list(disc)

        out["instructions"].append(inst)

    return out
file_path ="/home/flerb/Downloads/solana-defi-main/PumpFun/Typescript/stream_pumpfun_txns_fetch_bonding_pool_liquidity/idls/idl.json"
data = safe_load_from_json(file_path)
data = normalize_anchor_idl(data)
safe_dump_to_json(data=data,file_path=file_path)
