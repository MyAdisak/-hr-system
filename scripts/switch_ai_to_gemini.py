#!/usr/bin/env python3
"""
Switch 2 AI sub-workflows from Anthropic Haiku → Google Gemini 2.0 Flash (free tier).

Targets:
  - 97lD7mqpfOyvuu6u : AI - Classify Intent (Haiku)
  - sF2057d0TJUkiTQT : AI - Format Thai (Haiku)

Replaces:
  - HTTP Request URL, headers, body (Anthropic → Gemini)
  - Parse JSON code (content[0].text → candidates[0].content.parts[0].text)
  - Workflow name (Haiku → Gemini)

Idempotent: re-running on already-Gemini workflow leaves it the same.
"""
import json
import os
import sys
import urllib.request

API_KEY = os.environ.get("N8N_API_KEY")
if not API_KEY:
    sys.exit("N8N_API_KEY not set")

BASE = "http://hr_n8n:5678/api/v1"
GEMINI_MODEL = "gemini-2.0-flash"

# Per-workflow config: id, new name, system prompt, max_tokens
TARGETS = {
    "97lD7mqpfOyvuu6u": {
        "name": "AI - Classify Intent (Gemini)",
        "system": (
            "You classify Thai HR LINE messages. "
            'Return ONLY JSON: {"intent": one of [check_in, check_out, leave_request, '
            'salary_inquiry, ot_request, register, help, unknown], '
            '"confidence": 0-1, "slots": object}. No prose, no markdown.'
        ),
        "max_tokens": 256,
        "user_field": "user_msg",
    },
    "sF2057d0TJUkiTQT": {
        "name": "AI - Format Thai (Gemini)",
        "system": (
            "You rewrite text into polite, concise Thai suitable for HR LINE replies. "
            'Return ONLY JSON: {"formatted": "..."}. Respect tone and max_chars from input.'
        ),
        "max_tokens": 512,
        "user_field": "raw_text",
    },
}


def http(method, path, body=None):
    req = urllib.request.Request(
        f"{BASE}{path}",
        method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"},
    )
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def gemini_url():
    # API key passed via header (x-goog-api-key) instead of URL query for cleanliness
    return f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def build_http_node(existing, cfg):
    """Replace existing HTTP Request node parameters with Gemini equivalents."""
    body_json = (
        "={\n"
        '  "system_instruction": { "parts": [{"text": ' + json.dumps(cfg["system"]) + " }] },\n"
        '  "contents": [\n'
        '    { "role": "user", "parts": [{"text": {{ JSON.stringify($json.' + cfg["user_field"] + ") }}}] }\n"
        "  ],\n"
        '  "generationConfig": {\n'
        '    "responseMimeType": "application/json",\n'
        f'    "maxOutputTokens": {cfg["max_tokens"]}\n'
        "  }\n"
        "}"
    )
    existing["parameters"] = {
        "method": "POST",
        "url": gemini_url(),
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "content-type", "value": "application/json"},
                {"name": "x-goog-api-key", "value": "={{ $env.GEMINI_API_KEY }}"},
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": body_json,
        "options": {
            "response": {"response": {"responseFormat": "json"}},
            "timeout": 15000,
        },
    }
    existing["name"] = "Gemini Flash - " + (
        "Classify" if cfg["user_field"] == "user_msg" else "Format"
    )
    return existing


def patch_parse_node(node):
    node["parameters"]["jsCode"] = (
        "const raw = $input.first().json.candidates?.[0]?.content?.parts?.[0]?.text || '{}';\n"
        "let parsed;\n"
        "try { parsed = JSON.parse(raw); } catch (e) { parsed = { _raw: raw, _error: 'parse_failed' }; }\n"
        "return [{ json: parsed }];"
    )
    return node


def patch_workflow(wf_id, cfg):
    wf = http("GET", f"/workflows/{wf_id}")

    # Find HTTP node (Anthropic or already Gemini) and Parse JSON node
    http_node = None
    parse_node = None
    for n in wf["nodes"]:
        if n["type"] == "n8n-nodes-base.httpRequest":
            http_node = n
        elif n["name"] == "Parse JSON":
            parse_node = n

    if not http_node or not parse_node:
        print(f"⚠️  {wf_id}: missing HTTP Request or Parse JSON node — skip")
        return

    old_http_name = http_node["name"]
    build_http_node(http_node, cfg)
    new_http_name = http_node["name"]
    patch_parse_node(parse_node)

    # Update connections if HTTP node renamed
    conns = wf["connections"]
    if old_http_name != new_http_name and old_http_name in conns:
        conns[new_http_name] = conns.pop(old_http_name)
    # Also update upstream node pointing to old HTTP name
    for src, payload in conns.items():
        for outs in payload.get("main", []):
            for c in outs:
                if c.get("node") == old_http_name:
                    c["node"] = new_http_name

    wf["name"] = cfg["name"]

    allowed = {"name", "nodes", "connections", "settings", "staticData"}
    payload = {k: v for k, v in wf.items() if k in allowed}
    result = http("PUT", f"/workflows/{wf_id}", payload)
    print(f"✅ {wf_id} → '{result['name']}' (HTTP node: {new_http_name})")


for wf_id, cfg in TARGETS.items():
    patch_workflow(wf_id, cfg)
