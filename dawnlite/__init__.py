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
from dotenv import dotenv_values
from dawnlite import model

from dawnlite import comm
from dawnlite import templates
from dawnlite.utils import string_or_numeric
import time, json
from datetime import datetime
from queue import Queue
import threading


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

            import requests


# from flask import Flask, render_template, request, jsonify, make_response
# app = Flask(__name__)
# @app.route('/', methods=['OPTIONS','POST'])
# def greeting():
#     if request.method == 'OPTIONS': 
#         return build_preflight_response()
#     elif request.method == 'POST': 
#         req = request.get_json()
#         # query user with req['id']
#         # for demonstration, we assume the username to be Eric
#         return build_actual_response(jsonify({ 'name': 'Eric' }))
# def build_preflight_response():
#     response = make_response()
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add('Access-Control-Allow-Headers', "*")
#     response.headers.add('Access-Control-Allow-Methods', "*")
#     return response
# def build_actual_response(response):
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     return response

class BetterTime(json.JSONEncoder):
    """
    Deal with stadard Flask jsonify output of datatime objects.
    formatting codes from man page for strftime() on raspberry pi 
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            str = obj.strftime(r"%a, %b %d, %l:%M%P")
            return str
        return super().default(obj)

class Flag:
    def __init__(self, flag=False):
        self._flag = flag

    @property
    def busy(self):
        return self._flag
    
    @busy.setter
    def busy(self,value):
        self._flag = value

def create_app():
    app = Flask(__name__, 
                      static_folder=os.path.join(ROOT_PATH, 'frontend', 'static'),
                      template_folder=os.path.join(ROOT_PATH, 'frontend'))

                
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/alarms.db'.format(app.instance_path)

  
    env = dotenv_values('dawnlite/.env.global', verbose=True)
    for (key,val) in env.items():
        app.config[key] = string_or_numeric(val)

    app.config['DEBUG'] = True


    model.db.init_app(app)
    model.db.app = app
   
   
    return app


app = create_app()
CORS(app)

app.json_encoder = BetterTime # elimiate issue with GMT as standaret output

#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})



logging.basicConfig( filename='record.log', 
                    format = '%(levelname)-10s %(asctime)s %(module)-20s-%(funcName)-20s %(message)s'
                    )
LOGGER = logging.getLogger('dawnlite')
LOGGER.setLevel(logging.DEBUG)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
alarm_queue = app.config['ALARM_QUEUE_KEY']

byPassStream = Flag()


# def options (self):
#     return {'Allow' : 'PUT' }, 200, \
#     { 'Access-Control-Allow-Origin': '*', \
#       'Access-Control-Allow-Methods' : '*' }



redisEventQueue = Queue()
redis = comm.redis_cli 
redisPubSub = redis.pubsub()


#event form redis caught here

def getRedisMessage(message):
    # this will setup to handle incoming form Redis and tell streat what to push onto the even
    redisEventQueue.put(message)

# def redisPubSub_exception_handler(ex, pubsub, thread):
#     print(f"Redis PubSub Error {ex}")
#     thread.stop()
#     thread.join(timeout=1.0)
#     pubsub.close()
    
redisPubSub.subscribe(**{'dawnlite': getRedisMessage})
redisThread = redisPubSub.run_in_thread(sleep_time=0.010, daemon=True)


# sse setups here

def updateAlarm(alarmDict):
    with app.app_context():
        alarm = model.db.session.query(model.Alarm.id == alarmDict.id).first()
        model.Alarm.update_from_dict(alarm, alarmDict)
        model.db.session.commit()


@app.route('/api/stream')
def stream():
    def stream_send():
        count = 0
        if byPassStream.busy:
            yield "data: none\nevent: bypass\n\n"
        while True:
            if redisEventQueue.empty():
                pass
            else:
                item = redisEventQueue.get()
                yield f"data: {item}\nevent: redis\n\n"
            time.sleep(1)
            # count = (count + 1) % 60 # count seconds
            yield f"data: {datetime.now().strftime('%Y-%m-%dT%I:%M:%S%p')}\nevent: pulse\n\n"
            
    return Response(stream_send(), mimetype='text/event-stream')
        


@app.route('/api/alarms', methods=['GET'])
def get_alarms():
    LOGGER.debug("Entering alarm GET")
    alarms = model.Alarm.query.all()
    response = jsonify([alarm.to_dict() for alarm in alarms])
    return response


@app.route('/api/alarm', methods=['POST'])
def add_alarm():
    byPassStream.busy = True
    alarm = model.Alarm()
    model.Alarm.update_from_dict(alarm,request.json)
    alarm.schedule_next_alarm()
    LOGGER.debug(f"adding alarm {alarm}")
    model.db.session.add(alarm)
    model.db.session.commit()
    comm.send_message(app,comm.ReloadAlarmsMessage(), alarm_queue)
    response = jsonify(alarm.to_dict())
    byPassStream.busy =  False
    return response


@app.route('/api/alarm/<id>', methods=['GET'])
def get_alarm(id):
    alarm = model.Alarm.query.filter(model.Alarm.id == id).first()
    if alarm == None:
        LOGGER.info(f"for ID={id}, no alarm found")
        abort(404)
    response = jsonify(alarm.to_dict())
    return response


@app.route('/api/alarm', methods=['PATCH'])
@cross_origin()
def update_alarm():
    if request.method == "PATCH":
        byPassStream.busy = True
        value = request.json
        id = value.get('id')
        alarm = model.Alarm.query.filter(model.Alarm.id == id).first()
        if alarm is None:
            LOGGER.info(f"for ID={id}, no alarm found")
            abort(404) 
        model.Alarm.update_from_dict(alarm, value)
        alarm.schedule_next_alarm()
        LOGGER.debug(f"updating alarm {alarm}")
        model.db.session.commit()
        comm.send_message(app,comm.ReloadAlarmsMessage(), alarm_queue)
        response = jsonify(alarm.to_dict())
        byPassStream.busy = False
        return response
    if request.method == "OPTIONS":
        return '',204
    else:
        return '', 204


@app.route('/api/alarm/<id>', methods=['DELETE'])
def delete_alarm(id):
    LOGGER.debug(f"method {request.method}")
    LOGGER.debug(f"deleting record {id}")
    if request.method == "DELETE":
        byPassStream.busy = True
        alarm = model.Alarm.query.filter(model.Alarm.id == id).first()
        if alarm == None:
            LOGGER.info(f"for ID={id}, no alarm found")
            abort(404)
        model.db.session.delete(alarm)
        model.db.session.commit()
        comm.send_message(app,comm.ReloadAlarmsMessage(), alarm_queue)    
        byPassStream.busy = False           
    return '',204


@app.route('/api/light', methods=['GET'])
def get_light():
    state = comm.get_state(app)
    response = jsonify({'level': int(state.level), 'ramped': state.ramped, 'active_alarm': state.active_alarm})
    return response


@app.route('/api/light', methods = ['POST'])
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
    nextList = sorted([x.next_alarm for x in  model.Alarm.query.all() if x.next_alarm != None])
    nextAlarm = "no alarms" if len(nextList) == 0 else nextList[0]
    result = jsonify({'alarm' : nextAlarm})
    return result


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