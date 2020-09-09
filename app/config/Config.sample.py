import os


class ConfigSample(object):

    def __init__(self):
        self.data = {
            'ip': '0.0.0.0',
            'port': 8082,
            'import_name': __name__,
            'instance_path': None,
            'instance_relative_config': True,
            'debug': True,
            'testing': True,
            'timezone': 'UTC',
            'date_format': '%m%d%y',
            'secret_key': 'qwerty',
            'database_conn_sqlite': 'sqlite:////' + os.getcwd() + '/app/data/default.db',
            'database_conn_mysql': 'mysql://uid:qwerty@1.2.3.4/db_name',
            'sqlalchemy_track_modifications': True,
            'enable_internal_log': True,
            'internal_log_file_path': 'app/logs/access_log',
            'internal_log_max_bytes': 2097152,
            'internal_log_backup_count': 10,
            'database_log_backup_count': 10,
            'limit': {
                'soft': 100,
                'hard': 1000
            },
            'ban_timeout_millis': 60000,
            'ban_trap_range_millis': 1000,
            'ban_trap_max_attempts_in_range': 10,
            'service_timer_baseurl': 'http://1.2.3.4:8080/secret/qwerty/',
            'service_email_validate_secret': 'qwerty',
            'service_email_validate_baseurl': 'http://1.2.3.4:8081/v1/email/validate/',
            'token_expires_after_seconds': 600,
            'ott_token_expires_after_seconds': 30,
            'transport_interval_seconds': 2,
        }

        ###
        # In production mode, the settings below takes priority overriding the ones above.
        ###
        if os.getenv('APP_PROD_' + self.data['secret_key']) is not None:
            if os.getenv('APP_PROD_' + self.data['secret_key']):
                self.data['debug'] = False
                self.data['testing'] = False
