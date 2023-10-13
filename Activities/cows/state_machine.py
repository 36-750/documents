# A Quick StateMachine Implementation
#
# Example use:
#     class Foo(StateMachine):
#         a = State('a')
#         b = State('b')
#         c = State('c')
#
#         one = c >> a
#         two = a >> b | c >> b
#         six = b >> c
#
#         input = DelegateTo(one)
#
#         def on_enter_a(self):
#             print('Entering a')
#
#         def on_exit_a(self):
#             print('Exiting a')
#
#         def on_enter_b(self):
#             print('Entering b')
#
#         def on_exit_b(self):
#             print('Exiting b')
#
#         def during_six(self, event, source, target):
#             print(f'Transition {event["type"]} from {source} to {target}')
#
#     sm = Foo()
#     print(str(sm))
#
#     sm.dispatch({'type': 'two'})
#     print(sm.state)
#     sm.dispatch({'type': 'six'})

from __future__ import annotations

import re

from typing import Callable

#
# Helper classes for gathering machine specification
#

class DelegateTo:
    "Event translations"
    def __init__(self, local_event):
        self.target = local_event

class TransitionPairs:
    "Marker class for collecting transitions"
    def __init__(
            self,
            transitions: tuple['State', 'State | Callable'] | list[tuple['State', 'State | Callable']]
    ) -> None:
        if isinstance(transitions, list):
            self._edges = transitions
        else:
            self._edges = [transitions]

    def __or__(self, other):
        if isinstance(other, TransitionPairs):
            my_edges = self._edges[:]
            my_edges.extend(other._edges)
            return TransitionPairs(my_edges)
        return NotImplemented

class State:
    def __init__(self, name, *args):
        self._name = name

        if len(args) == 0:
            self.data = None
        elif len(args) == 1:
            self.data = args[0]
        else:
            self.data = args

    @property
    def name(self):
        return self._name

    def __rshift__(self, other):
        if isinstance(other, State) or callable(other):
            return TransitionPairs((self, other))

    def to(self, state: State | Callable):
        return TransitionPairs((self, state))

    def __str__(self):
        return str(self._name)

#
# Metaclass Processor
#

class StateConfig(type):
    def __new__(self, name, bases, namespace, **kwds):
        _states = []
        _transitions = {}
        _actions = {}      # Includes actions and guards
        remove = []
        for attr, value in namespace.items():
            if isinstance(value, State):
                _states.append(str(value))
                remove.append(attr)
            elif isinstance(value, TransitionPairs):
                trans = _transitions[attr] = {}
                for edge in value._edges:
                    state_from, state_to = edge
                    trans[state_from.name] = state_to if callable(state_to) else state_to.name 
                    remove.append(attr)
            elif isinstance(value, DelegateTo):
                if isinstance(value.target, str):
                    _transitions[attr] = value.target
                else:
                    for rm in remove:
                        if namespace[rm] == value.target:
                            _transitions[attr] = rm
                    remove.append(attr)
                remove.append(attr)
            elif callable(value) and not isinstance(value, staticmethod) and not isinstance(value, classmethod):
                if m := re.match(r'on_(enter|exit)_(\S*)$', attr):
                    method = m[1]
                    state = m[2]
                    # ATTN: inspect methods arguments
                    if state in _actions:
                        _actions[state][method] = value
                    else:
                        _actions[state] = {method: value}
                elif m := re.match(r'(before|during|after|guard)_(\S*)$', attr):
                    method = m[1]
                    transition = m[2]
                    if transition in _actions:
                        _actions[transition][method] = value
                    else:
                        _actions[transition] = {method: value}
        # Clean up the class data fields
        for rm in set(remove):
            if rm in namespace:
                del namespace[rm]
        namespace['_states'] = _states
        namespace['_transitions'] = _transitions
        namespace['_actions'] = _actions
        return super(StateConfig, self).__new__(self, name, bases, namespace)


#
# The StateMachine Base Class
#

class StateMachine(metaclass=StateConfig):
    "Base class for all state machines."
    def __init__(self, *, name='anonymous', initial=None):
        if not self._states:
            raise ValueError(f'State machine {name} is stateless.')
        if initial is None:
            self._state = self._states[0]
        elif initial in self._states:
            self._state = initial
        else:
            raise KeyError(f'Cannot find initial state for State Machine {name}')

        self._name = name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state not in self._states:
            raise ValueError(f'Unrecognized state {new_state} for StateMachine {self._name}.')
        self._state = new_state

    @property
    def states(self):
        return tuple(*self._states)

    @property
    def listens_for(self):
        return tuple(self._transitions.keys())

    @property
    def name(self):
        return self._name

    def delegate_to(self, new_event, my_event):
        if my_event not in self._transitions:
            raise KeyError(f'Unrecognized event {my_event} cannot be delegated to')
        if not isinstance(new_event, str):
            raise ValueError(f'Delegated event should be a string, got {new_event}')
        self._transitions[new_event] = my_event

    def show_states(self, print_it=True):
        out = "States: " + ", ".join(self._states)
        if print_it:
            print(out)
        return out

    def show_transitions(self, print_it=True):
        out = []
        for k, v in self._transitions.items():
            if isinstance(v, str):
                out.append(f'{k} => {v}')
            else:
                out.append(k + ':')
                for s_from, s_to in v.items():
                    out.append(f'  {s_from} -> {s_to}')
        out_s = "\n".join(out)
        if print_it:
            print(out_s)
        return out_s

    def __str__(self):
        return self.show_states(False) + "\n" + self.show_transitions(False)

    def dispatch(self, event):
        e_type = event['type']
        if e_type in self._transitions:
            trans = self._transitions[e_type]
            if isinstance(trans, str):  # Delegated
                if trans in self._transitions:
                    e_type = trans
                    trans = self._transitions[trans]  # Only delegate once
                else:
                    return None
            source = self.state
            if source not in trans:
                return None
            e_actions = self._actions[e_type] if e_type in self._actions else {}
            s_actions = self._actions[source] if source in self._actions else {}

            if 'guard' in e_actions and not e_actions['guard'](event):
                return None
            target = trans[source]
            if callable(target):
                target = target(self, source, event)
            t_actions = self._actions[target] if target in self._actions else {}

            if 'before' in e_actions:
                e_actions['before'](self, event, source, target)

            if 'exit' in s_actions:
                s_actions['exit'](self)

            if 'during' in e_actions:
                e_actions['during'](self, event, source, target)

            if 'enter' in t_actions:
                t_actions['enter'](self)

            if 'after' in e_actions:
                e_actions['after'](self, event, source, target)

            self.state = target
            return target
        return None
