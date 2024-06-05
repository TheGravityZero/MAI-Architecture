from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Index, inspect
from sqlalchemy.orm import sessionmaker
import json
import time
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
import random


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
            Column('recipient_login', String(255)),
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
            print("Successful initializated recipients")
        else:
            print("Postgres already initialized")


class MongoManager:
    def __init__(self):
        self.client = MongoClient(f"mongodb://root:root@mongo:27017/")
        self.db = self.client.get_database("arch")

    def get_collection(self, collection_name: str):
        return self.db.get_collection(collection_name)


class PackagesIniter:
    def create_packages(self, collection: Collection):
        if collection.find_one():
            print("Packages already inited")
            return
        packages: list[dict] = []
        for _ in range(1000):
            package = {}
            package["weight"] = random.random() * 100
            package["price"] = random.random() * 100
            packages.append(package)
        packages_ids = collection.insert_many(packages).inserted_ids
        print("Successful initializated packages")
        return packages_ids


class DeliveriesIniter:
    def create_deliveries(self, packages_ids: list[ObjectId], collection: Collection):
        if collection.find_one():
            print("Deliveries already inited")
            return
        with open("./recipients.json", "r") as data_json:
            data: dict = json.load(data_json)
        users_list = data['recipients']
        deliveries: list[dict] = []
        states: list[str] = ["on the way", "delivered"]
        for _ in range(len(packages_ids)):
            delivery = {}
            choises = [i for i in (random.choices(users_list, k=2))]
            delivery["from_address"], delivery["to_address"] = choises[0]["address"], choises[1]["address"]
            delivery["sender"], delivery["recipient"] = users_list.index(
                choises[0]), users_list.index(choises[1])
            delivery["state"] = random.choice(states)
            delivery["package_id"] = packages_ids.pop(
                random.randint(0, len(packages_ids))-1)
            deliveries.append(delivery)
        collection.insert_many(deliveries)
        print("Successful initializated deliveries")
        collection.database.client.close()


if __name__ == "__main__":
    SQLAlchemyManager(db_name="arch_db").init_database()
    manager = MongoManager()
    packages_collection = manager.get_collection("packages")
    deliveries_collection = manager.get_collection("deliveries")
    packages_ids = PackagesIniter().create_packages(collection=packages_collection)
    if packages_ids:
        deliveries_manager = DeliveriesIniter().create_deliveries(
            packages_ids=packages_ids, collection=deliveries_collection)
