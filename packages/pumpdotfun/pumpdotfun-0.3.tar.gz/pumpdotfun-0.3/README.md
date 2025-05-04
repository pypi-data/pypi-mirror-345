# MyLibrary

PumpFun SDK is a Python toolkit for interacting with the Pump.fun protocol on the Solana blockchain. This SDK provides modules for building transactions, monitoring on-chain events, decoding transactions with IDL support, and analyzing bonding curve states.

## Features
- Transaction Building: Create buy and sell transactions with pre-defined instruction discriminators.
- On-Chain Monitoring: Subscribe to logs and account updates via websockets.
- Transaction Analysis: Decode and analyze transactions using a provided IDL.
- Bonding Curve Analysis: Parse on-chain bonding curve state and compute token prices.
- Token Operations: Retrieve token information, prices, holders, transactions, and liquidity.
- User Operations: Track user's created tokens, trading history, and liquidity positions.

## Installation

You can install the library with pip:

```bash
pip install pumpdotfun