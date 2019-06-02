from flask import Flask, Blueprint
from flask_restplus import Resource, Api, fields
from gutter.client import get_gutter_client
from gutter.client.models import Switch
import logging

# APP FLASK
app_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(app_v1, version='1.0', title='Woven Gutter Feature Toggle API', description='Woven feature flag management.')
ns = api.namespace('', description='SWITCH')

app = Flask(__name__)
app.register_blueprint(app_v1)
app.config['RESTPLUS_MASK_SWAGGER'] = False


switch = api.model('switch', {
    'id': fields.String(required=True, description='The feature flag switch identity'),
    'description': fields.String(description='More details about the feature flag'),
    'state': fields.String(description='State of feature flag'),
    'active': fields.Boolean(readonly=True, description='Active or not')
})

# REDIS
# redis_host = os.environ.get('REDIS_HOST', '10.0.0.19')
# redis_port = int(os.environ.get('REDIS_PORT', 6379))
# redis_password = os.environ.get('REDIS_PASSWORD', None)
# redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
# redis_dict = RedisDict(keyspace='my_redis', connection=redis_client)

# GUTTER
manager = get_gutter_client(
    storage={},
    autocreate=True
)


def prepare_to_return(switch_p):
    logging.info('[Switch] --> {}'.format(switch_p))
    _active = manager.active(switch_p.name)
    return {'id': switch_p.name,
            'description': switch_p.description,
            'state': switch_p.state_string,
            'active': _active
            }


def translate_state(state):
    if state == 'DISABLED':
        return Switch.states.DISABLED

    if state == 'SELECTIVE':
        return Switch.states.SELECTIVE

    if state == 'GLOBAL':
        return Switch.states.GLOBAL

    return Switch.states.DISABLED


@ns.route('/switch')
class Feature(Resource):
    @ns.expect(switch)
    @ns.marshal_with(switch, code=201)
    def post(self):
        _state = Switch.states.DISABLED
        _description = api.payload['id']

        if 'state' in api.payload:
            _state = translate_state(api.payload['state'])

        if 'description' in api.payload:
            _description = api.payload['description']

        _switch = Switch(api.payload['id'], state=_state, description=_description)
        manager.register(_switch)

        return prepare_to_return(_switch)

    @ns.marshal_list_with(switch, code=201)
    def get(self):
        _switches = [prepare_to_return(_s) for _s in manager.switches]
        return _switches


@ns.route('/switch/<string:id>')
class FeatureId(Resource):
    @ns.marshal_with(switch, code=201)
    def get(self, id):
        _switch = manager.switch(id)
        return prepare_to_return(_switch)

    @ns.marshal_with(switch, code=201)
    @ns.expect(switch)
    def patch(self, id):

        _switch = manager.switch(id)

        if 'state' in api.payload:
            _switch.state = translate_state(api.payload['state'])

        if 'description' in api.payload:
            _switch.description = api.payload['description']

        if len(_switch.changes) > 0:
            _switch.save()

        return prepare_to_return(_switch)


if __name__ == '__main__':
    app.run(debug=True)