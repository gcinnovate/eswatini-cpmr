import os
# import sys
import string
import random
import click
from openpyxl import load_workbook
from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade
from app import create_app, db, redis_client
from app.models import (
    Location, LocationTree, Facility, User, Role,
    FlowData, SummaryCases)
from datetime import datetime
from flask import current_app
from sqlalchemy.sql import text
from getpass import getpass
from config import INDICATOR_NAME_MAPPING

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.before_first_request
def before_first_request_func():
    locs = Location.query.filter_by(level=3).all()
    districts = {}
    for l in locs:
        districts[l.name] = {'id': l.id, 'parent_id': l.parent_id}
    redis_client.districts = districts

    stations = Facility.query.all()
    facilities = {}
    for s in stations:
        facilities[s.name] = s.id
    redis_client.facilities = facilities

    print("This function will run once")


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


@app.cli.command("initdb")
def initdb():
    def id_generator(size=12, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    Role.insert_roles()
    country = Location.query.filter_by(name='Eswatini', level=1).all()
    if country:
        click.echo("Database Already Initialized")
        return

    click.echo("Database Initialization Starting.............!")

    db.session.add(LocationTree(name='Eswatini Administrative Divisions'))
    db.session.commit()
    # Add country
    db.session.add(Location(name='Eswatini', code=id_generator(), tree_id=1))  # Country
    # Add the regions
    db.session.add_all(
        [
            Location(name='Hhohho', code=id_generator(), parent_id=1, tree_id=1),  # 2
            Location(name='Lubombo', code=id_generator(), parent_id=1, tree_id=1),  # 3
            Location(name='Manzini', code=id_generator(), parent_id=1, tree_id=1),  # 4
            Location(name='Shiselweni', code=id_generator(), parent_id=1, tree_id=1),  # 5
        ]
    )

    db.session.commit()

    click.echo("Database Initialization Complete!")


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()


@app.cli.command("create-user")
def createuser():
    username = input("Enter Username: ")
    email = input("Enter Email: ")
    password = getpass()
    cpass = getpass("Confirm Password: ")
    assert password == cpass
    u = User(username=username, email=email)
    u.password = cpass
    db.session.add(u)
    db.session.commit()
    u.confirmed = True
    db.session.commit()
    click.echo("User added!")


@app.cli.command("create-views")
def create_views():
    with current_app.open_resource('../views.sql') as f:
        # print(f.read())
        click.echo("Gonna create views")
        db.session.execute(text(f.read().decode('utf8')))
        db.session.commit()
        click.echo("Done creating views")


@app.cli.command("load_test_data")
def load_test_data():
    pass


@app.cli.command("import-facilities")
@click.option('--filename', '-f')
def import_facilities(filename):
    click.echo('Importing facilities')

    wb = load_workbook(filename, read_only=True)
    for sheet in wb:
        # print sheet.title
        data = []
        headings = []
        j = 0
        for row in sheet.rows:
            if j > 0:
                # val = ['%s' % i.value for i in row]
                val = [u'' if i.value is None else str(i.value) for i in row]
                # print val
                data.append(val)
            else:
                headings = [u'' if i.value is None else str(i.value) for i in row]
            j += 1

    for d in data[:10]:
        print(d)
