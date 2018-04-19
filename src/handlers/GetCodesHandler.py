import json

from tornado.httpclient import AsyncHTTPClient, HTTPClient, HTTPError
from tornado.web import RequestHandler


class GetCodeAsyncHandler(RequestHandler):
    async def post(self):
        res = {}
        http_client = AsyncHTTPClient()
        urls_to_check = json.loads(self.request.body)
        for url in urls_to_check:
            try:
                response = await http_client.fetch(url)
                res[url] = response.code
            except HTTPError as e:
                res[url] = e.code
            except Exception as e:
                res[url] = str(e)
        self.write(json.dumps(res))

# class GetCodeHandler(RequestHandler):
#     def post(self):
#         http_client = HTTPClient()
#         try:
#             response = http_client.fetch("http://www.google.com/")
#             print(response.body)
#         except HTTPError as e:
#             # HTTPError is raised for non-200 responses; the response
#             # can be found in e.response.
#             print("Error: " + str(e))
#         except Exception as e:
#             # Other errors are possible, such as IOError.
#             print("Error: " + str(e))
#         http_client.close()
