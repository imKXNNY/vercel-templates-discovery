import json
import subprocess
import sys


def send_message(proc, message):
    data = json.dumps(message)
    encoded = data.encode("utf-8")
    header = f"Content-Length: {len(encoded)}\n\n".encode()
    proc.stdin.write(header)
    proc.stdin.write(encoded)
    proc.stdin.flush()


def read_message(proc):
    headers = {}
    while True:
        line = proc.stdout.readline()
        if not line:
            return None
        line = line.decode("utf-8").strip()
        if line == "":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
    length = int(headers.get("Content-Length", 0))
    if length:
        data = proc.stdout.read(length)
        return json.loads(data.decode("utf-8"))
    return None


def test_mcp_server_smoke():
    proc = subprocess.Popen(
        [sys.executable, "-m", "vercel_templates.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    # initialize
    send_message(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    msg = read_message(proc)
    assert msg is not None
    assert msg["id"] == 1
    assert msg["result"]["serverInfo"]["name"] == "vercel-templates-discovery"

    # tools/list
    send_message(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    msg = read_message(proc)
    assert msg is not None
    tool_names = [t["name"] for t in msg["result"]["tools"]]
    assert "search_templates" in tool_names
    assert "get_template" in tool_names
    assert "list_categories" in tool_names

    # search_templates
    send_message(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_templates",
                "arguments": {"query": "chatbot", "limit": 3},
            },
        },
    )
    msg = read_message(proc)
    assert msg is not None
    content = msg["result"]["content"][0]["text"]
    results = json.loads(content)
    assert len(results) <= 3

    # get_template
    send_message(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_template",
                "arguments": {"slug": "/templates/next.js/chatbot"},
            },
        },
    )
    msg = read_message(proc)
    assert msg is not None
    content = msg["result"]["content"][0]["text"]
    result = json.loads(content)
    assert result["slug"] == "/templates/next.js/chatbot"

    proc.stdin.close()
    proc.wait(timeout=5)
