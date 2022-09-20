import dominoes.zipper as Zip

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
    z = Zip.zipper(is_br, cs, mn, data)
    zd2d = Zip.down(Zip.down(z), 2)

    out = Zip.node(zd2d)
    assert out == [3, 30, [300]]
    assert Zip.node(Zip.left(zd2d)) == 2
    assert Zip.node(Zip.right(Zip.left(zd2d))) == out
    assert Zip.node(Zip.leftmost(zd2d)) == 1
    assert Zip.node(Zip.rightmost(Zip.up(zd2d))) == 5

    out = Zip.node(Zip.down(zd2d, 2))
    assert out == [300]
    assert Zip.root(Zip.down(zd2d, 2)) == data

    out = Zip.node(Zip.down(Zip.down(zd2d, 2)))
    assert out == 300

    out = Zip.node(Zip.up(Zip.down(zd2d, 2)))
    assert out == [3, 30, [300]]

    out = Zip.node(Zip.down(z, 1))
    assert out == 4


