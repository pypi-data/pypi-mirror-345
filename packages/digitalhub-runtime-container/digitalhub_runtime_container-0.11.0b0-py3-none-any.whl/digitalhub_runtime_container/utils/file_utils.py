from __future__ import annotations

from digitalhub.utils.file_utils import get_file_mime_type


def eval_readable_text(source: str) -> bool:
    """
    Evaluate readable type.

    Parameters
    ----------
    source : str
        Source.

    Returns
    -------
    bool
        True if path is readable as text.
    """
    return get_file_mime_type(source) in [
        "text/plain",
        "text/x-python",
        "text/x-shellscript",
    ]
