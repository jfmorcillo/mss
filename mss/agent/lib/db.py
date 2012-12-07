# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from sqlalchemy import create_engine, event
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine

from datetime import datetime
import json

engine = create_engine('sqlite:////var/lib/mss/mss-agent.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class OptionTable(Base):
    __tablename__ = 'option'

    key = Column(String, primary_key=True)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = json.dumps(value)

    def __repr__(self):
        return "<Option('%s', '%s')>" % (self.key, self.value)


class ModuleTable(Base):
    __tablename__ = 'module'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    configured = Column(DateTime, default=None)
    logs = relationship("LogTable", backref="module")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Module('%s','%s')>" % (self.name, self.configured)


class LogTypeTable(Base):
    __tablename__ = 'log_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<LogType('%s')>" % self.name


class LogTable(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('log_type.id'))
    module_id = Column(Integer, ForeignKey('module.id'))
    data = Column(String)
    date = Column(DateTime)

    def __init__(self, type, module, data):
        self.type_id = type
        self.module_id = module
        self.data = json.dumps(data)
        self.date = datetime.now()

    def __repr__(self):
        return "<Log('%s','%s', '%s')>" % (self.type_id, self.module_id, self.date)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
