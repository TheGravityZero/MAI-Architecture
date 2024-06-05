from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Index, inspect
from sqlalchemy.orm import sessionmaker
import json


class SQLAlchemyManager:
    def __init__(self, db_name: str = 'postgres'):
        try:
            self.engine = create_engine(
                'postgresql://root:root@postgres:5432/' + db_name)
            self.metadata = MetaData()
            self.metadata.bind = self.engine
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(e)

    def create_tables(self):
        users = Table(
            'recipients', self.metadata,
            Column('recipient_id', Integer, primary_key=True),
            Column('recipient_login', String(255), unique=True),
            Column('first_name', String(255)),
            Column('second_name', String(255)),
            Column('address', String(255)),
            Column('password', String(255))
        )

        self.metadata.create_all(self.engine)

        Index('recipient_id_index', users.c.recipient_id)
        Index('recipients_login_index', users.c.recipient_login)
        Index('first_name_index', users.c.first_name)
        Index('second_name_index', users.c.second_name)
        Index('address_index', users.c.address)

    def insert_data(self, data, table_name):
        session = self.Session()
        table = self.metadata.tables[table_name]
        session.execute(table.insert(), data)
        session.commit()
        session.close()

    def init_database(self):

        inspector = inspect(self.engine)
        if not inspector.has_table("recipients"):
            print("Initialize DB")
            self.create_tables()
            with open("./recipients.json", "r") as users_file:
                users_data = json.load(users_file)["recipients"]
            self.insert_data(users_data, "recipients")
            print("Successful initializing")
        else:
            print("Already inited")


sqlalchemy_manager = SQLAlchemyManager(db_name="arch_db")
sqlalchemy_manager.init_database()
