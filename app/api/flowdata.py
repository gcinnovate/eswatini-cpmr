from flask import jsonify, request
from .. import db
# from ..models import FlowData, Permission
from . import api
# from .decorators import permission_required
# from .errors import forbidden
from .. import redis_client
from .tasks import save_flowdata


@api.route('/flowdata')
def get_flowdata():
    return "Text flow data"


@api.route('/kwtranslation', methods=['GET'])
def kwtranslation():
    keyword = request.args.get('keyword', '')
    print(keyword)
    ret = redis_client.shortnames.get(keyword.lower())
    if ret:
        return jsonify(ret)
    res = db.engine.execute(
        "SELECT facility, region_id, facility_id FROM shortnames_view WHERE short_name = '{0}'".format(
            keyword.lower()))
    if res:
        try:
            row = res[0]
            ret = {
                'facility': row.facility,
                'facility_id': row.facility_id,
                'region_id': row.region_id
            }
            return jsonify(ret)
        except:
            return jsonify({})


@api.route('/flowdata/', methods=['POST'])
def flowdata_webhook():

    # redis_client.districts set using @app.before_first_request
    districts = redis_client.districts
    facilities = redis_client.facilities

    save_flowdata.delay(
        request.args, request.json, districts, facilities)

    return jsonify({'message': 'success'})
