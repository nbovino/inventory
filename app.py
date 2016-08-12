from flask import (Flask, g, render_template, flash, jsonify, redirect, url_for, abort, session)
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import datetime
import forms
import models
import json

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'nfj2984ijNDUUFH89()&&iJINOkf)(_@KLNFE:!#RefwkFpyio'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.Technicians.get(models.Technicians.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """ Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request. response"""
    g.db.close()
    return response


@app.route('/')
def base():
    if current_user:
        return redirect(url_for('main_actions'))
    return render_template('base.html', time=datetime.datetime.now())


@app.route('/test', methods=('GET', 'POST'))
def test():
    return render_template('test.html', time=datetime.datetime.now())


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.Login_Form()
    form.technician.choices = [(t.id, t.full_name) for t in models.Technicians]
    if form.validate_on_submit():
        try:
            user = models.Technicians.get(models.Technicians.id == form.technician.data)
        except models.DoesNotExist:
            flash("Your pin or name is not correct", "error")
        else:
            if check_password_hash(user.pin, form.pin.data):  # checks if password equal to entered password
                login_user(user)  # creates cookie and starts a session
                flash("You've been logged in!", "success")
                return redirect(url_for('main_actions'))
            else:
                flash("Your name or pin doesn't match!", "error")
    return render_template('login.html', form=form, time=datetime.datetime.now())


@app.route('/main', methods=('GET', 'POST'))
@login_required
def main_actions():
    form = forms.Main_Actions_Form()
    if form.validate_on_submit():
        return redirect(url_for(form.options.data))
    return render_template('main_actions.html', form=form, time=datetime.datetime.now())


@app.route('/options', methods=('GET', 'POST'))
@login_required
def options():
    edit = models.Technicians.select().where(models.Technicians.id == current_user.id).get()
    form = forms.Options_Form(obj=edit)
    form.populate_obj(edit)
    if form.validate_on_submit():
        models.Technicians.update_user(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            pin=form.pin.data
        )
        flash("Technician updated", "success")
        return redirect(url_for('main_actions', form=forms.Main_Actions_Form(), time=datetime.datetime.now()))
        # return render_template('options.html', form=form, time=datetime.datetime.now())
    else:
        return render_template('options.html', form=form, time=datetime.datetime.now())


@app.route('/new_inventory', methods=('GET', 'POST'))
@login_required
def new_inventory():
    form = forms.New_Inventory_Form()

    # form.item_type.choices = [(g.id, g.item_type) for g in models.Item_Types]
    # form.item_model.choices = [(g.id, g.item_model) for g in models.Item_Models]  #.select().where(models.Item_Models.of_type == 2)]


    if form.validate_on_submit():
        models.Inventory_Items.create_item(
            type = form.item_type.data,
            model = form.item_model.data,
            description = form.item_desc.data,
            location = form.location.data,
            serial_no = form.serial_no.data,
            dia_serial_no = form.dia_serial_no.data,
            notes = form.notes.data,
            stock=0
        )
        return redirect(url_for('new_inventory', form=form, time=datetime.datetime.now()))  # Redirect clears the form
    return render_template('new_inventory.html', form=form, time=datetime.datetime.now())



@app.route('/transfer', methods=('GET', 'POST'))
@login_required
def transfer_inventory():
    form = forms.Transfer_Form()
    form.item_type.choices = [(g.id, g.item_type) for g in models.Item_Types]
    form.item_model.choices = [(g.id, g.item_model) for g in models.Item_Models]
    return render_template('transfer_inventory.html', form=form, time=datetime.datetime.now())


@app.route('/logout')
@login_required
def logout():
    logout_user()  # deletes cookie and ends session
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('base'))


@app.route('/add_technician', methods=('GET', 'POST'))
@login_required
def add_technician():
    form = forms.Add_Technician_Form()
    if form.validate_on_submit() and current_user.is_admin == True:
        flash("Yay, you registered!", "success")
        models.Technicians.create_user(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            pin=form.pin.data.strip(),
            is_admin=form.is_admin.data
        )
        return redirect(url_for('main_actions'))
    elif not current_user.is_admin:
        return redirect(url_for('main_actions', message="You are not an admin, you cannot add a technician"))
    return render_template('add_technician.html', form=form, time=datetime.datetime.now())


@app.route('/add_type_or_model', methods=('GET', 'POST'))
@login_required
def add_type_or_model():
    form1 = forms.Add_Type_Form(prefix='form1')
    form2 = forms.Add_Model_Form(prefix='form2')

    form2.item_type.choices = [(g.id, g.item_type) for g in models.Item_Types]
    form2.manufacturer.choices = [(g.id, g.manufacturer) for g in models.Manufacturers]

    if form1.validate_on_submit() and form1.is_submitted():
        models.Item_Types.create_type(
            name=form1.item_type.data.strip()
        )

        item_id = models.Item_Types.get(models.Item_Types.item_type == form1.item_type.data.strip())

        add_item_type_to_json(form1.item_type.data.strip(), item_id.id)

        return redirect(url_for('add_type_or_model'))
    if form2.validate_on_submit() and form2.is_submitted():
        models.Item_Models.create_model(
            name=form2.item_model.data.strip(),
            description=form2.description.data.strip(),
            manufacturer=form2.manufacturer.data,
            of_type=form2.item_type.data
        )

        model_id = models.Item_Models.get(models.Item_Models.item_model == form2.item_model.data.strip())

        add_model_to_json(form2.item_type.data,
                          model_id.id,
                          form2.item_model.data.strip(),
                          form2.manufacturer.data, form2.description.data.strip())
        return redirect(url_for('add_type_or_model'))
    return render_template('add_type_or_model.html', form1=form1, form2=form2, time=datetime.datetime.now())


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


def add_model_to_json(of_type, model_id, name, manufacturer, description):
    model = {
        'name' : name,
        'model_id' : str(model_id),
        'manufacturer' : str(manufacturer),
        'of_type' : str(of_type),
        'description' : description
    }

    write_to_file = open('static/data/models.json', 'a')
    json.dump(model, write_to_file)

def add_item_type_to_json(item_type, type_id):
    item_type = {
        'item_id' : str(type_id),
        'item_type' : item_type,
    }
    write_to_file2 = open('static/data/item_types.json', 'a')
    json.dump(item_type, write_to_file2)

    # "of_type": "1", "model_id": 1, "name": "K1000", "manufacturer": 1, "description": "HP wireless keyboard"


if __name__ == '__main__':
    models.initialize()
    try:
        models.Technicians.create_user(
            first_name='John',
            last_name='Doe',
            pin='1234',
            is_admin=True
            )
        models.Technicians.create_user(
            first_name='Jane',
            last_name='Lapinski',
            pin='5678',
            # is_admin=False
        )
    except ValueError:
        pass
    try:
        models.Inventory_Items.create_item(
            type='Keyboard',
            model='K100',
            description='HP wireless keyboard',
            location='warehouse',
            serial_no='23451',
            dia_serial_no='00001',
            notes='None',
            stock=1,
        )
        models.Inventory_Items.create_item(
            type='Router',
            model='WL500',
            description='Wireless Netgear router',
            location="Jim's office",
            serial_no='12345',
            dia_serial_no='00002',
            notes='This will need replaced soon',
            stock=3,
        )
    except ValueError:
        pass
    try:
        models.Item_Types.create_type(name="Keyboard")
        models.Item_Types.create_type(name="Router")
        models.Item_Types.create_type(name="Screen")
    except ValueError:
        pass
    try:
        models.Item_Models.create_model(name='K1000',
                                        manufacturer=1,
                                        of_type=1,
                                        description='HP wireless keyboard')
        models.Item_Models.create_model(name='WL500',
                                        manufacturer=2,
                                        of_type=2,
                                        description='Wireless Netgear router')
        models.Item_Models.create_model(name='WL9000',
                                        manufacturer=2,
                                        of_type=2,
                                        description='Wireless Netgear router, more powerful')
    except ValueError:
        pass
    try:
        models.Manufacturers.create_manufacturer(name='Hewlet Packard')
        models.Manufacturers.create_manufacturer(name='Netgear')
    except ValueError:
        pass

    # create json file for javascript to use
    # models_array = []
    # for m in models.Item_Models.select():
    #     model = {
    #         'name' : m.item_model,
    #         'model_id' : m.id,
    #         'manufacturer' : m.manufacturer,
    #         'of_type' : m.of_type,
    #         'description' : m.description
    #     }
    #     models_array.append(model)
    #
    # write_to_file = open('static/data/models.json', 'a')
    # json.dump(models_array, write_to_file)
    #
    # item_types_array = []
    # for t in models.Item_Types.select():
    #     item_type = {
    #         'item_id' : t.id,
    #         'item_type' : t.item_type,
    #     }
    #     item_types_array.append(item_type)
    #
    # write_to_file2 = open('static/data/item_types.json', 'a')
    # json.dump(item_types_array, write_to_file2)


    app.run(debug=DEBUG, host=HOST, port=PORT)
