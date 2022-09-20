from dataclasses import dataclass
from operator    import attrgetter
from pyrsistent  import pmap, pvector, m, v, PMap, PVector
from typing      import Annotated, Any, Callable, Generic, Mapping, NamedTuple, NewType, TypeVar, Union

def is_pvec_empty(pv: Union[PVector, None]) -> bool:
    return pv is None or len(pv) == 0

T = TypeVar('T')

@dataclass  # Want to use NamedTuple but it is not currently allows
class ZipperMeta(Generic[T]):
    is_branch: Callable[[T], bool]
    children: Callable[[T], list[T]]
    make_node: Callable[[T, list[T]], T]
    meta: Mapping[str, Any]

Zipper = tuple[T, Union[PMap, None], ZipperMeta]

def zipper(is_branch: Callable[[T], bool],
           children: Callable[[T], list[T]],
           make_node: Callable[[T, list[T]], T],
           root: T ) -> Zipper:
    return (root, None, ZipperMeta(is_branch, children, make_node, meta=m()))

def is_at_root(loc: Zipper) -> bool:
    return loc[1] is None

def assoc_meta(loc: Zipper, key: str, val: Any) -> Zipper:
    updated_meta = loc[2].meta.set(key, val)
    return (loc[0], loc[1], ZipperMeta(loc[2].is_branch,
                                       loc[2].children,
                                       loc[2].make_node,
                                       updated_meta))

def node(loc: Zipper) -> T:
    return loc[0]

def up(loc: Zipper) -> Zipper:
    node, path, meta = loc
    if path is None or not path.pnodes:
        return None  # At root
    pnodes, ppath, l, r, is_changed = attrgetter('pnodes', 'ppath', 'l', 'r', 'is_changed')(path)
    parent = pnodes[len(pnodes) - 1]
    if is_changed:
        return (meta.make_node(parent, l + v(node) + r), ppath and ppath.set('is_changed', True), meta)
    return (parent, path.ppath, loc[2])

def down(loc: Zipper, index: Annotated[int, {min: 0}] = 0) -> Zipper:
    # index defaults to first child
    # uses last child if index is > that # children, first child if <= 0
    node, path, meta = loc
    if not meta.is_branch(node):
        return None
    children = meta.children(node)
    ind = max(index, 0) if index < len(children) else len(children) - 1
    new_path = m(l=pvector(children[0:ind]),
                 r=pvector(children[(ind+1):]),
                 pnodes=path.pnodes.append(node) if not is_pvec_empty(path) else v(node),
                 ppath=path,
                 is_changed=path.is_changed if path else False)

    return (children[ind], new_path, meta)

def left(loc: Zipper) -> Zipper:
    node, path, meta = loc
    if path is None or not path.l or len(path.l) == 0:
        return None
    new_path = m(l=path.l[:-1],
                 r=v(node).extend(path.r),
                 pnodes=path.pnodes,
                 ppath=path.ppath,
                 is_changed=path.is_changed)
    return (path.l[-1], new_path, meta)

def right(loc: Zipper) -> Zipper:
    node, path, meta = loc
    if path is None or not path.r or len(path.r) == 0:
        return None
    new_path = m(l=path.l.append(node),
                 r=path.r[1:],
                 pnodes=path.pnodes,
                 ppath=path.ppath,
                 is_changed=path.is_changed)
    return (path.r[0], new_path, meta)

def leftmost(loc: Zipper) -> Zipper:
    node, path, meta = loc
    if path is None or not path.l or len(path.l) == 0:
        return loc
    new_path = m(l=v(),
                 r=path.l[1:].append(node).extend(path.r),
                 pnodes=path.pnodes,
                 ppath=path.ppath,
                 is_changed=path.is_changed)
    return (path.l[0], new_path, meta)

def rightmost(loc: Zipper) -> Zipper:
    node, path, meta = loc
    if path is None or not path.r or len(path.r) == 0:
        return loc
    new_path = m(l=path.l.append(node).extend(path.r[:-1]),
                 r=v(),
                 pnodes=path.pnodes,
                 ppath=path.ppath,
                 is_changed=path.is_changed)
    return (path.r[-1], new_path, meta)

def root(loc: Zipper) -> T:
    current = loc
    while parent := up(current):
        current = parent
    return node(current)

def replace(loc: Zipper, new_node: T) -> Zipper:
    node, path, meta = loc
    return (new_node, path and path.set('is_changed', True), meta)

def edit(loc: Zipper, editor: Callable[[T], T]) -> Zipper:
    return replace(loc, editor(loc[0]))
