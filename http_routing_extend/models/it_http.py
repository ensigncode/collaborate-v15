# -*- coding: utf-8 -*-

import logging
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls
from odoo.tools import config, ustr, pycompat

try:
	import slugify as slugify_lib
except ImportError:
	slugify_lib = None

from odoo.addons.http_routing.models import ir_http
from odoo.addons.http_routing.models.ir_http import is_multilang_url

from odoo import api, models, registry, exceptions, tools, http
from odoo.http import request

_logger = logging.getLogger(__name__)


def url_lang(path_or_uri, lang_code=None):
	'''
		Override this method to change the condition while popping out the default language code,
		Change: Line no: 50
			Removed else if condition to make sure that it will not be removed from URL even if it's default language
    '''
	Lang = request.env['res.lang']
	location = pycompat.to_text(path_or_uri).strip()
	force_lang = lang_code is not None
	try:
		url = werkzeug.urls.url_parse(location)
	except ValueError:
		# e.g. Invalid IPv6 URL, `werkzeug.urls.url_parse('http://]')`
		url = False
	# relative URL with either a path or a force_lang
	if url and not url.netloc and not url.scheme and (url.path or force_lang):
		location = werkzeug.urls.url_join(request.httprequest.path, location)
		lang_url_codes = [url_code for _, url_code, *_ in Lang.get_available()]
		lang_code = pycompat.to_text(lang_code or request.context['lang'])
		lang_url_code = Lang._lang_code_to_urlcode(lang_code)
		lang_url_code = lang_url_code if lang_url_code in lang_url_codes else lang_code
		if (len(lang_url_codes) > 1 or force_lang) and is_multilang_url(location, lang_url_codes):
			loc, sep, qs = location.partition('?')
			ps = loc.split(u'/')
			if ps[1] in lang_url_codes:
				# Replace the language only if we explicitly provide a language to url_for
				if force_lang:
					ps[1] = lang_url_code
			# check the language code is already there or not, if not then add it here
			elif not any([code in ps for code in lang_url_codes]):
				ps.insert(1, lang_url_code)

			location = u'/'.join(ps) + sep + qs
	return location


# Monkey patching
ir_http.url_lang = url_lang


class IrHttp(models.AbstractModel):
	_inherit = 'ir.http'

	@classmethod
	def _dispatch(cls):
		"""
			Override to force language to be appeared event if it's default language,
			Changes:
				line no: 82, set this variable to False.
		"""
		request.routing_iteration = getattr(request, 'routing_iteration', 0) + 1

		func = None
		routing_error = None
		# handle // in url
		if request.httprequest.method == 'GET' and '//' in request.httprequest.path:
			new_url = request.httprequest.path.replace('//', '/') + '?' + request.httprequest.query_string.decode(
				'utf-8')
			return request.redirect(new_url, code=301)

		# locate the controller method
		try:
			rule, arguments = cls._match(request.httprequest.path)
			func = rule.endpoint
			request.is_frontend = func.routing.get('website', False)
		except werkzeug.exceptions.NotFound as e:
			# either we have a language prefixed route, either a real 404
			# in all cases, website processes them exept if second element is static
			# Checking static will avoid to generate an expensive 404 web page since
			# most of the time the browser is loading and inexisting assets or image. A standard 404 is enough.
			# Earlier check would be difficult since we don't want to break data modules
			path_components = request.httprequest.path.split('/')
			request.is_frontend = len(path_components) < 3 or path_components[2] != 'static' or '.' not in \
			                      path_components[-1]
			routing_error = e

		request.is_frontend_multilang = not func or (
				func and request.is_frontend and func.routing.get('multilang', func.routing['type'] == 'http'))

		# check authentication level
		try:
			if func:
				cls._authenticate(func)
			elif request.uid is None and request.is_frontend:
				cls._auth_method_public()
		except Exception as e:
			return cls._handle_exception(e)

		cls._geoip_setup_resolver()
		cls._geoip_resolve()

		# For website routes (only), add website params on `request`
		if request.is_frontend:
			cls._add_dispatch_parameters(func)

			path = request.httprequest.path.split('/')
			default_lg_id = cls._get_default_lang()
			if request.routing_iteration == 1:
				is_a_bot = cls.is_a_bot()
				nearest_lang = not func and cls.get_nearest_lang(request.env['res.lang']._lang_get_code(path[1]))
				url_lg = nearest_lang and path[1]

				# The default lang should never be in the URL, and a wrong lang
				# should never be in the URL.
				wrong_url_lg = False
				# The lang is missing from the URL if multi lang is enabled for
				# the route and the current lang is not the default lang.
				# POST requests are excluded from this condition.
				missing_url_lg = not url_lg and request.is_frontend_multilang and request.lang != default_lg_id and request.httprequest.method != 'POST'
				# Bots should never be redirected when the lang is missing
				# because it is the only way for them to index the default lang.
				if wrong_url_lg or (missing_url_lg and not is_a_bot):
					if url_lg:
						path.pop(1)
					if request.lang != default_lg_id:
						path.insert(1, request.lang.url_code)
					path = '/'.join(path) or '/'
					routing_error = None
					redirect = request.redirect(path + '?' + request.httprequest.query_string.decode('utf-8'))
					redirect.set_cookie('frontend_lang', request.lang.code)
					return redirect
				elif url_lg:
					request.uid = None
					if request.httprequest.path == '/%s/' % url_lg:
						# special case for homepage controller, mimick `_postprocess_args()` redirect
						path = request.httprequest.path[:-1]
						if request.httprequest.query_string:
							path += '?' + request.httprequest.query_string.decode('utf-8')
						return request.redirect(path, code=301)
					path.pop(1)
					routing_error = None
					return cls.reroute('/'.join(path) or '/')
				elif missing_url_lg and is_a_bot:
					# Ensure that if the URL without lang is not redirected, the
					# current lang is indeed the default lang, because it is the
					# lang that bots should index in that case.
					request.lang = default_lg_id
					request.context = dict(request.context, lang=default_lg_id.code)

			if request.lang == default_lg_id:
				context = dict(request.context)
				context['edit_translations'] = False
				request.context = context

		if routing_error:
			return cls._handle_exception(routing_error)

		# removed cache for auth public
		result = super(IrHttp, cls)._dispatch()

		cook_lang = request.httprequest.cookies.get('frontend_lang')
		if request.is_frontend and cook_lang != request.lang._get_cached('code') and hasattr(result, 'set_cookie'):
			result.set_cookie('frontend_lang', request.lang._get_cached('code'))

		return result
