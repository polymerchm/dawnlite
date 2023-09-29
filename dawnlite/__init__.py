import sys
import logging
import errno
from pickle import TRUE
import subprocess
import os
import sys



import click
from flask import Flask, request, jsonify, abort, render_template
from flask_cors import CORS, cross_origin

from dawnlite import model
from dawnlite import comm
from dawnlite import templates


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__, 
                      static_folder=os.path.join(ROOT_PATH, 'frontend', 'static'),
                      template_folder=os.path.join(ROOT_PATH, 'frontend'))

    app.config['CORS_HEADERS'] = 'Content-Type'                  

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/alarms.db'.format(app.instance_path)

    # the alarm queue is a LIFO of commands to turn on the light
    # the dawnliteDaemoon processese these
    app.config['DAWNLITE_ALARM_QUEUE_KEY'] = 'dawnlite_alarm_queue'
  
    #the remote_queue is a LIFO list of commands from the remoteControl daemon
    # to change the light settings in real time the dawnlightDaemon processes there
    app.config['DAWNLITE_REMOTE_QUEUE_KEY'] = 'dawnlite_remote_queue'
    
    # the status_light_quue is a LIFO List of commands to to on/off the status led and
    # is processed by the statusLED daemon
    app.config['DAWNLITE_STATUS_LIGHT_QUEUE_KEY'] = 'dawnlite_status_light_queue'
    
    # the status_light_quue is a LIFO List of commands to to on/off the status led and
    # is processed by the statusLED daemon
    app.config['DAWNLITE_MAIN_LIGHT_QUEUE_KEY'] = 'dawnlite_main_light_queue'

    #current state of the app (the backend)
    #all references to the state should be of laterest version on the redis server
    app.config['DAWNLITE_STATE_KEY'] = 'dawnlite_state'

    #if ramping the light in in process
    # the button and remoteControl apps wiill read/set this key
    # if 0, then ramping is not ocurring.   if a +ve number, its the number of seconds between steps
    # if -ve, its tell the ramping routing to stop immediately.
    app.config['DAWNLITE_RAMPING_KEY'] = 'dawnlite_ramping'
 
    # GPIO Inventory (BCM(Pin))
    #
    # 18(12)      Main Light (PWM)
    # 19(13)      Status LED (PCM)
    # 20(38)      Dim button
    # 21(40)      Toggle Button 
    # 26(37)      Bright Button
    # 6(31)       Reset (used by RaspWifi)


    # app.config['ALARM_PRE_DURATION'] = 60 * 30 # 30 minutes
    app.config['ALARM_POST_DURATION'] = 60 * 15 # 15 minutes
    app.config['LED_TYPE'] = "common_anode" # common anode -> pull down port to turn on
    #app.config['LED_TYPE'] = "common_cathode" # common cathode -> pull up port to turn on
    app.config['RAMP_DURATION'] = 1 # seconds  
    app.config['PWM_FREQUENCY'] = 12000 # 12 KHz 
    app.config['RAMP_STEPS'] = 100

    app.config['MAIN_LED_PWM'] = 1  #GPIO 18(12)
    app.config['STATUS_LED_PWM'] = 0 #GPIO 19(13)

    app.config['DIM_BUTTON'] = 'GPIO20'
    app.config['BRIGHT_BUTTON'] = 'GPIO26'
    app.config['TOGGLE_BUTTON'] = 'GPIO21'
    app.config['RASPIWIFI_RESET'] = 'GPIO6'

    app.config['REMOTE_REPEAT_DELAY'] = 2 # seconds
    app.config['STATUS_LED_INTERPULSE_DELAY'] = 0.500  # 500 milliseconds

    app.config['WIFI_LIST_KEY'] = 'wifi_list'
    app.config['NETWORK_INFO_KEY'] = 'network_info'


 
    
    app.config['DEBUG'] = True

    

    model.db.init_app(app)
    model.db.app = app
    CORS(app, resources={r"/*": {"origins": "*"}})
    

    return app


app = create_app()

logging.basicConfig( filename='record.log', 
                    format = '%(levelname)-10s %(asctime)s %(module)-20s-%(funcName)-20s %(message)s'
                    )
LOGGER = logging.getLogger('dawnlite')
LOGGER.setLevel(logging.DEBUG)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
alarm_queue = app.config['DAWNLITE_ALARM_QUEUE_KEY']


# def options (self):
#     return {'Allow' : 'PUT' }, 200, \
#     { 'Access-Control-Allow-Origin': '*', \
#       'Access-Control-Allow-Methods' : '*' }



@app.route('/api/alarm', methods=['GET'])
def get_alarms():
    LOGGER.debug("Entering alarm GET")
    alarms = model.Alarm.query.all()
    response = jsonify([alarm.to_dict() for alarm in alarms])
    return response


@app.route('/api/alarm', methods=['POST', 'OPTIONS'])
def add_alarm():
    alarm = model.Alarm()
    alarm.update_from_dict(request.json)
    alarm.schedule_next_alarm()
    LOGGER.debug(f"adding alarm {alarm}")
    model.db.session.add(alarm)
    model.db.session.commit()
    comm.send_message(app,comm.ReloadAlarmsMessage(), alarm_queue)
    response = jsonify(alarm.to_dict())
    return response


@app.route('/api/alarm', methods=['GET'])
def get_alarm(id):
    alarm = model.Alarm.query.filter(model.Alarm.id == id).first()
    if alarm == None:
        LOGGER.info(f"for ID={id}, no alarm found")
        abort(404)
    response = jsonify(alarm.to_dict())
    return response


@app.route('/api/alarm', methods=['PATCH', 'OPTIONS'])
def update_alarm():
    if request.method == "PATCH":
        value = request.json
        id = value.get('id')
        alarm = model.Alarm.query.filter(model.Alarm.id == id).first()
        if alarm is None:
            LOGGER.info(f"for ID={id}, no alarm found")
            abort(404) 
        alarm.update_from_dict(value)
        alarm.schedule_next_alarm()
        LOGGER.debug(f"updating alarm {alarm}")
        model.db.session.commit()
        comm.send_message(app,comm.ReloadAlarmsMessage(), alarm_queue)
        response = jsonify(alarm.to_dict())
        return response
    else:
        return '', 204


@app.route('/api/alarm/<id>', methods=['DELETE'])
def delete_alarm(id):
    LOGGER.debug(f"method {request.method}")
    LOGGER.debug(f"deleting record {id}")
    if request.method == "DELETE":
        alarm = model.Alarm.query.filter(model.Alarm.id == id).first()
        if alarm == None:
            LOGGER.info(f"for ID={id}, no alarm found")
            abort(404)
        model.db.session.delete(alarm)
        model.db.session.commit()
        comm.send_message(app,comm.ReloadAlarmsMessage(), alarm_queue)            
    return '',204


@app.route('/api/light', methods=['GET'])
def get_light():
    state = comm.get_state(app)
    response = jsonify({'level': int(state.level), 'ramped': state.ramped, 'active_alarm': state.active_alarm})
    return response


@app.route('/api/light', methods = ['POST', 'OPTIONS'])
def patch_light():
    if request.method == 'POST':
        # LOGGER.debug(f" data = {request.json}")
        state = comm.get_state(app)
        if request.json == {}:
           LOGGER.error(f"request is empty")
           sys.exit(1)
        else:
            next_level = int(request.json.get('level'))
            if  next_level != state.level:
                state.update(next_level=next_level)
                comm.set_state(app,state)
                comm.send_message(app,comm.SetLightStateMessage(level=next_level, ramped=True), app.config['DAWNLITE_MAIN_LIGHT_QUEUE_KEY'])
            return jsonify({'level': next_level})
    else:
        return '', 204

@app.route('/api/nextAlarm', methods = ['GET'])
def next_alarm():
    alarm = model.Alarm.query.order_by(model.Alarm.next_alarm)
    nextAlarm = "no alarms" if alarm.first() == None else alarm.first().next_alarm
    return jsonify({'alarm' : nextAlarm})


# @app.route('/api', defaults={'path': ''})
# @app.route('/api/<path:path>')
# def api_four_oh_four(path):
#     flask.abort(404)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    LOGGER.debug(f"path is {path}")
    return render_template("index.html")


@app.cli.command()
def initdb():
    if not os.path.exists(app.instance_path):
        os.mkdir(app.instance_path)
    model.db.create_all()
    model.db.session.commit()

# @app.cli.command()
# @click.option('--sites-available-directory', default='/etc/nginx/sites-available')
# @click.option('--sites-enabled-directory', default='/etc/nginx/sites-enabled')
# @click.option('--server-name', default='_')
# def setup_nginx(sites_available_directory, sites_enabled_directory, server_name):
#     site = 'pi-dawn.conf'
#     conf_file_path = os.path.abspath(os.path.join(sites_available_directory, site))
#     link_file_path = os.path.join(sites_enabled_directory, site)
#     default_site_path = os.path.join(sites_enabled_directory, 'default')
#     with open(conf_file_path, mode='w') as conf_file:
#         conf_file.write(templates.NGINX_CONF.format(server_name=server_name))
#     try:
#         os.symlink(conf_file_path, link_file_path)
#     except IOError as e:
#         if e.errno != errno.EEXIST:
#             pass
#     try:
#         os.unlink(default_site_path)
#     except IOError as e:
#         if e.errno != errno.ENOENT:
#             pass
#     subprocess.check_call(['nginx', '-t'])
#     subprocess.check_call(['nginx', '-s', 'reload'])


# @app.cli.command()
# @click.option('--target-directory', default='/etc/systemd/system')
# @click.option('--effective-user', default='pi')
# def install_services(target_directory, effective_user):
#     bin_path = os.path.dirname(os.path.abspath(sys.argv[0]))
#     services = {
#         'dawnlite-web': templates.WEB_SERVICE,
#         'dawnlite': templates.MAIN_SERVICE,
#         'dawnlite-remote' : templates.REMOTE_SERVICE,
#     }
#     for name, template in services.items():
#         unit_file_path = os.path.abspath(os.path.join(target_directory, '{}.service'.format(name)))
#         with open(unit_file_path, mode='w') as unit_file:
#             unit_file.write(template.format(bin_path=bin_path, user=effective_user))

#     subprocess.check_call(['systemctl', 'daemon-reload'])
#     for name in services:
#         subprocess.check_call(['systemctl', 'start', name])
#         subprocess.check_call(['systemctl', 'enable', name])




if __name__=='__main__':
    app.run(debug=TRUE) #use with vscode