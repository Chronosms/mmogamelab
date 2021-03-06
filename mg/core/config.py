#!/usr/bin/python2.6

# This file is a part of Metagam project.
#
# Metagam is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# Metagam is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Metagam.  If not, see <http://www.gnu.org/licenses/>.

from mg.core.cass import CassandraObject, CassandraObjectList
import weakref
import re

re_config_path = re.compile(r'^(.+?)\.(.+)$')

class DBConfigGroup(CassandraObject):
    clsname = "ConfigGroup"
    indexes = {
        "all": [[]],
    }

class DBConfigGroupList(CassandraObjectList):
    objcls = DBConfigGroup

class ConfigError(Exception):
    "Error during config loading"
    pass

class Config(object):
    """
    This class is a config manager for the application. It keeps list of loaded
    config groups and can perform get operation on the configuration.
    """
    def __init__(self, app):
        self.app = weakref.ref(app)
        self.clear()

    def clear(self):
        self._config = {}
        self._modified = set()

    def _load_groups(self, groups):
        """
        Load requested config groups without lock
        groups - list of config group names
        """
        load_groups = [g for g in groups if g not in self._config]
        if load_groups:
            list = self.app().objlist(DBConfigGroupList, load_groups)
            list.load(silent=True)
            for g in list:
                self._config[g.uuid] = g.data
            for g in load_groups:
                if not g in self._config:
                    self._config[g] = {}

    def load_groups(self, groups):
        """
        Load requested config groups with lock
        groups - list of config group names
        """
        with self.app().config_lock:
            self._load_groups(groups)

    def load_all(self):
        """
        Load all config entries related to the application
        """
        pass

    def get(self, name, default=None):
        """
        Returns config value
        name - key identifier (format: "group.name")
        default - default value for the key
        """
        m = re_config_path.match(name)
        if not m:
            raise ConfigError("Invalid config key: %s" % name)
        (group, name) = m.group(1, 2)
        if group not in self._config:
            self.load_groups([group])
        return self._config[group].get(name, default)

    def get_group(self, group):
        """
        Returns config group as a dict
        group - group name
        """
        if not group in self._config:
            self.load_groups([group])
        return self._config[group]

    def set(self, name, value):
        """
        Change config value
        name - key identifier (format: "group.name")
        value - value to set
        Note: to store configuration in the database use store() method
        """
        if type(value) == str:
            value = unicode(value, "utf-8")
        m = re_config_path.match(name)
        if not m:
            raise ConfigError("Invalid config key: %s" % name)
        (group, name) = m.group(1, 2)
        with self.app().config_lock:
            if group not in self._config:
                self._load_groups([group])
            self._config[group][name] = value
            self._modified.add(group)

    def delete(self, name):
        """
        Delete config value
        name - key identifier (format: "group.name")
        Note: to store configuration in the database use store() method
        """
        m = re_config_path.match(name)
        if not m:
            raise ConfigError("Invalid config key: %s" % name)
        (group, name) = m.group(1, 2)
        with self.app().config_lock:
            if group not in self._config:
                self._load_groups([group])
            try:
                del self._config[group][name]
                self._modified.add(group)
            except KeyError:
                pass

    def delete_group(self, group):
        """
        Delete config group
        group - group identifier
        Note: to store configuration in the database use store() method
        """
        with self.app().config_lock:
            self._config[group] = {}
            self._modified.add(group)

    def store(self):
        if len(self._modified):
            with self.app().config_lock:
                lst = self.app().objlist(DBConfigGroupList, [])
                lst.load()
                for g in self._modified:
                    data = self._config[g]
                    obj = self.app().obj(DBConfigGroup, g, data=data)
                    if data:
                        obj.dirty = True
                        lst.append(obj)
                    else:
                        obj.remove()
                lst.store()
                self._modified.clear()

