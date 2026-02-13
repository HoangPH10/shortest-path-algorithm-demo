"""Input form component for route visualization application.

This module provides the user interface for entering start and destination addresses.
"""

from typing import Tuple

import streamlit as st


def render_input_form() -> Tuple[str, str, bool]:
    """Render the input form for start and destination addresses.

    Returns:
        A tuple containing:
        - start_address: Starting location address string
        - dest_address: Destination location address string
        - calculate_clicked: Boolean indicating if Calculate button was clicked

    Example:
        >>> start, dest, clicked = render_input_form()
        >>> if clicked:
        ...     # Process the addresses
        ...     pass
    """
    # Input fields for addresses
    start_address = st.text_input(
        "Starting Location",
        placeholder="e.g., Times Square, New York",
        key="start_address",
    )

    dest_address = st.text_input(
        "Destination",
        placeholder="e.g., Central Park, New York",
        key="dest_address",
    )

    # Disable button if either input is empty
    button_disabled = not start_address.strip() or not dest_address.strip()

    # Calculate button
    calculate_clicked = st.button(
        "🚀 Calculate Routes",
        disabled=button_disabled,
        type="primary",
        use_container_width=True,
    )

    return start_address.strip(), dest_address.strip(), calculate_clicked
