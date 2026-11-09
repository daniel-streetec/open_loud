"""Local Fusion MCP client. Only localhost:27182; explicit read/run actions."""
import argparse
import json
from pathlib import Path
import urllib.request

URL = "http://127.0.0.1:27182/mcp"
ROOT = Path(__file__).resolve().parents[1]


def rpc(payload, session=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session:
        headers["MCP-Session-Id"] = session
    request = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=headers)
    response = urllib.request.urlopen(request, timeout=180)
    body = response.read()
    return (json.loads(body) if body else {}), response.headers.get("MCP-Session-Id")


def call(name, arguments):
    initialized, session = rpc({"jsonrpc":"2.0", "id":1, "method":"initialize", "params":{"protocolVersion":"2024-11-05", "capabilities":{}, "clientInfo":{"name":"open-loud", "version":"E02"}}})
    rpc({"jsonrpc":"2.0", "method":"notifications/initialized"}, session)
    result, _ = rpc({"jsonrpc":"2.0", "id":2, "method":"tools/call", "params":{"name":name,"arguments":arguments}}, session)
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action", choices=["read", "run", "inspect"])
    parser.add_argument("argument")
    args=parser.parse_args()
    if args.action == "read":
        result=call("fusion_mcp_read",json.loads(args.argument))
    else:
        path=(ROOT / args.argument).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Script must be inside repository")
        result=call("fusion_mcp_execute",{"featureType":"script","object":{"script":path.read_text(encoding="utf-8"),"readOnly":args.action=="inspect"}})
    print(json.dumps(result, ensure_ascii=True))
    nested=[]
    for item in result.get("result",{}).get("content",[]):
        if item.get("type")=="text":
            try: nested.append(json.loads(item["text"]))
            except (ValueError,KeyError): pass
    if "error" in result or result.get("result",{}).get("isError") or any(r.get("success") is False for r in nested):
        raise SystemExit(1)
