from ..zipper import zipper, node, root, up, down, left, right, leftmost, rightmost

from pyrsistent  import pmap, pvector, m, v, PMap, PVector
from typing      import Annotated, Any, Callable, Generic, Mapping, NamedTuple, NewType, TypeVar, Union

Node = NewType('Node', Union[int, list['Node']])

def is_br(node: Node) -> bool:
    return isinstance(node, list)

def cs(node: Node) -> list[Node]:
    return node

def mn(node: Node, children: list[Node]) -> Node:
    return children

def test_basic_zipper_moves():
    data = [[1, 2, [3, 30, [300]]], 4, 5]
    z = zipper(is_br, cs, mn, data)
    zd2d = down(down(z), 2)

    out = node(zd2d)
    assert out == [3, 30, [300]]
    assert node(left(zd2d)) == 2
    assert node(right(left(zd2d))) == out
    assert node(leftmost(zd2d)) == 1
    assert node(rightmost(up(zd2d))) == 5

    out = node(down(zd2d, 2))
    assert out == [300]
    assert root(down(zd2d, 2)) == data

    out = node(down(down(zd2d, 2)))
    assert out == 300

    out = node(up(down(zd2d, 2)))
    assert out == [3, 30, [300]]

    out = node(down(z, 1))
    assert out == 4


