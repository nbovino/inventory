from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, IntegerField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)
from flask_login import current_user
from flask import g

import models
import app


class Login_Form(Form):
    technician = SelectField(
        "Technician",
        coerce=int
    )
    pin = PasswordField('Pin', validators=[DataRequired(),
                                           Length(max=4)
                                           ])


class Main_Actions_Form(Form):
    options = SelectField(
        choices=[('new_inventory', 'New Inventory',),
                 ('transfer_inventory', 'Transfer / Deployment Inventory'),
                 ('do', 'Do Inventory'),
                 ('adjust', 'Adjust Locations'),
                 ('add_type_or_model', 'Add Item Type/Model'),
                 ('options', 'Personal Options')]
    )

class Add_Technician_Form(Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    pin = PasswordField('PIN', validators=[DataRequired()])
    is_admin = BooleanField()


class Options_Form(Form):
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    pin = PasswordField(validators=[DataRequired()])


class New_Inventory_Form(Form):
    item_type = SelectField("Type", choices=()) # First arg becomes the id element in the html
    item_model = SelectField("Model", choices=())
    item_desc = StringField("Description")
    location = StringField("Location")
    serial_no = StringField("Serial No")
    dia_serial_no = StringField("Diamond Serial No")
    notes = TextAreaField("Notes")


class Transfer_Form(Form):
    item_type = SelectField("Type", coerce=int)
    item_model = SelectField("Model", coerce=int)
    manufacturer = StringField()
    item_desc = StringField()
    serial_no = StringField()
    dia_serial_no = StringField()


class Add_Type_Form(Form):
    item_type = StringField()


class Add_Model_Form(Form):
    manufacturer = SelectField(label="Choose a Manufacturer", coerce=int)
    item_type = SelectField("Type", coerce=int)
    item_model = StringField()
    description = StringField()
