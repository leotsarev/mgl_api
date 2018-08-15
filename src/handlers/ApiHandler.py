import json
from json import JSONDecodeError

import os
from services.db import DB
from services.misc import api_fail, get_logger
from tornado.web import RequestHandler


error_logger = get_logger(__name__, 'logs/api_errors.log')
logger = get_logger(__name__, 'logs/api_posts.log')


class DefaultHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Access-Control-Allow-Headers",
                        "x-requested-with,access-control-allow-origin,authorization,content-type")

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class ApiHandler(DefaultHandler):
    func = None

    def initialize(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.db = DB()

    def get_exception_text(self, e, data):
        return ''

    async def post(self):
        try:
            body = self.request.body or "{}"
            logger.info(body)
            try:
                req = json.loads(body)
            except JSONDecodeError:
                out = api_fail("JSON-запрос невалиден")
            else:
                out = self.func(self, req)
            self.write(json.dumps(out, indent=4))
        except Exception as e:
            err_text = self.get_exception_text(self, e)
            msg = e.sql if hasattr(e, 'sql') else str(type(e)) + ":" + str(e)
            data = e.data if hasattr(e, 'data') else ''
            fail_args = {"msg": err_text} if err_text else {"args": e.args, "msg": msg, "data": data}
            error_logger.error("======================================================================")
            error_logger.info(body)
            error_logger.exception(msg, exc_info=e)

            self.write(json.dumps(api_fail(**fail_args)))


class LogsHandler(DefaultHandler):
    async def get(self):
        args = {key: val[0].decode() for key, val in self.request.arguments.items()}
        if 'log' in args:
            self.write("<xmp>"+open("logs/"+args['log']+".log").read()+"</xmp>")
        if 'clear' in args:
            os.unlink("logs/"+args['clear']+".log")