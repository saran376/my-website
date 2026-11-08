"""Private server-side client for CartPal's Channel3 product search."""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.trychannel3.com"


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def _headers(user_id=""):
    api_key = os.environ.get("CHANNEL3_API_KEY", "").strip()
    if not api_key:
        raise ApiError(
            503,
            "Product search is not configured. Add CHANNEL3_API_KEY in Vercel Project Settings → Environment Variables.",
        )
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if isinstance(user_id, str) and re.fullmatch(r"[a-zA-Z0-9._@-]{1,128}", user_id):
        headers["x-user-id"] = user_id
    return headers


def _request(url, headers, payload=None, timeout=20):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read(2_000_000))
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            raise ApiError(502, "Live product search could not authenticate. Check CHANNEL3_API_KEY in Vercel settings.")
        if error.code == 429:
            raise ApiError(429, "Product search is temporarily busy. Please try again shortly.")
        raise ApiError(502, "The live product catalog could not complete this request. Please try again.")
    except urllib.error.URLError:
        raise ApiError(502, "The live product catalog could not be reached. Please try again.")
    except TimeoutError:
        raise ApiError(504, "Product search took too long. Please try again.")
    except (ValueError, json.JSONDecodeError):
        raise ApiError(502, "The live product catalog returned an unreadable response.")


def search_products(query, max_price=None, retailer_domain="", user_id=""):
    payload = {"query": query, "config": {"mode": "agentic"}, "limit": 12}
    filters = {}
    if isinstance(max_price, (int, float)) and 0 < max_price <= 100000:
        filters["price"] = {"max_price": max_price}
    if isinstance(retailer_domain, str):
        domain = retailer_domain.strip().lower()
        if domain and re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,116}[a-z0-9])?\.[a-z]{2,24}", domain):
            filters["website_ids"] = [domain]
    if filters:
        payload["filters"] = filters
    result = _request(BASE_URL + "/v1/search", _headers(user_id), payload, timeout=30)
    products = result.get("products", result.get("data", result.get("items", []))) if isinstance(result, dict) else []
    if not isinstance(products, list):
        products = []
    return {"products": products, "count": len(products), "source": "live"}


def get_product(product_id, user_id=""):
    if not isinstance(product_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", product_id):
        raise ApiError(400, "That product identifier is invalid.")
    product = _request(
        BASE_URL + "/v1/products/" + urllib.parse.quote(product_id, safe=""),
        _headers(user_id),
        timeout=15,
    )
    return {"product": product}


def read_body(handler):
    try:
        size = int(handler.headers.get("Content-Length", "0"))
    except (TypeError, ValueError):
        size = 0
    if size < 1 or size > 16384:
        raise ApiError(413, "Search request is too large.")
    try:
        body = json.loads(handler.rfile.read(size))
    except (ValueError, json.JSONDecodeError):
        raise ApiError(400, "We could not read that request. Please try again.")
    if not isinstance(body, dict):
        raise ApiError(400, "We could not read that request. Please try again.")
    return body


def send_json(handler, status, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def user_id(handler):
    return handler.headers.get("X-CartPal-User", "")
