from main import create_app, db
from main.config import DeploymentConfig
from flask_migrate import Migrate

app = create_app(DeploymentConfig)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)
    