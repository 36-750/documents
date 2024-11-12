# Initial Thoughts on Parser Construction Thu 07 Nov

import fp_concepts
from   fp_concepts.all import *

# type Parser a = String -> Pair String (Maybe a)

def char(input: str) -> Pair[str, Maybe[char]]:
    if not input:
        return (input, None_())
    return (input[1:], Some(input[0]))

def natural(input: str) -> Pair[str, Maybe[int]]:
    ...

# s -> Pair s (Maybe Char)
# s -> Pair s (Maybe Natural)

def both(input1: str) -> Pair[str, Maybe[Pair[char, int]]]:
    input2, mc = char(input1)
    if not mc:
        return (input, None_())
    input3, mn = natural(input2)

    if not mn:
        return (input, None_())
    return (input3, map2(pair, mc, mn))


# type Parser a = Parser (str -> Pair str (Maybe a))

# both : Parser a -> Parser b -> Parser (Pair a b)
def both(parser1: Parser[a], parser2: Parser[b]) -> Parser[Pair[a, b]]:
    def do_both(input1: str) -> Pair[str, Maybe[Pair[a, b]]]:
        input2, mc = parser1(input1)
        if not mc:
            return (input, None_())
        input3, mn = parser2(input2)
        if not mn:
            return (input, None_())
        return (input3, map2(pair, mc, mn))

    return do_both
