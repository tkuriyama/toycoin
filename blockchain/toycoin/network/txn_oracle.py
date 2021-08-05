"""Transaction oracle.

Bootstraps a set of wallets and genesis transactions, and
thereafter generates random (valid) transactions periodically,
broadcasting them to the network. This provides a source of
truth against which the state of toycoin nodes can be compared.
"""


import asyncio # type: ignore
import argparse # type: ignore
import random # type: ignore
from toycoin import transaction, wallet, signature # type: ignore
from toycoin.network import serialize # type: ignore
from toycoin.network.msg_protocol import send_msg # type: ignore
from typing import List, Tuple # type: ignore
import uuid # type: ignore


################################################################################


OracleState = List[wallet.Wallet]


################################################################################
# Main Loop


async def main(args):
    """Transaction oracle main loop."""
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}: Transaction Oracle')
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    print(f'I am {writer.get_extra_info("sockname")}')

    channel = b'/connect'
    await send_msg(writer, channel)

    chan = args.channel.encode()
    try:
        txn_pairs, state = init_state()
        while True:
            await asyncio.sleep(random.randint(args.min_interval,
                                               args.max_interval))
            try:
                for txn_pair in txn_pairs:
                    data = b'TXN ' + serialize.pack_txn_pair(txn_pair).encode()
                    print(f'Sending {data[:19]}')
                    await send_msg(writer, chan)
                    await send_msg(writer, data)
                txn_pairs, state = update_state(state)

            except OSError:
                print('Connection ended.')
                break

    except asyncio.CancelledError:
        writer.close()
        await writer.wait_closed()


################################################################################
# Wallets and Transactions


def init_state() -> Tuple[List[transaction.TxnPair], OracleState]:
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

    return ([([], txn0a), ([], txn0b)],
            [a_wallet, b_wallet, c_wallet, d_wallet])


def update_state(state: OracleState
                 ) -> Tuple[List[transaction.TxnPair], OracleState]:
    """Generate a random transaction and update state of wallets."""
    print('\nGenerating new transaction...')
    print_state(state)

    while True:
        sender, receiver = draw_two(len(state) - 1)
        amount = min(random.randint(5, 15), state[sender].balance())
        if amount > 0:
            txn_pair = state[sender].send(amount,
                                          state[receiver].public_key)
            if not txn_pair:
                print('Unexpected send error...')
            else:
                print(f'Sending from wallet {sender} to {receiver}: {amount}')
                _, txn = txn_pair
                state[sender].confirm_send(transaction.hash_txn(txn))
                state[sender].receive(txn)
                state[receiver].receive(txn)
                break

    print_state(state)
    return ([txn_pair], state)


################################################################################
# Helpers


def gen_wallet() -> wallet.Wallet:
    """Generate wallet."""
    priv_key = signature.gen_priv_key()
    pub_key = signature.get_pub_key_bytes(priv_key)
    return wallet.Wallet(pub_key, priv_key)


def draw_two(max_n: int) -> Tuple[int, int]:
    """Draw two different ints given max (mod max)."""
    i = random.randint(0, max_n)
    j = (i + random.randint(1, max_n - 1)) % max_n
    return i, j


def print_state(state: OracleState):
    """Print wallet balances."""
    balances = [str(wallet.balance()) for wallet in state]
    s = f'Wallet balances: {", ".join(balances)}'
    print(s)


################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000, type=int)
    parser.add_argument('--channel', default='/topic/main')
    parser.add_argument('--min_interval', default=3, type=float)
    parser.add_argument('--max_interval', default=10, type=float)
    parser.add_argument('--size', default=0, type=int)

    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')

