from flask_migrate import Migrate
from app import create_application
from app.config import TestingConfig
from app.extensions import db

# ✅ Expose the Flask app instance at the top level
app = create_application(TestingConfig)
migrate = Migrate(app, db)

# ✅ Run only in local dev context
if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
