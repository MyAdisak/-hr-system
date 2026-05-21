#!/usr/bin/env python3
"""
Switch 2 AI sub-workflows from Anthropic Haiku → Google Gemma 3 27B IT (free).

Why Gemma instead of Gemini: this Google account's Gemini quota is 0,
but Gemma (open-source models served by same API) is accessible.

Targets:
  - 97lD7mqpfOyvuu6u : AI - Classify Intent
  - sF2057d0TJUkiTQT : AI - Format Thai

Constraints (Gemma vs Gemini):
  - No system_instruction support → fold system prompt into user message
  - No responseMimeType:application/json → rely on strict prompt + temperature 0.1

Idempotent: re-running on already-Gemma workflow leaves it the same.
"""
import json
import os
import sys
import urllib.request

API_KEY = os.environ.get("N8N_API_KEY")
if not API_KEY:
    sys.exit("N8N_API_KEY not set")

BASE = "http://hr_n8n:5678/api/v1"
MODEL = "gemma-3-27b-it"

TARGETS = {
    "97lD7mqpfOyvuu6u": {
        "name": "AI - Classify Intent (Gemma)",
        "instruction": (
            "You classify Thai HR LINE messages. "
            'Output ONLY a single JSON object on one line. No prose, no markdown, no code fences.\n'
            'Schema: {"intent": one of [check_in, check_out, leave_request, salary_inquiry, ot_request, register, help, unknown], '
            '"confidence": 0-1, "slots": object}'
        ),
        "max_tokens": 200,
        "user_field": "user_msg",
    },
    "sF2057d0TJUkiTQT": {
        "name": "AI - Format Thai (Gemma)",
        "instruction": (
            "You rewrite text into polite, concise Thai suitable for HR LINE replies. "
            'Output ONLY a single JSON object on one line. No prose, no markdown, no code fences.\n'
            'Schema: {"formatted": "..."}\n'
            "Respect tone and max_chars from input if provided."
        ),
        "max_tokens": 400,
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


def gemma_url():
    return f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def build_http_node(existing, cfg):
    user_field = cfg["user_field"]
    instruction_json = json.dumps(cfg["instruction"])
    # Combined user message: instruction + actual input separated by clear delimiter
    body_json = (
        "={\n"
        '  "contents": [{\n'
        '    "role": "user",\n'
        '    "parts": [{ "text": '
        + instruction_json
        + ' + "\\n\\nInput: " + JSON.stringify($json.'
        + user_field
        + ') + "\\n\\nJSON:" }]\n'
        "  }],\n"
        '  "generationConfig": {\n'
        f'    "maxOutputTokens": {cfg["max_tokens"]},\n'
        '    "temperature": 0.1\n'
        "  }\n"
        "}"
    )
    existing["parameters"] = {
        "method": "POST",
        "url": gemma_url(),
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
            "timeout": 20000,
        },
    }
    existing["name"] = "Gemma - " + (
        "Classify" if user_field == "user_msg" else "Format"
    )
    return existing


def patch_parse_node(node):
    # Gemma sometimes wraps JSON in code fences despite instructions — strip defensively
    node["parameters"]["jsCode"] = (
        "let raw = $input.first().json.candidates?.[0]?.content?.parts?.[0]?.text || '{}';\n"
        "raw = raw.trim();\n"
        "// Strip markdown code fences if present\n"
        "raw = raw.replace(/^```(?:json)?\\s*/i, '').replace(/```\\s*$/i, '').trim();\n"
        "let parsed;\n"
        "try { parsed = JSON.parse(raw); } catch (e) { parsed = { _raw: raw, _error: 'parse_failed' }; }\n"
        "return [{ json: parsed }];"
    )
    return node


def patch_workflow(wf_id, cfg):
    wf = http("GET", f"/workflows/{wf_id}")

    http_node = None
    parse_node = None
    for n in wf["nodes"]:
        if n["type"] == "n8n-nodes-base.httpRequest":
            http_node = n
        elif n["type"] == "n8n-nodes-base.code":
            # take the last code node — it's the output parser
            parse_node = n

    if not http_node or not parse_node:
        print(f"⚠️  {wf_id}: missing HTTP Request or Parse JSON node — skip")
        return

    old_http_name = http_node["name"]
    build_http_node(http_node, cfg)
    new_http_name = http_node["name"]
    patch_parse_node(parse_node)

    conns = wf["connections"]
    if old_http_name != new_http_name and old_http_name in conns:
        conns[new_http_name] = conns.pop(old_http_name)
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
