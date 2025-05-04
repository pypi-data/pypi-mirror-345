import base58
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from pumpdotfun.utils import (cli_log)

LAMPORTS_PER_SOL = 1_000_000_000


def create_wallet():
    keypair = Keypair.generate()
    public_key = str(keypair.public_key)
    private_key = base58.b58encode(keypair.secret_key).decode()
    return {"Pubkey": public_key, "privateKey": private_key}

def get_public_key(private_key: str):
    try:
        keypair = Keypair.from_secret_key(base58.b58decode(private_key))
        return str(keypair.public_key)
    except Exception:
        return None

def is_valid_address(public_key: str):
    try:
        Pubkey(public_key)
        return True
    except Exception:
        return False

def get_balance(connection: Client, public_key: str, lamports: bool = False):
    try:
        response = connection.get_balance(Pubkey(public_key))
        balance = response['result']['value']
        return balance if lamports else balance / LAMPORTS_PER_SOL
    except Exception as e:
        print("get_balance error:", e)
        return 0

def send_sol(connection: Client, sender: Keypair, receiver: Pubkey, amount: int):
    try:
        lamports_to_send = amount - 5000
        tx = Transaction()
        tx.add(transfer(
            TransferParams(
                from_pubkey=sender.public_key,
                to_pubkey=receiver,
                lamports=lamports_to_send
            )
        ))
        response = connection.send_transaction(tx, sender, opts=TxOpts(skip_confirmation=False))
        return 'result' in response and 'signature' in response['result']
    except Exception as e:
        print("send_sol error:", e)
        return False

def get_keypair_from_private_key(private_key: str) -> Keypair:
    return Keypair.from_secret_key(base58.b58decode(private_key))

async def is_invalid_keypair(keypair: Keypair):
    try:
        if not keypair:
            return True
        await cli_log(f"Invalid. {keypair}")
        return False
    except Exception as e:
        print(e)
        return False

def print_sol_balance(connection: Client, pub_key: Pubkey, info: str = ""):
    balance = connection.get_balance(pub_key)["result"]["value"]
    print(f"{info + ' ' if info else ''}{str(pub_key)}: {balance / LAMPORTS_PER_SOL} SOL")

def base_to_value(base: int, decimals: int) -> float:
    return base * (10 ** decimals)

def value_to_base(value: float, decimals: int) -> int:
    return int(value / (10 ** decimals))
