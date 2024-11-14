from flask import Blueprint
from flask_restx import Api

from secret import ROOT_PATH_PREFIX

blueprint = Blueprint('apis', __name__, url_prefix=ROOT_PATH_PREFIX)

api = Api(version="1.0",
          title="TopTable Staff API",
          description="TopTable API for the staff side",
          prefix=ROOT_PATH_PREFIX,
          doc=f'{ROOT_PATH_PREFIX}' )

from .auth import api as api_auth
from .layout import api as api_layout
from.ui import api as api_ui
from .upload import api as api_upload

api.add_namespace(api_auth)
api.add_namespace(api_layout)
api.add_namespace(api_ui)
api.add_namespace(api_upload)