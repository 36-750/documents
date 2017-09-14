import re
from collections import defaultdict

class dict_with_attributes(defaultdict):
    """A dictionary type that can accept defaults and arbitrary attributes."""
    pass

def tokenize(line):
    words = re.compile(r'([A-Za-z][-A-Za-z]+)')
    return [s.lower() for s in re.findall(words, line)]


def ngram_key(ngram):
    """Generate a unique strnig from a given ngram, a vector of strings"""
    return "+".join(ngram)

def ngram_generator(filename, n=1):
    """Generates successive n-grams from filename

    Parameters:
      filename -- a string representing a readable file
      n        -- the order of n-grams to compute

    Yields successive n-grams (n-gram keys) from the file. The file is
    tokenized and n successive words combined to an ngram key, with the
    window shifting each time by 1 word.

    For example, a string 'all good folks know' has ngrams for n=2
    'all+good', 'good+folks', and 'folks+know'; for n=1, each word is an
    n-gram. This function reads text from the connection, tokenizes it,
    and computes ngram frequencies.

    """
    with open(filename, "r") as f:
        token_number = 0
        tokens = []
        for line in f:
            tokens.extend(tokenize(line))

            while len(tokens) >= token_number + n:
                index = token_number
                token_number += 1
                yield ngram_key(tokens[index:(index+n)])


def ngram_frequency(filename, n=1):
    """
    Generates frequency distribution of ngrams from a given text source

    Parameters:
      filename -- a string representing a readable file
      n        -- the order of n-grams to compute (defaults to single words)

    Returns a dictionary mapping ngrams in the text to the number of
    times the ngram appears.
    """
    ngram_counts = dict_with_attributes(int)
    total = 0

    ATTN:FILLINHERE

    ngram_counts.total = total
    ngram_counts.order = n
    return ngram_counts

def ngram_intersection(ngram_counts1, ngram_counts2):
    """
    Finds the n-grams common to two text sources

    Parameters ngram_counts1 and ngram_counts2 are dictionaries
    as returned by ngram_frequency.

    Returns a list of ngram keys for ngrams common to the
    two text sources.
    """
    ngrams12 = dict_with_attributes(int)
    if ngram_counts1.order != ngram_counts2.order:
        return []

    for ngram, count in ngram_counts1.items():
        if ngram in ngram_counts2:
            ngrams12[ngram] = min(count, ngram_counts2[ngram])

    return ngrams12.keys()
    
    
