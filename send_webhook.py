import requests
import json

# Simulate push event
push_payload = {
    "ref": "refs/heads/main",
    "pusher": {"name": "Travis"},
    "head_commit": {"timestamp": "2025-07-01T12:45:00Z"}
}

# Simulate pull request
pull_payload = {
    "action": "opened",
    "pull_request": {
        "user": {"login": "Travis"},
        "head": {"ref": "staging"},
        "base": {"ref": "master"},
        "created_at": "2025-07-01T12:30:00Z"
    }
}

# Simulate merge (closed + merged)
merge_payload = {
    "action": "closed",
    "pull_request": {
        "user": {"login": "Travis"},
        "head": {"ref": "dev"},
        "base": {"ref": "master"},
        "created_at": "2025-07-01T12:00:00Z",
        "merged": True
    }
}

headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "pull_request"
}

response = requests.post("http://127.0.0.1:5000/webhook", headers=headers, data=json.dumps(merge_payload))
print("Status:", response.status_code)
print(response.text)
