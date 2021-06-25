# Merkle Hash Tree

from toycoin import hash
from typing import List, Optional


################################################################################

class MerkleTree:
    """Merkle hash tree.
    Initialize with from_singleton() and from_list() functions.
    """

    def __init__(self,
                 label: bytes,
                 left: Optional['MerkleTree'] = None,
                 right: Optional['MerkleTree'] = None
                 ):
        self.label = label
        self.left = left
        self.right = right
        self.size = self.init_size(left, right)


    def init_size(self,
                  left: Optional['MerkleTree'] = None,
                  right: Optional['MerkleTree'] = None
                  ) -> int:
            """"""
            if left is not None and right is not None:
                size = left.size + right.size
            elif left is not None:
                size = left.size
            else:
                size = 1
            return size


    def insert(self, label: bytes):
        """Recurse insertion; return count of new nodes from insertion."""
        # base cases
        if self.left is None:
            self.left = MerkleTree(b'\x00' + label)
            self.update()

        elif self.right is None:
            self.right = MerkleTree(b'\x00' + label)
            self.update()

        elif self.left.size == self.right.size:
            self.left = MerkleTree(self.label, self.left, self.right)
            self.right = from_singleton(label)
            self.update()

        # recursive case
        else:
            self.right.insert(label)
            self.update()


    def update(self):
        """Update hash and size of interior node."""
        assert self.left is not None

        if self.right is None:
            labels = self.left.label
            size_ = self.left.size
        else:
            labels = self.left.label + self.right.label
            size_ = self.left.size + self.right.size
        self.label = b'\x01' + hash.hash(labels)
        self.size = 1 + size_


################################################################################
# Constructors


def from_singleton(label: bytes) -> MerkleTree:
    """Create singleton Merkle Tree, with root and one leaf."""
    leaf = MerkleTree(b'\x00' + label)
    root = MerkleTree(b'', leaf)
    root.update()
    return root


def from_list(labels: List[bytes]) -> MerkleTree:
    """Create singleton Merkle Tree, with root and one leaf."""
    if not labels:
        return MerkleTree(b'')

    head, tail = labels[0], labels[1:]
    t = from_singleton(head)
    for label in tail:
        t.insert(label)

    return t


################################################################################
# Verification


    



################################################################################
# Helpers


def show_tree(tree: MerkleTree, level: int = 1):
    """Print string representation of tree."""

    indent = '--' * level
    print(f'{indent} Level: {level} | Label: {tree.label.hex()}\n')
    if tree.left is not None:
        show_tree(tree.left, level + 1)
    if tree.right is not None:
        show_tree(tree.right, level + 1)
