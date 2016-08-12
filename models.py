import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin, current_user
from peewee import *

DATABASE = SqliteDatabase('inventory.db')


class Technicians(UserMixin, Model):
    first_name = CharField()
    last_name = CharField()
    full_name = CharField(unique=True)
    pin = CharField(max_length=100)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-last_name',)

    @classmethod
    def create_user(cls, first_name, last_name, pin, is_admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=first_name + " " + last_name,
                    pin=generate_password_hash(pin),
                    is_admin=is_admin)
        except IntegrityError:
            raise ValueError("User already exists")

    @classmethod
    def update_user(cls, first_name, last_name, pin):
        try:
            with DATABASE.transaction():
                q = Technicians.update(first_name=first_name, last_name=last_name, full_name=first_name + " " + last_name,
                                      pin=generate_password_hash(pin)).where(Technicians.id == current_user.id)
                q.execute()

        except IntegrityError:
            raise ValueError("Cannot update")

    def get_full_name(self):
        return Technicians.query.with_entities(Technicians.full_name)


class Manufacturers(Model):
    manufacturer = CharField(unique=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_manufacturer(cls, name):
        try:
            with DATABASE.transaction():
                cls.create(
                    manufacturer=name
                )
        except IntegrityError:
            raise ValueError("Manufacturer already in database")


class Item_Types(Model):
    item_type = CharField(unique=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_type(cls, name):
        try:
            with DATABASE.transaction():
                cls.create(
                    item_type=name
                )
        except IntegrityError:
            raise ValueError("Type already exists")


class Item_Models(Model):
    item_model = CharField(unique=True)
    manufacturer = IntegerField()
    of_type = IntegerField()
    description = CharField()

    class Meta:
        database = DATABASE
        order_by = ('id',)

    @classmethod
    def create_model(cls, name, manufacturer, of_type, description):
        try:
            with DATABASE.transaction():
                cls.create(
                    item_model=name,
                    manufacturer=manufacturer,
                    of_type=of_type,
                    description=description,
                )
        except IntegrityError:
            raise ValueError("Type already exists")

class Inventory_Items(Model):
    item_type = CharField()  # maybe just populate this from types of items table
    item_model = CharField()  # or make it a foreign key field
    item_desc = TextField()
    location = CharField()  #(scan barcode)
    serial_no = CharField(unique=True)  #(scan Manufacture S/N)
    dia_serial_no = CharField(unique=True)  #(scan diamond s/n)
    last_updated=DateTimeField()
    stock = IntegerField()
    notes = TextField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_item(cls, type, model, description, location, serial_no, dia_serial_no, notes=None, stock=0):
        try:
            with DATABASE.transaction():
                cls.create(
                    item_type=type,
                    item_model=model,
                    item_desc=description,
                    location=location,
                    serial_no=serial_no,
                    dia_serial_no=dia_serial_no,
                    last_updated=datetime.datetime.now(),
                    notes=notes,
                    stock=stock
                )
        except IntegrityError:
            raise ValueError("Item already exists")

    @classmethod
    def add_inventory(cls, serial_no, dia_serial_no, stock=0):
        try:
            with DATABASE.transaction():
                q = Inventory_Items.update(stock=stock).where(Inventory_Items.serial_no == serial_no and Inventory_Items.dia_serial_no == dia_serial_no)
                q.execute()
        except IntegrityError:
            raise ValueError("Cannot update")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Technicians, Inventory_Items, Manufacturers, Item_Types, Item_Models], safe=True)
    DATABASE.close()