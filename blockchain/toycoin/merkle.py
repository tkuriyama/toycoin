# Merkle Hash Tree

from toycoin import hash
from typing import List, Optional, Tuple


################################################################################


Hash = bytes



class MerkleTree:
    """Merkle hash tree.
    Initialize with from_singleton() and from_list() functions.
    """

    def __init__(self,
                 label: Hash,
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
        """Helper for initializing size."""
        if left is not None and right is not None:
            size = left.size + right.size + 1
        elif left is not None:
            size = left.size + 1
        else:
            size = 1
        return size


    def insert(self, leaf: Hash):
        """Recurse insertion."""
        # base cases
        if self.left is None:
            self.left = MerkleTree(b'\x00' + leaf)
            self.update()

        elif self.right is None:
            self.right = MerkleTree(b'\x00' + leaf)
            self.update()

        elif self.left.size == self.right.size:
            self.left = MerkleTree(self.label, self.left, self.right)
            self.right = from_singleton(leaf)
            self.update()

        # recursive case
        else:
            self.right.insert(leaf)
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


def from_singleton(leaf: Hash) -> MerkleTree:
    """Create singleton Merkle tree, with root and one leaf."""
    leaf_node = MerkleTree(b'\x00' + leaf)
    root = MerkleTree(b'', leaf_node)
    root.update()
    return root


def from_list(leaves: List[Hash]) -> Optional[MerkleTree]:
    """Create Merkle tree from one or more nodes."""
    if not leaves:
        return None

    head, tail = leaves[0], leaves[1:]
    t = from_singleton(head)
    for leaf in tail:
        t.insert(leaf)

    return t


################################################################################
# Verification

MaybeLeft = Optional[Hash]
MaybeRight = Optional[Hash]
HashTriple = Tuple[Hash, MaybeLeft, MaybeRight]
HashPath = List[HashTriple]


def valid(tree: MerkleTree) -> bool:
    """Return True if all tree hashes are valid."""
    if is_leaf(tree):
        return tree.label[0] == 0 and len(tree.label) > 1

    assert tree.left is not None
    if tree.right is None:
        hash_ = b'\x01' + hash.hash(tree.left.label)
        valid_ = tree.label == hash_ and valid(tree.left)
    else:
        hash_ = b'\x01' + hash.hash(tree.left.label + tree.right.label)
        valid_ = tree.label == hash_ and valid(tree.left) and valid(tree.right)

    return valid_


def contains(tree: MerkleTree, leaf: Hash) -> HashPath:
    """Find hash path to leaf (or empty path if none found)."""
    paths = [[(tree, get_hash_triple(tree))]]

    while paths:
        path = paths.pop()
        t, (label, _, _) = path[-1]
        if label == b'\x00' + leaf:
            return [triple for _, triple in path]
        elif not is_leaf(t):
            paths.extend(extend_path(path, t))

    return []


def extend_path(path: List[Tuple[MerkleTree, HashTriple]],
                tree: MerkleTree,
                ) -> List[List[Tuple[MerkleTree, HashTriple]]]:
    """Extend path if possible."""
    paths = []
    for t in (tree.left, tree.right):
        if t is not None:
            path_ = path + [(t, get_hash_triple(t))]
            paths.append(path_)
    return paths


def get_hash_triple(tree: MerkleTree) -> HashTriple:
    """Extract Hash triple for from given tree."""
    return (tree.label, get_label(tree.left), get_label(tree.right))


################################################################################
# Helpers


def is_leaf(tree: MerkleTree) -> bool:
    """Return True if given tree is a leaf node."""
    return tree.left is None and tree.right is None

def get_label(tree: Optional[MerkleTree]) -> Optional[Hash]:
    """Maybe get label."""
    maybe_label : Optional[Hash]
    if tree is not None:
        maybe_label = tree.label
    else:
        maybe_label = None
    return maybe_label


def show(tree: MerkleTree, level: int = 1, show_prefix: bool = False):
    """Print string representation of tree."""
    indent = '--' * level
    label = tree.label.hex() if show_prefix else tree.label[1:].hex()
    print(f'{indent} Level {level} | Size {tree.size} | ' +
          f'Label: {label}\n')

    if tree.left is not None:
        show(tree.left, level + 1, show_prefix)
    if tree.right is not None:
        show(tree.right, level + 1, show_prefix)

