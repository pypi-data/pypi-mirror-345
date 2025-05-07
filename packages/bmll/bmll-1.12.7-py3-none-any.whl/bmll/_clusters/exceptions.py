""" Exceptions that can be raised when working with _clusters.
"""

__all__ = (
    "InvalidArgumentError",
    "ClusterException",
    "InvalidDateTime",
)


from bmll.exceptions import BMLLError


class InvalidArgumentError(ValueError):
    """Return a given Exception if a parameter is not in the expected values."""

    def __init__(self, var, var_name, valid_options):
        super().__init__(self._get_msg(var, var_name, valid_options))

    @staticmethod
    def _get_msg(var, var_name, valid_options):
        valid_options = list(valid_options)

        if len(valid_options) <= 2:
            valid_option_str = " or ".join(f'"{nt}"' for nt in valid_options)
        else:
            valid_option_str = ", ".join(f'"{nt}"' for nt in valid_options[:-1])
            valid_option_str += f', or "{valid_options[-1]}"'

        msg = f'"{var_name}" must be {valid_option_str}, not "{var}".'

        return msg


class BaseBmllClusterError(BMLLError):
    """ Base class for all cluster-related errors.
    """


class ClusterException(BaseBmllClusterError):
    """ Raised when an error occurs when working with _clusters.
    """


class InvalidDateTime(BaseBmllClusterError):
    """ Raised when an error occurs when working with timestamps
    """
