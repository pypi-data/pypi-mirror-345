import aniclustermap.logger as _logger
import aniclustermap.utils as _utils
from aniclustermap.main import AniClustermap

__version__ = "2.0.0"
__all__ = ["AniClustermap"]

_logger.init_null_logger()
_utils.add_bin_path()
