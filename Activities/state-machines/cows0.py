from functools     import reduce
from bounded_queue import BoundedQueue
from state_machine import State, StateMachine

class BreedState(StateMachine):
    viable = State('viable')
    pending = State('pending')
    crowded = State('crowded')

    in_window = viable >> pending | pending >> crowded
    out_window = pending >> viable

    def on_enter_crowded(self):
        id = self.acc.get('largest_id', None)
        if id is None or self.breed > id:
            self.acc['largest_id'] = self.breed

    def __init__(self, breed, acc={'largest_id': None}):
        super().__init__(name=breed)
        self._breed = breed
        self.acc = acc

    @property
    def breed(self):
        return self._breed


def crowded_cows(breed_ids, K):
    the_state = {
        'largest_id': None,
        'window': BoundedQueue(K),
        'seen': {}
    }

    def update(state, breed):
        # This mutates state and assumes the ref is the same
        if breed not in state['seen']:
            state['seen'][breed] = BreedState(breed, state)
        leaving = state['window'].enqueue(breed)
        if leaving is not None:
            state['seen'][leaving].dispatch({'type': 'out_window'})
        state['seen'][breed].dispatch({'type': 'in_window'})
        return state

    return reduce(update, breed_ids, the_state)['largest_id']


def breeds_from_file(filename):
    with open(filename) as f:
        breeds = list(map(int, f.read().splitlines()))
    return breeds
