import sys
import logging
import errno
from pickle import TRUE
import subprocess
import os
import sys

import click
from flask import Flask, request, jsonify, abort, render_template, Response

from flask_cors import CORS, cross_origin
import redis
from dotenv import dotenv_values
from dawnlite import model
from dawnlite import comm
from dawnlite import templates
from dawnlite.utils import string_or_numeric
import time
from datetime import datetime



ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def string_or_numeric(value):
    try:
        int_value = int(value)
        return int_value
    except:
        try: 
            float_value = float(value)
            return float_value
        except:
            return value

def create_app():

    
    app = Flask(__name__, 
                      static_folder=os.path.join(ROOT_PATH, 'frontend', 'static'),
                      template_folder=os.path.join(ROOT_PATH, 'frontend'))

    app.config['CORS_HEADERS'] = 'Content-Type'                  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/alarms.db'.format(app.instance_path)

  
    env = dotenv_values('dawnlite/.env.global')
    for (key,val) in env.items():
        app.config[key] = string_or_numeric(val)


   

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
alarm_queue = app.config['ALARM_QUEUE_KEY']


# def options (self):
#     return {'Allow' : 'PUT' }, 200, \
#     { 'Access-Control-Allow-Origin': '*', \
#       'Access-Control-Allow-Methods' : '*' }


# sse setups here

@app.route('/api/stream')
def stream():
    def stream_send():
        while True:
            # the decision logic goes in here
            time.sleep(1)
            yield f'data: {datetime.now().second}\nevent: message\n\n'


    return Response(stream_send(), mimetype='text/event-stream')
        


@app.route('/api/alarms', methods=['GET'])
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
                comm.send_message(app,comm.SetLightStateMessage(level=next_level, ramped=True), app.config['MAIN_LIGHT_QUEUE_KEY'])
            return jsonify({'level': next_level})
    else:
        return '', 204

@app.route('/api/nextAlarm', methods = ['GET'])
def next_alarm():
    alarm = model.Alarm.query.order_by(model.Alarm.next_alarm)
    nextAlarm = "no alarms" if alarm.first() == None else alarm.first().next_alarm
    return jsonify({'alarm' : nextAlarm})


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