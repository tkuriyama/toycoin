"""Toycoin node.
"""


import asyncio # type: ignore
from asyncio import Queue # type: ignore
import argparse, uuid # type: ignore
from toycoin import block, transaction # type: ignore
from toycoin.network import serialize, show # type: ignore
from toycoin.network.msg_protocol import read_msg, send_msg # type: ignore
from typing import List, Set # type: ignore


################################################################################
# Global State

Address = bytes

BLOCKCHAIN : block.Blockchain = []


################################################################################
# Main Loop


async def main(args):
    """Main."""
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}: Full Node')
    reader, writer = await asyncio.open_connection(args.host, args.port)
    print(f'I am {writer.get_extra_info("sockname")}')

    txn_queue = Queue()
    asyncio.create_task(block_worker(txn_queue, writer))

    channel = args.channel
    print(f'Node on channel {channel}')
    await send_msg(writer, channel.encode())

    try:
        while data := await read_msg(reader):
            handle_data(data, txn_queue)
    except asyncio.IncompleteReadError:
        print('Server closed.')

    finally:
        writer.close()
        await writer.wait_closed()


################################################################################
# Data Handler


def handle_data(data: bytes, txn_queue: Queue):
    """Data handler."""
    print(f'Received message type: {data[:4].decode()}')
    if data[:4] == b'TXN ':
        txn_pair = serialize.unpack_txn_pair(data[4:])
        handle_txn(txn_pair, txn_queue)
    elif data[:4] == b'BLOC':
        blocks = serialize.unpack_blockchain(data[4:])
        handle_blocks(blocks)
    else:
        print(f'Could not handle message type {data[:4].decode()}')


def handle_txn(txn_pair: transaction.TxnPair, txn_queue: Queue):
    """"Handle transaction pair.
    Append to txn queue if the tokens are valid payments for the txn.
    """
    tokens, txn = txn_pair
    if not transaction.valid_txn(tokens, txn):
        print(f'Txn pair is invalid: {show.show_txn_pair(txn_pair)}\n')
        return
    txn_queue.put_nowait(txn_pair)


def handle_blocks(blocks: block.Blockchain):
    """Handle blocks.
    Update node blockchain if blocks are valid and form a longer chain.
    """
    global BLOCKCHAIN
    if len(blocks) > len(BLOCKCHAIN) and block.valid_blockchain(blocks):
        BLOCKCHAIN = blocks


################################################################################
# Block Generation


async def block_worker(txn_queue: Queue, writer: asyncio.StreamWriter):
    """Queue manager for generating blocks."""
    global BLOCKCHAIN

    token_set : Set[transaction.Token] = set()
    txns : List[transaction.Transaction] = []

    while True:
        tokens, txn = await txn_queue.get()
        if valid_tokens(txn, tokens, token_set):
            token_set = token_set | tokens
            txns.append(txn)

        if len(txns) >= 3:
            block, txns_ = await asyncio.to_thread(gen_block, txns)
            if block and block.valid_blockchain(BLOCKCHAIN + [block]):
                BLOCKCHAIN.append(block)
                await send_msg(writer, b'BLOC')
                await send_msg(writer, serialize.pack_blockchain(BLOCKCHAIN))
                txns = txns_[:] if txns_ else []
            else:
                # figure out what to do with txns
                pass


def valid_tokens(txn: transaction.Transaction,
                 tokens: List[transaction.Token],
                 token_set: Set[transaction.Token]):
    """Verify that the tokens are valid for use in the txn."""
    valid = True

    if set(tokens) & token_set:
        print(f'Some tokens already spent: {tokens}')
        valid = False
    elif not block.valid_tokens(tokens, BLOCKCHAIN):
            print(f'Some tokens don\'t have source txns: {tokens}')
            valid = False

    if not valid:
        print('Some tokens are invalid, skpping txn: {txn}')

    return valid


def gen_block(txns: List[transaction.Transaction]):
    """Try to generate a block."""
    print('Hi from blocker')

    ret = block.gen_block(b'genesis', txns, 1)
    print('Loop finished')

    return ret


################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000)
    parser.add_argument('--channel', default='/topic/main')

    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
