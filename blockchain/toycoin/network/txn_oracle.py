"""Transaction oracle.

Bootstraps a set of wallets and genesis transactions, and
thereafter generates random (valid) transactions periodically,
broadcasting them to the network. This provides a source of
truth against which the state of toycoin nodes can be compared.
"""


import asyncio # type: ignore
import argparse # type: ignore
import json # type: ignore
import random # type: ignore
from toycoin import transaction, wallet, signature # type: ignore
from toycoin.network.msg_protocol import send_msg # type: ignore
from typing import List, Tuple # type: ignore
import uuid # type: ignore


################################################################################


Txns = List[transaction.Transaction]
OracleState = List[wallet.Wallet]


################################################################################
# Main Loop


async def main(args):
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}: Transaction Oracle')
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    print(f'I am {writer.get_extra_info("sockname")}')

    channel = b'/txn'
    await send_msg(writer, channel)

    chan = args.channel.encode()
    try:
        txns, state = init_state()
        while True:
            await asyncio.sleep(random.randint(args.min_interval,
                                               args.max_interval))
            try:
                for txn in txns:
                    data = json.dumps(txn).encode()
                await send_msg(writer, chan)
                await send_msg(writer, data)
            except OSError:
                print('Connection ended.')
                break

    except asyncio.CancelledError:
        writer.close()
        await writer.wait_closed()


################################################################################
# Wallets and Transactions


def init_state() -> Tuple[Txns, OracleState]:
    """Bootstrap wallets and genesis transactions."""

    a_wallet, b_wallet = gen_wallet(), gen_wallet()
    c_wallet, d_wallet = gen_wallet(), gen_wallet()

    txn0a = {'previous_hashes': [],
             'receiver': a_wallet.public_key,
             'receiver_value': 100,
             'receiver_signature': b'',
             'sender': b'genesis',
             'sender_change': 0,
             'sender_signature': b''
             }

    txn0b = {'previous_hashes': [],
             'receiver': b_wallet.public_key,
             'receiver_value': 50,
             'receiver_signature': b'',
             'sender': b'genesis',
             'sender_change': 0,
             'sender_signature': b''
             }

    a_wallet.receive(txn0a)
    b_wallet.receive(txn0b)

    return [txn0a, txn0b,], [a_wallet, b_wallet, c_wallet, d_wallet]


################################################################################
# Helpers


def gen_wallet() -> wallet.Wallet:
    """Generate wallet."""
    priv_key = signature.gen_priv_key()
    pub_key = signature.get_pub_key_bytes(priv_key)
    return wallet.Wallet(pub_key, priv_key)


################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000, type=int)
    parser.add_argument('--channel', default='/topic/foo')
    parser.add_argument('--min_interval', default=3, type=float)
    parser.add_argument('--max_interval', default=10, type=float)
    parser.add_argument('--size', default=0, type=int)

    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

