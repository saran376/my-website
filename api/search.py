"""Vercel serverless endpoint: POST /api/search."""
from http.server import BaseHTTPRequestHandler

from channel3_api import ApiError, read_body, search_products, send_json, user_id


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            body = read_body(self)
            query = body.get("query")
            if not isinstance(query, str) or not query.strip() or len(query) > 500:
                raise ApiError(400, "Enter what you are looking for (up to 500 characters).")
            result = search_products(
                query.strip(),
                body.get("maxPrice"),
                body.get("retailerDomain", ""),
                user_id(self),
            )
            send_json(self, 200, result)
        except ApiError as error:
            send_json(self, error.status, {"error": error.message})
        except Exception:
            send_json(self, 500, {"error": "Something went wrong while searching. Please try again."})

    def do_GET(self):
        self.send_response(405)
        self.send_header("Allow", "POST")
        self.end_headers()
