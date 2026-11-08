"""Vercel serverless endpoint: GET /api/product?id=PRODUCT_ID."""
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from channel3_api import ApiError, get_product, send_json, user_id


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        product_id = parse_qs(urlparse(self.path).query).get("id", [""])[0]
        try:
            result = get_product(product_id, user_id(self))
            send_json(self, 200, result)
        except ApiError as error:
            send_json(self, error.status, {"error": error.message})
        except Exception:
            send_json(self, 500, {"error": "Could not refresh this product. Search for it again."})

    def do_POST(self):
        self.send_response(405)
        self.send_header("Allow", "GET")
        self.end_headers()
