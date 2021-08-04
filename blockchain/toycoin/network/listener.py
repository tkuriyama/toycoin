"""Listener node.
"""


import asyncio # type: ignore
import argparse, uuid # type: ignore
from toycoin import transaction # type: ignore
from toycoin.network import serialize # type: ignore
from toycoin.network.msg_protocol import read_msg, send_msg # type: ignore


################################################################################


async def main(args):
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    reader, writer = await asyncio.open_connection(args.host, args.port)
    print(f'I am {writer.get_extra_info("sockname")}')
    channel = args.listen.encode()
    await send_msg(writer, channel)

    try:
        while data := await read_msg(reader):
            txn_pair = serialize.unpack_txn_pair(data)
            print(f'Received by {me}: {show_txn_pair(txn_pair)}')
            print('Connection ended.')
    except asyncio.IncompleteReadError:
        print('Server closed.')

    finally:
        writer.close()
        await writer.wait_closed()


################################################################################
# Printers


def show_txn_pair(txn_pair: transaction.TxnPair) -> str:
    """Return stringoof transaction pair."""
    tokens, txn = txn_pair
    
    tokens = '\n'.join(serialize.pack_token(token, True) for token in tokens)
    s1 = f'Tokens\n{tokens}'
    s2 = f'Transaction\n{serialize.pack_txn(txn, True)}'

    return f'\n{"-" * 80}\n{s1}\n{s2}'


################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000)
    parser.add_argument('--listen', default='/topic/txn')

    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
