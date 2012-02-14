from .resource import resource_spec
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
from UserDict import DictMixin
from paste.deploy.loadwsgi import NicerConfigParser as ConfigParser
import codecs


class SectionMap(DictMixin):
    """
    A maplike object that wraps a section of a config parser
    """

    cfp_klass = ConfigParser

    def __init__(self, cp, section, **kw):
        if not cp.has_section(section):
            raise NoSectionError("%s does not exist in %s" %(section, cp))
        self.cp = cp
        self.vars = kw
        self.section = section

    @property
    def section_items(self):
        return self.cp.items(self.section, vars=self.vars)
    
    def __getitem__(self, key):
        try:
            return self.cp.get(self.section, key, vars=self.vars)
        except NoOptionError:
            raise KeyError(key)

    def __delitem__(self, key):
        self.cp.remove_option(self.section, key)

    def __setitem__(self, key, value):
        self.cp.set(self.section, key, value)

    def keys(self):
        return dict(self.section_items).keys()

    @classmethod
    def from_file(cls, fp, name):
        cp = cls.cfp_klass()
        cp.read(fp)
        return cls(cp, name)

    def write_out(self, fp):
        self.cp.write(fp)



class ConfigMap(DictMixin):
    """
    a readonly mapping wrapper for a configparser object
    """
    klass = ConfigParser
    section_map_klass = SectionMap
    
    def __init__(self, cp, **kw):
        self.cp = cp
        self.vars = kw

    def keys(self):
        return self.cp.sections()

    def __getitem__(self, key):
        return self.section_map_klass(self.cp, key, **self.vars)

    def __setitem__(self, key, value):
        raise NotImplemented

    def __delitem__(self, key, value):
        raise NotImplemented

    @classmethod
    def from_file(cls, fp, **kw):
        cp = cls.klass(fp)
        cp.read(fp)
        return cls(cp, **kw)

    @classmethod
    def from_spec(cls, spec, **kw):
        fp = resource_spec(spec)
        return cls.from_file(fp, **kw)
    
    @classmethod
    def from_spec_force_utf8(cls, spec, **kw):
        cp = ConfigParser()
        cp.readfp(codecs.open(resource_spec(spec), "r", "utf8"))
        return cls(cp, **kw)


