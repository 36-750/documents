from ..dominoes import best_chain, search

def test_simple_chains():
    dominoes = [(4,2), (2,5), (5,1), (0, 4)]
    res = search(dominoes, best_chain)
    assert res.score == 23

    dominoes = [(4,2), (2,5), (5,1), (0, 4), (5, 7)]
    res = search(dominoes, best_chain)
    assert res.score == 29

    dominoes = [(4,2), (2,5), (5,1), (0, 4), (5, 7), (4, 9), (9, 6)]
    res = search(dominoes, best_chain)
    assert res.score == 32

    dominoes = [(0,2), (2,2), (2,3), (3,4), (3,5), (0,1), (10,1), (9, 10)]
    res = search(dominoes, best_chain)
    assert res.score == 31

