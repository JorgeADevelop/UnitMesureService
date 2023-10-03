from chalice import Chalice

app = Chalice(app_name='UnitMeasureService')

if (app.current_request.stage_variables['DEBUG']):
    app.debug = True


@app.route('/')
def index():
    return {'hello': 'world'}
