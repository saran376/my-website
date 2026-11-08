"""Vercel serverless endpoint: GET /api/health."""
import os
from http.server import BaseHTTPRequestHandler

from channel3_api import send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        send_json(self, 200, {"ok": True, "catalogConnected": bool(os.environ.get("CHANNEL3_API_KEY"))})

    def do_POST(self):
        self.send_response(405)
        self.send_header("Allow", "GET")
        self.end_headers()
