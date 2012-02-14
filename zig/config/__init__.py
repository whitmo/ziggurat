from .config import ConfigMap
from .config import SectionMap
from .resource import resource_spec
from .resolver import DottedNameResolver

resolve = DottedNameResolver(None).maybe_resolve

