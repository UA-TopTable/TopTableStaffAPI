from flask import Blueprint
from flask_restx import Api

blueprint = Blueprint('apis', __name__)

api = Api(version="1.0",title="TopTable Staff API",description="TopTable API for the staff side",prefix="/api/v1")

from .auth import api as api_auth
from .layout import api as api_layout

api.add_namespace(api_auth)
api.add_namespace(api_layout)