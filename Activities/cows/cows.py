import sys

from folds         import make_fold
from bounded_queue import BoundedQueue
from state_machine import State, StateMachine

class BreedState(StateMachine):
    viable = State('viable')
    pending = State('pending')
    crowded = State('crowded')

    in_window = viable >> pending | pending >> crowded
    out_window = pending >> viable

    def on_enter_crowded(self):
        id = self.acc.get('largest_id', -1)
        if self.breed > id:
            self.acc['largest_id'] = self.breed

    def __init__(self, breed, acc={'largest_id': -1}):
        super().__init__(name=breed)
        self.breed = breed
        self.acc = acc

def update(state, breed):
    "Updates and returns (mutated) `state` for having seen `breed`."
    biggest_so_far = state['largest_id']
    if breed > biggest_so_far and breed not in state['seen']:
        state['seen'][breed] = BreedState(breed, state)
    leaving = state['window'].enqueue(breed)
    # We abandon irrelevant states here, with no cost
    if leaving is not None and leaving > biggest_so_far:
        state['seen'][leaving].dispatch({'type': 'out_window'})
    # in_window must follow out_window in case breed == leaving
    if breed > biggest_so_far:
        state['seen'][breed].dispatch({'type': 'in_window'})
    return state

cow_fold = make_fold(update, finish=lambda state: state['largest_id'])


def crowded_cows(breed_ids, K):
    the_state = {
        'largest_id': -1,
        'window': BoundedQueue(K + 1),
        'seen': {}
    }
    return cow_fold.fold(breed_ids, the_state)


#
# Simple driver
#

def breeds_from_file(filename):
    with open(filename) as f:
        breeds = list(map(int, f.read().splitlines()))
    return breeds

def main(filename, threshold):
    breeds = breeds_from_file(filename)
    ans = crowded_cows(breeds, threshold)
    print(f'Largest crowded breed: {ans if ans >= 0 else "none"}')

if __name__ == '__main__':
    n = len(sys.argv)
    if n < 2:
        raise ValueError('Data filename required')
    filename = sys.argv[1]
    K = int(sys.argv[2]) if n >= 3 else 1
    main(filename, K)
