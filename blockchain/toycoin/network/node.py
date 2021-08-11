"""Toycoin node.

"""


import asyncio # type: ignore
from asyncio import Queue # type: ignore
import argparse, uuid # type: ignore
from toycoin import block, transaction # type: ignore
from toycoin.network import serialize, show # type: ignore
from toycoin.network.msg_protocol import read_msg, send_msg # type: ignore
from typing import List, Optional, Tuple # type: ignore


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

    channel = args.channel
    print(f'Node on channel {channel}')
    await send_msg(writer, channel.encode())

    txn_queue = Queue()
    asyncio.create_task(block_worker(txn_queue, writer, channel, args.delay))

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
        print('Received longer, valid blockchain.')
        BLOCKCHAIN = blocks
    else:
        print('Received blockchain but it is not longer, or invalid.')


################################################################################
# Block Generation


async def block_worker(txn_queue: Queue,
                       writer: asyncio.StreamWriter,
                       channel: str,
                       delay: int):
    """Queue manager for generating blocks."""
    txn_pairs : List[transaction.TxnPair] = []

    while True:
        txn_pair = await txn_queue.get()
        if valid_tokens(txn_pair, txn_pairs):
            txn_pairs.append(txn_pair)

        if len(txn_pairs) >= 2:
            txns = [txn for _, txn in txn_pairs]
            b, txns_ = await asyncio.to_thread(gen_block, txns)
            await asyncio.sleep(delay) # slow some nodes down artificially

            if b and block.valid_blockchain(BLOCKCHAIN + [b]):
                await update_blockchain(b, writer, channel)
                txn_pairs = update_txn_pairs(txn_pairs, txns_)
            else:
                print('Invalid block or blockchain')
                print(f'Dropping txns:\n{show.show_txn_hashes(txns)}\n')
                txn_pairs = []


def valid_tokens(txn_pair: transaction.TxnPair,
                 txn_pairs: List[transaction.TxnPair]):
    """Verify that tokens are valid and not double spent."""
    tokens, txn = txn_pair
    seen_tokens = [ts for ts, _ in txn_pairs]
    valid = True

    if not block.valid_tokens(tokens, BLOCKCHAIN):
        print(f'Some tokens missing source txns: {show.show_tokens(tokens)}')
        valid = False
    elif any([token in seen_tokens for token in tokens]):
        print(f'Some tokens already used in other txns: {show.show_tokens(tokens)}')
        valid = False

    return valid


def gen_block(txns: List[transaction.Transaction]
              ) -> Tuple[Optional[block.Block], List[transaction.Transaction]]:
    """Try to generate a block."""
    print('Starting block gen...')
    h = (block.GENESIS if len(BLOCKCHAIN) == 0 else
         BLOCKCHAIN[-1]['header']['this_hash'])

    b, txns_ = block.gen_block(h, txns, block.next_difficulty(len(BLOCKCHAIN)))
    block
    if b:
        print(f'Finished block gen, hash {b["header"]["this_hash"]}')
        print(f'Block has {len(b["txns"])} txns')
    else:
        print('Finished block gen but no block was generated.')
        print('Started with {len(txns)}, {len(txns_)} are leftover.')

    return b, txns_


async def update_blockchain(b: block.Block,
                            writer: asyncio.StreamWriter,
                            channel: str):
    """Update blockchain and send to network."""
    global BLOCKCHAIN
    BLOCKCHAIN.append(b)
    msg = b'BLOC' + serialize.pack_blockchain(BLOCKCHAIN).encode()
    await send_msg(writer, channel.encode())
    await send_msg(writer, msg)
    print('Sent updated blockchain')


def update_txn_pairs(txn_pairs: List[transaction.TxnPair],
                     txns: List[transaction.Transaction]
                     ) -> List[transaction.TxnPair]:
    """Filter for txn_pairs matching given txns."""
    return [(tokens, txn) for tokens, txn in txn_pairs
            if txn in txns]



################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000)
    parser.add_argument('--channel', default='/topic/main')
    parser.add_argument('--delay', default=0, type=int)

    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
