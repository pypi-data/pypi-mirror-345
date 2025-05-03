#!/usr/bin/env python3
import configparser
import getpass
import os
import pwd
from abc import ABC, abstractmethod
from typing import Mapping

import keyring
import psycopg2
import psycopg2.extensions

"""
object wrapper for psycopg2
database utility functions / classes
"""


class AbstractDatabase(ABC):
    """OO wrapper for psycopg2 and Facade to connect PasswordCache"""
    __DATABASE = 'database'
    """Password cache context"""

    def __init__(self):
        self._app_name = 'Python app'
        self.schema = None
        self.port = 5432
        self._sslmode = None

    @abstractmethod
    def host(self) -> str:
        pass

    @abstractmethod
    def database_name(self) -> str:
        pass

    @abstractmethod
    def user(self) -> str:
        pass

    @abstractmethod
    def password(self) -> str:
        pass

    def set_app_name(self, name):
        """set application name"""
        self._app_name = name

    def application_name(self):
        return self._app_name

    def require_ssl(self):
        """Require SSL connection"""
        self._sslmode = 'require'

    def connect_fail(self, database, user, password, schema):
        """Overridable callback when connect fails"""
        pass

    def connect_success(self, database, user, password, schema):
        """Overridable callback when connect fails"""
        pass

    def connect(self, *, database_name: str = None, application_name: str = None, schema: str = None,
                **kwargs):
        """Connect to database, set schema if present, return connection
        :param database_name: use instead of self.database_name()
        :param application_name: name to use for connection string
        :param schema: use instead of self.schema
        :return database connection
        """
        if application_name is not None:
            appname = application_name
        else:
            appname = self.application_name()
        if schema is not None:
            sch = schema
        else:
            sch = self.schema
        if database_name is not None:
            dbname = database_name
        else:
            dbname = self.database_name()
        user = self.user()
        password = self.password()
        connect_string = f"host='{self.host()}' dbname='{dbname}' user='{user}' password='{password}' port={self.port}"
        if self._sslmode:
            connect_string += f" sslmode='{self._sslmode}'"
        try:
            conn = psycopg2.connect(connect_string, application_name=appname, **kwargs)
            self.connect_success(dbname, user, password, sch)
        except psycopg2.OperationalError:
            self.connect_fail(dbname, user, password, sch)
            raise
        if sch is not None:
            with conn.cursor() as cursor:
                cursor.execute("set search_path to {}".format(sch))
            conn.commit()

        return conn


class DatabaseSimple(AbstractDatabase):
    """
    Create by specifying parameters
    """

    def __init__(self, *, host: str, port: int = 5432, user: str, database_name: str):
        super().__init__()
        self._host = host
        self.port = port
        self.username = user
        self._dbname = database_name

    def host(self) -> str:
        return self._host

    def database_name(self) -> str:
        return self._dbname

    def user(self) -> str:
        if not self.username:
            u = input("database user: ")
            self.username = u.strip()
        return self.username

    @property
    def service_name(self):
        return f"Database {self.host()}.{self.database_name()}"

    def set_password(self, password) -> None:
        """"Set password explicitly"""
        keyring.set_password(self.service_name, self.user(), password)

    def password(self) -> str:
        """Get password from keyring or prompt"""
        if (pw := keyring.get_password(self.service_name, self.user())) is not None:
            return pw
        pw = getpass.getpass(f"Enter password for {self.service_name} {self.user()}")
        return pw

    def connect_success(self, database, user, password, schema):
        self.set_password(password)
        super().connect_success(database, user, password, schema)


class DatabaseDict(DatabaseSimple):
    """
    Create from dictionary with host/user/database keys
    """

    def __init__(self, *, dictionary: Mapping):
        host = dictionary['host']
        user = dictionary.get('user', None)
        if user == 'linux user':
            user = pwd.getpwuid(os.geteuid()).pw_name
        dbname = dictionary['database']
        port = int(dictionary.get('port', 5432))
        super().__init__(host=host, port=port, user=user, database_name=dbname)


class DatabaseConfig(DatabaseDict):

    def __init__(self, *, config: 'configparser.ConfigParser', section_key: str = 'database',
                 application_name: str = None):
        config_section = config[section_key]
        super().__init__(dictionary=config_section)
        self.set_app_name(application_name)


class SelfCloseConnection:
    """A ContextManger connection which closes itself when it goes out of scope"""

    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()


class SelfCloseCursor:
    """A ContextManger cursor which closes the connection when it goes out of scope"""

    def __init__(self, conn) -> None:
        self._conn = conn

    def __enter__(self):
        return self._conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    @property
    def connection(self):
        """Return connection"""
        return self._conn


class ReadOnlyCursor:
    """A ContextManager cursor which sets the session to readonly. Fails if current transaction is in place"""

    def __init__(self, conn, cursor_factory=None) -> None:
        self._conn = conn
        self._factory = cursor_factory

    def __enter__(self):
        self.existing_readonly = self._conn.readonly
        self._conn.readonly = True
        self._curs = self._conn.cursor(cursor_factory=self._factory)
        return self._curs

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._curs.close()
        self._conn.rollback()
        self._conn.readonly = self.existing_readonly

    @property
    def connection(self):
        """Return connection"""
        return self._conn


class NewTransactionCursor:
    """A ContextManger cursor which starts a new transaction (rollbacks any current SQL) statements,
    and commits in on normal exit"""

    def __init__(self, conn, cursor_factory=None) -> None:
        self._conn = conn
        self._factory = cursor_factory

    def __enter__(self):
        self._conn.rollback()
        return self._conn.cursor(cursor_factory=self._factory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._conn.rollback()
        else:
            self._conn.commit()

    @property
    def connection(self):
        """Return connection"""
        return self._conn


class Qobject:
    """Auto object generated from results of query"""

    def __str__(self) -> str:
        rval = ""
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                rval += k + ": " + str(v) + '\n'
        return rval


def query_to_object(cursor, query: str) -> list:
    """
    Convert generic query into list of objects
    :param cursor:
    :param query:
    :return: list of Objects with fields named after columns in query
    """
    cursor.execute(query)
    return cursor_to_objects(cursor)


def cursor_to_objects(cursor) -> list:
    """
    Convert cursor results to list of objects
    :param cursor: cursor that has just executed query
    :return: list of Objects with fields named after columns in query
    """
    rval = []
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    ncols = len(cols)
    for r in rows:
        qo = Qobject()
        for i in range(ncols):
            v = r[i]
            setattr(qo, cols[i], v)
        rval.append(qo)
    return rval


def update_object_in_database(cursor: psycopg2.extensions.cursor, object, table: str, key: str) -> None:
    """update an object whose fields match columns names into database
    :param cursor: open cursor with write access
    :param object: data source
    :param table: name of table to update
    :param key: primary key column name (only single key supported)
    :raises ValueError if key value not found on object or single row not updated
    """
    query = "update {} set ".format(table)
    sets = []
    values = []
    keyvalue = None
    for field, value in object.__dict__.items():
        if field != key:
            sets.append('{} = %s'.format(field))
            values.append(value)
        else:
            keyvalue = value
    if keyvalue is None:
        raise ValueError("Key attribute {} not found on {}".format(key, object))
    query += ','.join(sets)
    query += ' where {} = %s'.format(key)
    values.append(keyvalue)
    cursor.execute(query, values)
    if cursor.rowcount != 1:
        raise ValueError("No update for {}.{} value {}".format(table, key, keyvalue))


def row_estimate(connection, table: str) -> int:
    """A quick estimate about how many rows
    are in a table. +/ 10%"""
    with connection.cursor() as curs:
        curs.execute("""SELECT reltuples::bigint
        FROM pg_catalog.pg_class
        WHERE relname = %s""", (table,))
        row = curs.fetchone()
        return int(row[0])
