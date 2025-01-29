FROM python:3.12.5-bullseye
SHELL ["/bin/bash", "--login", "-c"]
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV COLUMNS=80
RUN apt-get update && apt-get install -y \
 curl nano python3-pip gettext chrpath libssl-dev libxft-dev postgresql-client supervisor \
 libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev sudo ufw systemd \
 python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx systemd-sysv \
 snapd redis-tools openssl libcap2-bin gpg less \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /code/
RUN pip install wheel
COPY . /code/

RUN curl -o /code/conf_files/awscliv2.zip "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" 
RUN gpg --import /code/conf_files/aws.pem
RUN curl -o /code/conf_files/awscliv2.sig "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip.sig"
RUN gpg --verify /code/conf_files/awscliv2.sig /code/conf_files/awscliv2.zip
RUN unzip /code/conf_files/awscliv2.zip -d /code/conf_files/
RUN bash /code/conf_files/aws/install -i /usr/local/aws-cli -b /usr/local/bin
RUN rm -rf /code/conf_files/awscliv2.sig /code/conf_files/awscliv2.zip /code/conf_files/aws/

RUN pip install -r requirements.txt
RUN pip install -e /code/build_files/accumate_robinstocks
COPY conf_files/supervisord_app.conf /etc/supervisor/conf.d/supervisord.conf
COPY conf_files/nginx.conf /etc/nginx/nginx.conf
RUN mkdir /run/gunicorn/
RUN chown www-data: /var/log/ /var/log/nginx /var/lib/nginx /var/www/
RUN chown www-data: /etc/nginx /etc/nginx/conf.d /etc/nginx/nginx.conf
RUN chmod 777 /etc
RUN mkdir /etc/letsencrypt /etc/letsencrypt/live /etc/letsencrypt/live/accumate-backend.link/
COPY conf_files/fullchain.pem /etc/letsencrypt/live/accumate-backend.link/fullchain.pem
COPY conf_files/privkey.pem /etc/letsencrypt/live/accumate-backend.link/privkey.pem
RUN mkdir /run/nginx/
RUN chown www-data: /run/nginx/ /run/gunicorn/
RUN chmod 775 /var/run/ /run
RUN chown :www-data /var/run/ /run/
RUN chown -R www-data: /code/
RUN setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx
USER www-data
CMD ["./build_files/entrypoint_app.sh"] 