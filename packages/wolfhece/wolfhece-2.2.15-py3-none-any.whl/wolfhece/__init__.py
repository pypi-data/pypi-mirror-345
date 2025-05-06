from . import _add_path
from .PyTranslate import _

try:
    from osgeo import gdal, osr, ogr
    gdal.UseExceptions()
    ogr.UseExceptions()
    osr.UseExceptions()
except ImportError as e:
    print(e)
    raise Exception(_('Error importing GDAL library\nPlease ensure GDAL is installed and the Python bindings are available\n\ngdal wheels can be found at https://github.com/cgohlke/geospatial-wheels'))

from .apps.version import WolfVersion

__version__ = WolfVersion().get_version()