from solana.rpc.api import Pubkey
from solana.rpc.api import Client
import base64
import zlib
import json
from abstract_apis import *
def get_account_info(address):
    url = 'https://solcatcher.io/ratelimiter/fetch-accountInfo/'
    return postRequest(url,data={"address":str(address)})
    
client = Client("https://api.mainnet-beta.solana.com")

def get_idl_address(program_id: str) -> Pubkey:
    return Pubkey.find_program_address(
        [b"anchor:idl"],
        Pubkey.from_string(program_id)
    )[0]

def fetch_raw_idl(program_id: str) -> dict:
    idl_addr = get_idl_address(program_id)

    resp = get_account_info(idl_addr)

    if resp["result"]["value"] is None:
        raise RuntimeError("IDL account not found (program may not be Anchor)")

    data_b64 = resp["result"]["value"]["data"][0]
    raw = base64.b64decode(data_b64)

    # Anchor IDL account layout:
    # [8 bytes discriminator][4 bytes length][zlib-compressed json]
    compressed = raw[8 + 4:]
    json_bytes = zlib.decompress(compressed)

    return json.loads(json_bytes)

idl = fetch_raw_idl("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")

print(idl.keys())
