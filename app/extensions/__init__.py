from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger

# Instantiate extensions (to be initialized in app factory)
db = SQLAlchemy()
migrate = Migrate()
swagger = Swagger()
