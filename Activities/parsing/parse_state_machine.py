#
# A DSL for specifying state machines.
# Actions accept arbitrary delimited text, which could be code
# or prompts for an LLM or anything.
#
# States, transitions, and actions can be given in any order
# and can be checked for validity once collected. To this end,
# line information is maintained for each object.
#
# Example
#     state a
#     state b
#
#     transition one from c to a
#     transition two from a, b to c
#     transition three from b to c, d
#     transition six from b to d or from d to e
#
#     delegate input to one
#
#     action on enter a
#       | ... arbitrary lines
#       | ...
#     end
#
#     action during two with event, source, target
#       | ...
#       | ...
#     end
#
# Only action blocks span more than one line and these have the
# delimited form shown above. The components of a transition are
# cartesian products like 'a to b, c' where the comma-separated list
# can occur on both sides of the 'to'. This names a group of
# transitions which are treated similarly.
#
# All names are taken to be identifiers starting with a letter,
# see the parser 'name' below.
#
# EXERCISE. Comments are useful for specifications like this.
# Add support for comments in the text, e.g., everything
# on a line after a '#' or a '--' or a '//' or whatever is
# ignored. If you are ambitious, you can have special structured
# metadata in comments at the beginning of a file that is parsed
# and stored in the data representation, e.g., owner, date, version,
# or whatever.
#
# EXERCISE. Support wildcards in transitions. For instance,
# from b to * could mean from b to every other state, or
# you could even match patterns like from b to over* to transtion
# to every state whose name starts with over.
#

import enum as E   # enum is a combinator

from dataclasses import dataclass

from combinators import (Parser, ParseResult, Success, parse, failed, do, fmap,
                         seq, follows, between, interleave,
                         alts, optional, many,
                         space, hspace, newline,
                         char, symbol, istring, strings, sjoin, regex)


#
# Data representation of state-machine components.
#
# The components will be stored in a dictionary with lists of
# component types: states, transitions and delegates, and actions.

@dataclass
class State:
    name: str

@dataclass
class Transition:
    name: str
    edges: list[tuple[State, State]]

@dataclass
class Delegated:
    name: str
    delegate: Transition | str

class ActionType(E.StrEnum):
    ENTER_STATE = "EnterState"
    EXIT_STATE = "ExitState"
    BEFORE_TRANS = "BeforeTransition"
    DURING_TRANS = "DuringTransition"
    AFTER_TRANS = "AfterTransition"

def action_type(atype: str) -> ActionType:
    match atype:
        case 'on enter':
            return ActionType.ENTER_STATE
        case 'on exit':
            return ActionType.EXIT_STATE
        case 'before':
            return ActionType.BEFORE_TRANS
        case 'during':
            return ActionType.DURING_TRANS
        case 'after':
            return ActionType.AFTER_TRANS
        case _:
            raise ValueError(f'Unrecognized action type {atype}')

@dataclass
class Action:
    action_type: ActionType
    target: State | Transition | str
    code: str
    param_names: tuple[str, str, str] | None = None

@dataclass
class StateMachine:
    """A data representation of a state machine specification. This is NOT the machine itself.

    In this simple version, states that are referenced are automatically created.
    Transitions referenced in actions or delegated statements are pending and handled
    during clean. See Exercise below.

    EXERCISE. Consider this design choice. If you think you have a better choice, sketch
    out a policy and perhaps an implementation that executes your choice.

    """
    states: dict[str, State]
    transitions: dict[str, Transition]
    delegated: list[Delegated]
    actions: list[Action]
    pending_transitions: dict[str, Transition]

    @classmethod
    def make(cls):
        "Creates a fresh structure to record state machine spec data"
        return cls({}, {}, [], [], {})

    def add_state(self, state: str):
        "Adds a confirmed state to the store."
        if state not in self.states:
            self.states[state] = State(state)
        return self

        # This is how we would handle states if they were not implicitly defined
        # See the EXERCISE below for considering alternatives.
        # if state in self.states:
        #     return self.states[state]
        # if state in self.pending_states:
        #     self.states[state] = self.pending_states[state]
        #     del self.pending_states[state]
        # else:
        #     self.states[state] = State(state)
        # return self.states[state]

    def ref_state(self, state: str) -> State:
        "Handles a reference to a state that may or may not be defined."
        if state not in self.states:
            self.states[state] = State(state)
        return self.states[state]

        # This is how we would handle states if they were not implicitly defined
        # See the EXERCISE below for considering alternatives.
        # if state in self.states:
        #     return self.states[state]
        # if state not in self.pending_states:
        #     self.pending_states[state] = State(state)
        # return self.pending_states[state]

    def add_transitions(self, name: str, edges: list[tuple[list[str], list[str]]]):
        "Adds confirmed transitions to the store with name, source, and target."
        if name in self.transitions:
            return self
        if name in self.pending_transitions:
            self.transitions[name] = self.pending_transitions[name]
            del self.pending_transitions[name]
            return self

        transitions = []
        for edge in edges:
            sources, targets = edge
            for source in sources:
                src = self.ref_state(source)
                for target in targets:
                    tgt = self.ref_state(target)
                    transitions.append((src, tgt))
        self.transitions[name] = Transition(name, transitions)
        return self

    def add_delegate(self, delegate: str, trans: str):
        """Add a delegate.

        Note delegated transitions are not pending and will be checked at
        the end since we don't have source and target.

        """
        self.delegated.append(Delegated(delegate, trans))  # Correct at end
        return self

    def add_action(self, atype: ActionType, target: str, code: str, params=None):
        if atype == ActionType.ENTER_STATE or atype == ActionType.EXIT_STATE:
            self.actions.append(Action(atype, self.ref_state(target), code))
            return self

        self.actions.append(Action(atype, target, code, params))
        return self

    # EXERCISE. The clean method needs to be called when the file is done
    # processing, but that requirement is not enforced and a source of bugs.
    # Implement a context handler with state_machine() as sm: ...
    # that will both make a fresh instance and clean it allowing the machine
    # to be processed and cleaned automatically.

    def clean(self):
        """Cleans up/checks transitions in delegates and actions and pending states/transitions.

        For the moment, raises an error if a transition is undefined. If a state is undefined,
        it is defined implicitly as it has no data other than its name.
        EXERCISE. Find a good alternative way of handling this case.
        """
        for delegated in self.delegated:
            if isinstance(delegated.delegate, str):
                if delegated.delegate in self.transitions:
                    delegated.delegate = self.transitions[delegated.delegate]
                else:
                    raise KeyError(f'Undefined transition {delegated.delegate} in delegate')
        for action in self.actions:
            if isinstance(action.target, str):
                if action.target in self.transitions:
                    action.target = self.transitions[action.target]
                else:
                    raise KeyError(f'Undefined transition {action.target} in action')

        if len(self.pending_transitions) > 0:
            raise KeyError(f'Undefined transitions: {", ".join(self.pending_transitions.keys())}')

        return self


#
# State-Machine Parser Components
#

space0 = optional(space, "")
hspace0 = optional(hspace, "")
end_line = sjoin(hspace0, newline)  # type: ignore
lexeme = lambda s: symbol(s.lower(), hspace, str.lower)
name = regex(r'[A-Za-z_][-A-Za-z_0-9?!]*')
names = interleave(name, sjoin(hspace0, char(','), hspace0))  # type: ignore
link = seq(between(lexeme('from'), names, hspace), follows(lexeme('to'), names))
links = interleave(link, sjoin(hspace, istring('or'), hspace))
code_line = follows(sjoin(hspace0, char('|')), sjoin(regex('.*'), newline))  # type: ignore

def state(sm: StateMachine) -> Parser[StateMachine]:
    return fmap( between(lexeme('state'), name, end_line), lambda s: sm.add_state(s) )

def transition(sm: StateMachine) -> Parser[StateMachine]:
    @do
    def transition_spec():
        yield lexeme('transition')
        trans = yield name
        yield hspace
        edges = yield links
        yield end_line

        sm.add_transitions(trans, edges)
        return sm
    return transition_spec

def delegated(sm: StateMachine) -> Parser[StateMachine]:
    @do
    def delegate():
        yield lexeme('delegate')
        d = yield name
        yield hspace
        yield lexeme('to')
        target = yield name
        yield end_line
        sm.add_delegate(d, target)
        return sm
    return delegate

def action(sm: StateMachine) -> Parser[StateMachine]:
    @do
    def actionP():
        yield lexeme('action')
        atype = yield fmap( strings('on enter', 'on exit', 'before', 'during', 'after'),
                            action_type )
        yield hspace
        target = yield name
        # ATTN: The params could be made more precise
        params = yield optional(interleave(name, regex(r', *'),
                                           start=seq(hspace, lexeme('with'))))
        yield end_line
        code = yield fmap( many(code_line), lambda lines: "".join(lines) )
        yield sjoin(hspace0, istring('end'), end_line)

        sm.add_action(atype, target, code, params)
        return sm
    return actionP

def state_machine(sm: StateMachine) -> Parser[list[StateMachine]]:
    def choices(*p):
        return interleave(alts(*p), space0)

    return choices(
        state(sm),
        transition(sm),
        delegated(sm),
        action(sm)
    )


#
# Main State-Machine Parser
#

# EXERCISE. When there are errors, it would be helpful to keep track
# of the line number of the block (or line) that contains the error.
# Adjust the implementation to handle this.

def parse_state_machine(spec: str) -> StateMachine:
    """Parses a string encoding a state machine specification and returns the spec data.

    Raises an error if parsing fails.

    """
    machine_data = StateMachine.make()  # Note: This is mutable
    parsed: ParseResult[list[StateMachine]] = parse(spec, state_machine(machine_data))
    if failed(parsed):
        raise ValueError(f'State machineparsing failed at position {parsed.pos}: {parsed.message}')
    assert isinstance(parsed, Success)
    sm = machine_data.clean()
    return sm


# EXERCISE. This parser uses a mutable machine that is modified at each step.
# (Technically, this makes the pieces something other than combinators as they
# depend on that mutating external state.)
# Consider this design decision. Is there an easy way to alter that approach?
# Is it worthwhile? Try it.
