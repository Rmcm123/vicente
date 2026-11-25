from peewee import SqliteDatabase

from auxiliares.configuracion import RUTA_BASE_DATOS

base_datos = SqliteDatabase(RUTA_BASE_DATOS, pragmas={"foreign_keys": 1})
