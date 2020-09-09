from flask import Flask
from app.config.Config import Config as config_app


###
# This is the bootstrap of the app, it creates the app and set it up
#   loading the values from the configuration file.
###
class App(object):


    def __init__(self):
        response = Flask(
            import_name=__name__,
            instance_path=config_app().data['instance_path'],
            instance_relative_config=config_app().data['instance_relative_config']
        )
        response.config['DEFAULT_TIMEZONE'] = config_app().data['timezone']
        response.config['SECRET_KEY'] = config_app().data['secret_key']
        response.config['TESTING'] = config_app().data['testing']
        response.debug = config_app().data['debug']
        response.config['SQLALCHEMY_BINDS'] = {
            'sqlite': config_app().data['database_conn_sqlite'],
            'mysql': config_app().data['database_conn_mysql']
        }
        response.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_app().data['sqlalchemy_track_modifications']
        self.data = response
        if config_app().data['enable_internal_log']:
            from logging.handlers import RotatingFileHandler
            import logging
            handler = RotatingFileHandler(
                config_app().data['internal_log_file_path'],
                maxBytes=config_app().data['internal_log_max_bytes'],
                backupCount=config_app().data['internal_log_backup_count']
            )
            logger = logging.getLogger(config_app().data['import_name'])
            logger.setLevel(logging.ERROR)
            logger.addHandler(handler)


    def run(self):
        return self.data
