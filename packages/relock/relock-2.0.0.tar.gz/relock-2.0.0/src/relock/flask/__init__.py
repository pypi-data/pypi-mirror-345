import os
import sys
import logging
import binascii
import bleach

logging = logging.getLogger(__name__)

from flask import (Blueprint,
				   current_app as app, 
				   has_request_context,
				   request,
				   session)

from flask_login import (current_user as worker,
						 user_logged_in,
					     user_logged_out,
					     user_loaded_from_cookie,
					     user_loaded_from_request,
					     user_login_confirmed,
					     user_unauthorized,
					     user_needs_refresh,
					     user_accessed,
					     session_protected)

from .login import AnonymousUserMixin

from ..tcp import TCP
from ..thread import Thread
from .device import Device

bp = os.environ.get('RELOCK_ROUTE', 'relock')
bp = Blueprint(bp, __name__, url_prefix='/%s' % bp,
							 template_folder='templates',
							 static_folder='static',
							 static_url_path='/static/%s' % bp)

class Flask(object):

	def __init__(self, app=None, host=None,
								 port=None,
								 pool=1,
								 ping=False,
								 timeout=30):
		if app is not None:
			self.init_app(app)
		self.tcp = None

	def init_app(self, app, add_context_processor=True):
		""" Configures an application. This registers an `before_request` call, and
			attaches this `Relock service` to it as `app.relock`.

			:param app: The :class:`flask.Flask` object to configure.
			:type app: :class:`flask.Flask`
			:param add_context_processor: Whether to add a context processor to
				the app that adds a `current_user` variable to the template.
				Defaults to ``True``.
			:type add_context_processor: bool
		"""
		app.relock = self

		if not hasattr(app, 'login_manager'):
			raise RuntimeError('Relock service requires Flask-Login to start first.')

		app.login_manager.anonymous_user = AnonymousUserMixin

		app.config.setdefault('RELOCK_SERVICE_HOST', str(os.environ.get('RELOCK_SERVICE_HOST', '127.0.0.1')))
		app.config.setdefault('RELOCK_SERVICE_PORT', int(os.environ.get('RELOCK_SERVICE_PORT', 8111)))
		app.config.setdefault('RELOCK_SERVICE_POOL', int(os.environ.get('RELOCK_SERVICE_POOL', 1)))
		app.config.setdefault('RELOCK_SERVICE_PING', bool(os.environ.get('RELOCK_SERVICE_PING', False)))
		app.config.setdefault('RELOCK_SERVICE_TIMEOUT', int(os.environ.get('RELOCK_SERVICE_TIMEOUT', 30)))

		with app.app_context():
			try:
				self.tcp = TCP(host=app.config.get('RELOCK_SERVICE_HOST'),
							   port=app.config.get('RELOCK_SERVICE_PORT'),
							   pool=app.config.get('RELOCK_SERVICE_POOL'),
							   ping=app.config.get('RELOCK_SERVICE_PING'),
							   timeout=app.config.get('RELOCK_SERVICE_TIMEOUT'))
			except (SystemExit, KeyboardInterrupt):
				sys.exit()
			except Exception as e:
				raise RuntimeError('Session Sentinel host is not available.')
			else:
				app.before_request(Device.before)
				app.after_request(Device.after)

				from .context import (x_key_xsid_processor,
									  x_key_screen_processor,
									  x_key_nonce_processor,
									  x_key_signature_processor,
									  x_key_credential_processor,
									  x_key_remote_addr_processor)
				from .routes import (exchange,
									 validate,
									 close,
									 clear)

				app.register_blueprint(bp)
				for p in app.url_map.iter_rules():
					if 'relock' in str(p) and ':' not in str(p):
						self.tcp.expose(str(p))

		self.tcp.expose('/')
