"""Listener node.
Used in toycoin for monitoring network activity, indepepdently on nodes.
"""


import asyncio # type: ignore
import argparse, uuid # type: ignore
from toycoin.network import serialize, show # type: ignore
from toycoin.network.msg_protocol import read_msg, send_msg # type: ignore


################################################################################


async def main(args):
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}: Listener')
    reader, writer = await asyncio.open_connection(args.host, args.port)
    print(f'I am {writer.get_extra_info("sockname")}')
    print(f'Listening on channel {args.listen}')
    await send_msg(writer, args.listen.encode())

    try:
        while data := await read_msg(reader):
            handle_data(data)
            print('Transmission ended.')
    except asyncio.IncompleteReadError:
        print('Server closed.')

    finally:
        writer.close()
        await writer.wait_closed()


################################################################################
# Data Handler

def handle_data(data: bytes):
    """Data handler."""
    if data[:4] == b'TXN ':
        txn_pair = serialize.unpack_txn_pair(data[4:])
        print(f'Received TXN:\n{show.show_txn_pair(txn_pair)}')
    elif data[:4] == b'BLOC':
        chain = serialize.unpack_blockchain(data[4:])
        print(f'Received BLOC:\n{show.show_blockchain(chain)}')
    else:
        print(f'Couldn not handle message type {data[:4].decode()}')


################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000)
    parser.add_argument('--listen', default='/topic/main')

    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
