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
    FlowData, SummaryCases, FacilityShortName)
import datetime
from flask import current_app
from sqlalchemy.sql import text
from getpass import getpass
from calendar import monthrange
from config import INDICATOR_NAME_MAPPING, INDICATORS, INDICATOR_POSSIBLE_VALUES

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
    locs = Location.query.filter_by(level=2).all()
    districts = {}
    for l in locs:
        districts[l.name] = {'id': l.id, 'parent_id': l.parent_id}
    redis_client.districts = districts

    stations = Facility.query.all()
    facilities = {}
    for s in stations:
        facilities[s.name] = s.id
    redis_client.facilities = facilities
    results = db.engine.execute("SELECT * FROM shortnames_view")
    shortnames = {}
    for row in results:
        shortnames[row.short_name] = {
            'facility': row.facility,
            'facility_id': row.facility_id,
            'region_id': row.region_id
        }
    redis_client.shortnames = shortnames

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
@click.option('--report', '-r', default='csfm')
@click.option('--start-year', '-s', default=2016)
@click.option('--end-year', '-e', default=2020)
@click.option('--start-month', '-m', default=1)
@click.option('--end-month', '-n', default=13)
@click.option('--limit', '-x', default="yes")  # whether to limit on years to create data for
def load_test_data(report, start_year, end_year, start_month, end_month, limit):
    # facilities that have shortnames/keywords
    facilities = Facility.query.filter(Facility.shortnames.any()).all()
    year = datetime.datetime.now().year
    if start_year == end_year:
        end_year += 1
    for y in range(start_year, end_year):
        for m in range(start_month, end_month):
            if y == year and m > datetime.datetime.now().month - 1:
                if limit == "yes":
                    continue
                else:
                    pass
            # loop through the day of the month
            # get a random number (n) of facilities out of those with keywords (may be 1/2 of them)
            # generate random data for the n facilities for that day
            num_days_in_month = monthrange(y, m)[1] # num_days = 28
            no_of_facilities_with_keywords = len(facilities)
            for d in range(1, num_days_in_month + 1):
                for i in range(random.choice(range(no_of_facilities_with_keywords))):  # random number of times
                    # time message is assumed to be received = created
                    created = '{0}-{1}-{2} {3}'.format(
                        y, m, d, random.choice(['12:00', '11:30', '13:20', '10:15', '14:20', '9:00', '8:20']))
                    month = '{0}-{1:02}'.format(y, m)
                    year = '{0}'.format(y)
                    # get a random facility
                    random_idx = random.choice(range(no_of_facilities_with_keywords))
                    facility = facilities[random_idx]
                    # now generate random data
                    values = {}
                    for indicator in INDICATORS.get(report, []):
                        # get a random value for indicator from its possibilities
                        possible_values_mapping = INDICATOR_POSSIBLE_VALUES.get(report, {})
                        possible_values = possible_values_mapping.get(indicator, [])
                        values[indicator] = random.choice(possible_values)

                    print(facility, "=>", created, "=>", values)

                    db.session.add(
                        FlowData(
                            created=created, month=month, year=year, facility=facility.id,
                            report_type=report, district=facility.region_id, values=values))
                    db.session.commit()


@app.cli.command("import-facilities")
@click.option('--filename', '-f')
def import_facilities(filename):
    click.echo('Importing facilities')

    locs = Location.query.filter_by(level=2).all()
    districts = {}
    for l in locs:
        districts[l.name] = l.id

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

    for d in data:
        if not (d[0] and d[1] and d[2]):
            click.echo("missing field")
            continue
        facility = Facility.query.filter_by(code=d[1]).first()
        if facility:
            click.echo("updating faility")
            facility.name = d[2]
            facility.region_id = districts[d[0]]
            shortnames = [x for x in d[3].strip().split(',') if x]

            for sname in shortnames:
                shortname_obj = FacilityShortName.query.filter_by(
                    facility_id=facility.id, short_name=sname.lower()).first()
                if not shortname_obj:
                    new_shortname_obj = FacilityShortName(facility_id=facility.id, short_name=sname.lower())
                    db.session.add(new_shortname_obj)

            code = d[1].strip()
            if code:
                shortname_obj = FacilityShortName.query.filter_by(
                    facility_id=facility.id, short_name=code.lower()).first()
                if not shortname_obj:
                    new_shortname_obj = FacilityShortName(facility_id=facility.id, short_name=code.lower())
                    db.session.add(new_shortname_obj)
            # facility.short_name = d[3]
        else:
            click.echo("adding faility")
            facility = Facility(region_id=districts[d[0]], code=d[1], name=d[2])
            db.session.add(facility)

            shortnames = [x for x in d[3].strip().split(',') if x]
            for sname in d[3].strip().split(','):
                if sname:
                    print("SNMAE=>", sname)
                    shortname_obj = FacilityShortName.query.filter_by(
                        facility_id=facility.id, short_name=sname.lower()).first()
                    if not shortname_obj:
                        new_shortname_obj = FacilityShortName(facility_id=facility.id, short_name=sname.lower())
                        db.session.add(new_shortname_obj)

            code = d[1].strip()
            if code:
                shortname_obj = FacilityShortName.query.filter_by(
                    facility_id=facility.id, short_name=code.lower()).first()
                if not shortname_obj:
                    new_shortname_obj = FacilityShortName(facility_id=facility.id, short_name=code.lower())
                    db.session.add(new_shortname_obj)
        db.session.commit()
