from __future__ import annotations
from enum import Enum
from typing import List, Dict, Tuple
import re


class Color(Enum):
    RED = (0, "\033[91m")
    GREEN = (1, "\033[92m")

    def __init__(self, identifier: int, ansi_escape_code: str) -> None:
        self.id = identifier
        self.ansi_escape_code = ansi_escape_code


def colored_print(text: str, color: Color) -> None:
    CEND = "\033[0m"
    print(color.ansi_escape_code + text + CEND)


class DFAStatus(Enum):
    UNKNOWN_SYMBOL_ERROR = (0, "There is a symbol in the transmitted string that is not in the alphabet")
    NO_TRANSITIONS = (1, "There are no transitions from the current state")
    NOT_REACHED_FINAL_STATE = (2, "The final states has not been reached")
    REACHED_FINAL_STATE = (3, "The final state has been reached")

    def __init__(self, identifier: int, message) -> None:
        self.id = identifier
        self.message = message


def uniqueness(container):
    """
    Checks if the container is unique.

    In case of uniqueness it returns True
    """
    return len(container) == len(list(set(container)))


class DFA:
    """
    A class that is a deterministic finite state machine
    """
    __transition_function: Dict[Tuple[str, str], str]

    def __init__(self, states: List[str], alphabet: List[str], transition_table: str,
                 start_state: str, accepted_states: List[str]) -> None:

        DFA.data_valid(states, alphabet, start_state, accepted_states)

        self.__states = states
        self.__alphabet = alphabet
        self.__start_state = start_state
        self.__accepted_states = accepted_states
        self.__current_state = None
        self.__transition_function = self.__make_transition_function(transition_table)

    @property
    def states(self) -> List[str]:
        return self.__states

    @property
    def alphabet(self) -> List[str]:
        return self.__alphabet

    @property
    def transition_function(self) -> Dict[Tuple[str, str], str]:
        return self.__transition_function

    @property
    def start_state(self) -> str:
        return self.__start_state

    @property
    def current_state(self) -> str:
        return self.__current_state

    @property
    def accepted_states(self) -> List[str]:
        return self.__accepted_states

    def __transition_valid(self, state: str, symbol: str, next_state: str) -> None:
        """
        Checking the transition to permissibility
        """
        if state not in self.states:
            raise ValueError(f"Transmitted a non-existent state: {state}!")

        if next_state not in self.states:
            raise ValueError(f"Transmitted a non-existent state {next_state}!")

        if symbol not in self.alphabet:
            raise ValueError(f"A character ({symbol}) that is not in the alphabet is passed on!")

    def __add_transition(self, tf: Dict[Tuple[str, str], str], transition: str) -> None:
        """
        Adds a transition to the transition function if it matches

        the set format and parameters of the finite automaton
        """
        if not re.findall(r"\w*-\w*-\w*", transition):
            raise ValueError(f"The transition: {transition} is in an incorrect format!")

        state, symbol, next_state = transition.split("-")

        self.__transition_valid(state, symbol, next_state)

        maybe_next_state = tf.get((state, symbol))

        if maybe_next_state is None:
            tf[(state, symbol)] = next_state
            return
        if maybe_next_state == next_state:
            raise Warning(f"Transition <{transition}> is defined twice")

        raise ValueError(f"Transition <{state}-{symbol}> is defined " +
                         f"twice with different end states ({maybe_next_state} != {next_state})!")

    def __make_transition_function(self, transition_table: str) -> Dict[Tuple[str, str], str]:
        """
        Making a transition function from a string of a set format:

        state-symbol-next_state,state2-symbol2-next_state2,...,stateN-symbolN-next_stateN
        """
        tf = dict()
        transitions = transition_table.split(",")

        if len(transitions) == 0:
            raise ValueError("Not a single transition has been transmitted!")

        [self.__add_transition(tf, transition) for transition in transitions]

        return tf

    def __transition(self, symbol: str) -> DFAStatus:
        """
        Switching to a new state by the symbol
        """
        if symbol not in self.alphabet:
            return DFAStatus.UNKNOWN_SYMBOL_ERROR

        self.__current_state = self.transition_function.get((self.current_state, symbol), None)

        if self.current_state is None:
            return DFAStatus.NO_TRANSITIONS

        if self.current_state not in self.accepted_states:
            return DFAStatus.NOT_REACHED_FINAL_STATE

        return DFAStatus.REACHED_FINAL_STATE

    def check_ownership(self, string) -> bool:
        """
        String affiliation check
        """
        self.__current_state = self.start_state
        status = DFAStatus.REACHED_FINAL_STATE if self.start_state in self.accepted_states \
            else DFAStatus.NOT_REACHED_FINAL_STATE
        for symbol in string:
            status = self.__transition(symbol)
            if status in [DFAStatus.UNKNOWN_SYMBOL_ERROR, DFAStatus.NO_TRANSITIONS]:
                break

        if status != DFAStatus.REACHED_FINAL_STATE:
            colored_print("Rejected", Color.RED)
            return False

        colored_print("Accepted", Color.GREEN)
        return True

    def get_string_representation_of_tf(self) -> str:
        return "  ".join([f"{key}->{value}" for key, value in self.transition_function.items()])

    def __repr__(self):
        return f"states: {self.states}\n" \
               f"alphabet: {self.alphabet}\n" \
               f"start state: {self.start_state}\n" \
               f"accepted states: {self.accepted_states}\n" \
               f"transition function: {self.get_string_representation_of_tf()}"

    @staticmethod
    def data_valid(states: List[str], alphabet: List[str], start_state: str, accepted_states: List[str]) -> None:
        """
        Checking states, alphabet, final states for uniqueness,
        initial state and final states for consistency with states
        """
        if not uniqueness(alphabet):
            raise ValueError("Some of symbols is defined twice, but the alphabet must be unique!")
        if not uniqueness(states):
            raise ValueError("Some of states is defined twice, but they must be unique!")
        if not uniqueness(accepted_states):
            raise Warning("Final states are not unique.")
        if start_state not in states:
            raise ValueError(f"Start state ({start_state}) does not correspond "
                             f"to any of the possible states: {states}!")
        for s in accepted_states:
            if s not in states:
                raise ValueError(f"Final state ({s}) does not correspond to any of the possible states: {states}!")
