
## Overview

To try out `toycoin` in the terminal...

1. Follow the [installation](https://github.com/tkuriyama/toycoin/tree/master/blockchain) instructions, noting Python version etc
2. Try the below steps (running in multiple terminal windows, or e.g. split panes with `tmux`)

See also this [write-up](http://localhost:4000/crypto/2021/08/10/toycoin-part6b-nodes.html), which provides some sample output from each of the scripts.


## Running Toycoin in the Terminal

All of the scripts involved reside under [`blockchian/toycoin/network`](https://github.com/tkuriyama/toycoin/tree/master/blockchain/toycoin/network).

1. start a message relay: `python relay.py`
2. start a listner: `python listener.py`
3. start a node: `python node.py`
4. start a transaction oracle: `python txn_oracle.py`

All of the scripts have default addresses and ports, so they should "just work".

Multiple nodes can be started, with delays to simulate slower CPUs, e.g. `python node.py --delay=5`, which delays the node by 5 seconds each time it tries to generate a block.



