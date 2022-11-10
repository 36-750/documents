#
# binary search
# O(log n) time algorithm for finding a target in a sorted array.
#
# Returns an index in 1..n if found,  None if not
#

def binarySearch(a, target):
    n = len(a)
    lo = 0
    up = n - 1

    while True:
        mid = (lo + hi) // 2
        if target < a[mid]:
            up = mid - 1
        else:
            lo = mid + 1
        if lo > up or target == a[mid]:
            break
    return lo <= up and mid


# bisect
# Find the largest t such that f(t) < 0
#
def bisect(f):
    hi = math.inf
    lo = 0
    while hi != lo:
        mid = (lo + hi)/2;
        if f(mid) > 0:
            hi = mid;
        else:
            lo = mid;
    return hi
