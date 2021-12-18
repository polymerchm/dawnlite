NGINX_CONF = """server {{
    listen 80;

    server_name {server_name};

    error_log  /var/log/nginx/error.log;

    location / {{
        proxy_pass         http://127.0.0.1:5000/;
        proxy_redirect     off;

        proxy_set_header   Host                 $host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }}
}}
"""

WEB_SERVICE = """[Unit]
Description=dawnlite Web Service

[Service]
Environment=FLASK_APP=dawnlite
ExecStart={bin_path}/flask run
User={user}

[Install]
WantedBy=multi-user.target
"""

MAIN_SERVICE = """[Unit]
Description=Dawnlite Service

[Service]
ExecStart={bin_path}/dawnlite-daemon
User={user}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

REMOTE_SERVICE = """[Unit]
Description=Dawnlite Remote Service

[Service]
ExecStart={bin_path}/dawnlite-remote
User={user}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""