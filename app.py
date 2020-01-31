from flask_restful import Api
from blueprints import app, manager
import logging, sys
from logging.handlers import RotatingFileHandler


from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

api = Api(app, catch_all_404s=True)


if __name__ == '__main__':
    ## run manage
    try:
        if sys.argv[1] == 'db':
            manager.run()
    
    except Exception as e:
        
        formatter = logging.Formatter(
            "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
        )
        
        log_handler = logging.handlers.RotatingFileHandler(
            "%s/%s" %(app.root_path, '../storage/log/app.log'),maxBytes=10000, backupCount=10
        ) 

        logging.getLogger().setLevel('INFO')

        log_handler.setFormatter(formatter)
        app.logger.addHandler(log_handler)

        app.run(debug=False, host='0.0.0.0', port=5000)