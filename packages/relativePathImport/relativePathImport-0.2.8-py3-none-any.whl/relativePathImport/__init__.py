
from .relativePathImport import relativePathImport
import sys
sys.modules[__name__] = relativePathImport