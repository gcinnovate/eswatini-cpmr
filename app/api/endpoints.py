import json
from flask import jsonify, request
from . import api
from .. import redis_client, RAPIDPRO_APIv2_ROOT, CSFM_GENERIC_FLOW_UUID
from .tasks import post_request_to_rapidpro


@api.route('/start_csfm_flow', methods=['GET', 'POST'])
def start_csfm_flow():
    if request.method == "GET":
        code = request.args.get('code', '')
        msisdn = request.args.get('msisdn', '')
        if not msisdn:
            msisdn = request.args.get('phone', '')
    if request.method == "POST":
        data = request.get_json()
        code = data.get("code", request.args.get("code", ""))
        msisdn = data.get('msisdn', request.args.get("msisdn", ""))

    flow_starts_endpoint = RAPIDPRO_APIv2_ROOT + "flow_starts.json"
    extra_data = redis_client.shortnames.get(code.lower())
    if not extra_data:
        extra_data = {}
    params = {
        'flow': CSFM_GENERIC_FLOW_UUID,
        'urns': ["tel:{0}".format(msisdn.strip())],
        'extra': extra_data
    }
    print("KEYWORD: {0}, MSISDN: {1}".format(code, msisdn))
    print("Start Flow Params [URL: {0}], Params: {1}".format(flow_starts_endpoint, params))
    if request.method == "POST":
        print(request.get_json())
    post_data = json.dumps(params)
    post_request_to_rapidpro.delay(flow_starts_endpoint, post_data)

    return jsonify({'message': 'successfully queued'})
