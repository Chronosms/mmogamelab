from mg import *
import re

default_location_delay = 20
re_param_attr = re.compile(r'^p_(.+)')

class DBLocation(CassandraObject):
    _indexes = {
        "all": [[], "name"],
        "name": [["name"]],
    }

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "Location-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBLocation._indexes

class DBLocationList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "Location-"
        kwargs["cls"] = DBLocation
        CassandraObjectList.__init__(self, *args, **kwargs)

class DBCharacterLocation(CassandraObject):
    _indexes = {
        "location": [["location"]],
        "instance": [["instance"]],
    }

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "CharacterLocation-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBCharacterLocation._indexes

class DBCharacterLocationList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "CharacterLocation-"
        kwargs["cls"] = DBCharacterLocation
        CassandraObjectList.__init__(self, *args, **kwargs)

class DBLocParams(CassandraObject):
    _indexes = {}

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "LocParams-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBLocParams._indexes

class DBLocParamsList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "LocParams-"
        kwargs["cls"] = DBLocParams
        CassandraObjectList.__init__(self, *args, **kwargs)

class Location(Module):
    def __init__(self, app, uuid, fqn="mg.mmorpg.locations.Location"):
        Module.__init__(self, app, fqn)
        self.uuid = uuid

    @property
    def db_location(self):
        try:
            return self._db_location
        except AttributeError:
            self._db_location = self.obj(DBLocation, self.uuid)
            return self._db_location

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            self._name = self.db_location.get("name")
            return self._name

    @property
    def name_g(self):
        try:
            return self._name_g
        except AttributeError:
            self._name_g = self.db_location.get("name_g") or self.db_location.get("name")
            return self._name_g

    @property
    def name_a(self):
        try:
            return self._name_a
        except AttributeError:
            self._name_a = self.db_location.get("name_a") or self.db_location.get("name")
            return self._name_a

    @property
    def name_w(self):
        try:
            return self._name_w
        except AttributeError:
            self._name_w = self.db_location.get("name_w") or self.db_location.get("name")
            return self._name_w

    @property
    def name_f(self):
        try:
            return self._name_f
        except AttributeError:
            self._name_f = self.db_location.get("name_f") or self.db_location.get("name")
            return self._name_f

    @property
    def name_t(self):
        try:
            return self._name_t
        except AttributeError:
            self._name_t = self.db_location.get("name_t") or self.db_location.get("name")
            return self._name_t

    def valid(self):
        try:
            db = self.db_location
        except ObjectNotFoundException:
            return False
        else:
            return True

    @property
    def image_type(self):
        try:
            return self._image_type
        except AttributeError:
            self._image_type = self.db_location.get("image_type")
            return self._image_type

    @property
    def transitions(self):
        try:
            return self._transitions
        except AttributeError:
            self._transitions = self.db_location.get("transitions")
            return self._transitions

    @property
    def delay(self):
        try:
            return self._delay
        except AttributeError:
            self._delay = self.db_location.get("delay", default_location_delay)
            return self._delay

    def script_attr(self, attr, handle_exceptions=True):
        if attr == "id":
            return self.uuid
        elif attr == "name":
            return self.name
        elif attr == "name_g":
            return self.name_g
        elif attr == "name_a":
            return self.name_a
        elif attr == "name_f":
            return self.name_f
        elif attr == "name_t":
            return self.name_t
        elif attr == "name_w":
            return self.name_w
        else:
            m = re_param_attr.match(attr)
            if m:
                param = m.group(1)
                return self.param(param, handle_exceptions)
            else:
                raise AttributeError(attr)

    @property
    def db_params(self):
        try:
            return self._db_params
        except AttributeError:
            self._db_params = self.obj(DBLocParams, self.uuid, silent=True)
            return self._db_params

    def param(self, key, handle_exceptions=True):
        try:
            cache = self._param_cache
        except AttributeError:
            cache = {}
            self._param_cache = cache
        try:
            return cache[key]
        except KeyError:
            # 'param-value' handles cache storing automatically
            return self.call("locations.param-value", self, key, handle_exceptions)

    def script_params(self):
        return {"loc": self}
