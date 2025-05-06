from collections.abc import Callable
from logging import getLogger
from typing import Generic, Literal, TypeVar

import streamlit as st

logger = getLogger(__name__)

T = TypeVar("T")
Stateful = TypeVar("Stateful")


class StateAttribute(Generic[T, Stateful]):
    """Descriptor which manages statefulness via st.session_state."""

    name: str
    owner_cls_name: str
    default: T | None
    default_factory: Callable[[], T] | None
    rerun: Literal["never", "on_change", "on_assignment"]
    """If the streamlit app should be rerun using `st.rerun`:
        "never": App should not be rerun.
        "on_change": Only when new value differs from old one.
        "on_assignment": On each assignment (also if it is the same value).
    """

    def __init__(
        self,
        default: T | None = None,
        default_factory: Callable[[], T] | None = None,
        rerun: Literal["never", "on_change", "on_assignment"] = "never",
    ) -> None:
        # TODO(David): Handle default=None (if the value should be initialized to None).
        self.default = default
        self.default_factory = default_factory
        self.rerun = rerun

    def __set_name__(self, owner: type[Stateful], name: str) -> None:
        """Set name and owner class name when the attribute is defined in the class."""
        self.name = name
        self.owner_cls_name = owner.__name__

    def get_key(self, instance: Stateful) -> str:
        """Return key which is used to get/set value in st.session_state."""
        instance_key = getattr(instance, "key", "")
        instance_sep = "." if instance_key else ""
        return f"{self.owner_cls_name}{instance_sep}{instance_key}.{self.name}"

    def __get__(self, instance: Stateful, owner: type[Stateful]) -> T:
        """Get the value either from the streamlit session state or initialize from default.

        Default factory is preferred over default.
        """
        key = self.get_key(instance)
        if key in st.session_state:
            return st.session_state[key]
        logger.info(f"Key {key} not in session state. Initializing from default...")
        value = (
            self.default_factory() if self.default_factory is not None else self.default
        )
        self.__set__(instance, value)
        return value

    def __set__(self, instance: Stateful, value: T) -> None:
        """Set the value in the streamlit session state (with logging)."""
        key = self.get_key(instance)
        logger.info(f"Setting: {key}={value!r}")
        prev_value = st.session_state.get(key)
        st.session_state[key] = value
        if self.rerun == "on_assignment" or (
            self.rerun == "on_change" and prev_value != value
        ):
            logger.info("Trigger rerun.")
            st.rerun()
