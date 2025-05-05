import os
import uuid
from typing import Literal
from typing import Optional

import streamlit.components.v1 as components

RAW = os.getenv('ST_COPY_DEV_SERVER')
DEV_URL = (RAW or '').strip()

if DEV_URL:
    if DEV_URL.lower() in {'auto', 'default'}:
        DEV_URL = 'http://localhost:3001'
    component = components.declare_component(
        'st_copy',
        url=DEV_URL
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(parent_dir, 'frontend', 'dist')
    component = components.declare_component(
        'st_copy',
        path=frontend_dir
    )


def copy_button(
    text: str,
    *,
    icon: Literal['material_symbols', 'st'] = 'material_symbols',
    tooltip: str = 'Copy',
    copied_label: str = 'Copied!',
    key: Optional[str] = None,
) -> Optional[bool]:
    """
    Render a copy‑to‑clipboard button.

    Parameters:
        text : str
            The text that will be placed on the user’s clipboard.

        icon : {'material_symbols', 'st'}, default 'material_symbols'
            Which icon to show:

            * 'material_symbols' – Google Material content_copy glyph
            * 'st' – the native Streamlit code‑block icon

        tooltip : str, default 'Copy'
            Tooltip shown on hover / focus.

        copied_label : str, default 'Copied!'
            Small text that appears next to the icon for ~1 second after a
            successful copy operation.

        key : str | None, optional
            Streamlit component key.  If None, a random
            `uuid.uuid4()` string is generated.

    Returns:
        bool | None
            * `True` – text copied successfully.
            * `False` – browser blocked the Clipboard API.
            * `None`  – the button has not been clicked yet.
    """
    if key is None:
        key = str(uuid.uuid4())

    return component(
        text=text,
        icon=icon,
        tooltip=tooltip,
        copied_label=copied_label,
        key=key,
    )
