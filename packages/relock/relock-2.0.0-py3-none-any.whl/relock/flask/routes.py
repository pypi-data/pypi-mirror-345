from flask import (current_app as app, 
				   session, 
				   request, 
				   Response, 
				   url_for, 
				   json,
				   render_template, 
				   flash, 
				   jsonify, 
				   redirect, 
				   abort, 
				   make_response, 
				   session)

from flask_login import (current_user as worker, 
						 login_required)

from . import bp, logging

import bleach
import random, os
import time
import pickle
import base64
import hashlib
import binascii
import subprocess

from datetime import datetime
from datetime import timedelta
from jsmin import jsmin

from urllib.parse import urlparse

@bp.route('/remote', methods=['POST'])
def remote():
	""" This is a demo purpose only method. It should not be implemented 
		in production ready systems. The method when invoked (and should be
		invoked manually) emulates the behavior of stolen keys attack.

		This route is invoked by a user manually by a pressing the button
		inside the demo application.
	"""
	if response := request.device.remote():
		return response
	return dict()

@bp.route('/register', methods=['POST'])
def register():
	""" This method is invoked by a javascript component when the user
		is trying to register the passkey. The credential is passed from
		request directly to relock service.
	"""
	if request.method == 'POST' and request.json.get('credential'):
		return request.device.webauthn(request.json)
	return request.device.webauthn()

@bp.route('/authenticate', methods=['POST'])
def authenticate():
	""" This method is invoked by a javascript component when the user
		is trying to authenticate using passkey.
	"""
	if request.method == 'POST' and 'credential' in request.json:
		return request.device.authenticate(request.json.get('credential'))
	return request.device.authenticate()

@bp.route("/screen", methods=['POST'])
def screen(token=None):
	""" This method is invoked by the browser side javascript automatically, 
		when the user starts a new tab in session.

		request.form.get('screen', str()),
		request.form.get('origin', str()),
		request.form.get('path', str())
		request.form.get('wrong', str())
	"""
	return ('', 204)

@bp.route("/close", methods=['POST'])
def close(token=None, delay=1.5):
	""" This method is invoked by the browser at he moment of website 
		beeing unloaded from the browser tab. The browser sends a hash
		specyfic to the closed tab, if this is a last tab on browser 
		side the server will close a session and logout a user.
	"""
	with app.app_context():
		request.device.close(request.form.get('screen', str()),
							 request.form.get('origin', str()),
							 request.form.get('path', str()))
	return ('', 204)

@bp.route("/exchange", methods=['POST'])
def exchange():
	""" This method is invoked by javascript at the moment when the browser
		has no registered keys for the domain. Before establish of trust the 
		browser and the server need to agree the secret material of the key.
		This process is one-time action unless the keys are not erased for 
		some reasons.
	"""
	if not isinstance(request.json.get('key'), list):
		return dict(error='The key should be an list of bytes')
	if not isinstance(request.json.get('hash'), list):
		return dict(error='The hash should be an list of bytes')
	if keys := request.device.exchange(bytes(request.json.get('key')),
									   bytes(request.json.get('hash')),
									   bytes(request.json.get('xsid')),
									   bytes(request.json.get('screen'))):
		return keys
	return dict(error='Key agreement failure.')

@bp.route("/validate", methods=['POST'])
def validate(token=None, signature=None):
	""" This route is invoked by a browser every time when the transient
		has been rotated and/or whenever the confirmation of the keys is
		needed. The parameters passed in headers and as a json message
		are passed directly to the device object in the application and 
		next by a SDK connector to the relock service.
	"""
	if keys := request.device.validate(request.json.get('screen', str()),
									   request.json.get('nonce', str()),
									   request.headers.get('X-Key-Token', str()),
									   request.headers.get('X-Key-Signature', str())):
		return keys
	return dict(status=False)

@bp.route('/relock.js', methods=['GET'])
def js(minified=True):
	""" The route is invoked by a browser. To reduce the processing time
		the compiled data from the relock service are assigned to the 
		object in the current server process. Local data are modyficated 
		only when server-side returns different checksum of the compiled
		javascript file.
	"""
	with app.app_context():
		if response := request.device.js(id=app.extensions.get('relock_id', bytes()),
										 minified=True,
										 debug=app.config.get('DEBUG'),
										 host=app.config.get('SERVER_HOST')):
			if app.extensions.get('relock_id') != response.get('id'):
				app.extensions['relock_js'] = response.get('js')
				app.extensions['relock_id'] = response.get('id')
	return Response(app.extensions.get('relock_js'), status=200, 
													 content_type='text/javascript; charset=utf-8')

@bp.route("/clear", methods=['POST', 'GET'])
def clear():
	""" This method is invoked by a browser javascript at the moment of 
		the failure of key agreement process. If invoked it will erase
		all information about device from server repository.
	"""
	if response := request.device.clear():
		return dict()
	return dict()