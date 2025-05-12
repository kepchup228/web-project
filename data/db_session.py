import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return  # Если уже есть, то выходим

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")  # Проверка на наличие БД

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'  # Подключение
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)  # База данных
    __factory = orm.sessionmaker(bind=engine)  #Сессии

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)  # Создание всех таблиц в БД


def create_session() -> Session:
    global __factory
    return __factory()  # Создание новой сессии
