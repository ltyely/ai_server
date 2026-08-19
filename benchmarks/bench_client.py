#!/usr/bin/env python3
"""简单的 OpenAI 兼容 API 客户端，用于 benchmark。"""
import json
import time
import urllib.request
from typing import Optional


class ChatClient:
    def __init__(self, base_url: str, model: str, api_key: str = "your-api-key"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def chat(self, messages, temperature: float = 0.4, max_tokens: int = 512, stream: bool = False, extra_body: Optional[dict] = None):
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if extra_body:
            payload.update(extra_body)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        start = time.time()
        with urllib.request.urlopen(req, timeout=1200) as resp:
            body = resp.read().decode("utf-8")
        elapsed = time.time() - start
        result = json.loads(body)
        content = result["choices"][0]["message"].get("content", "")
        usage = result.get("usage", {})
        return {
            "content": content,
            "elapsed": elapsed,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    def is_ready(self, timeout: float = 2.0):
        url = f"{self.base_url}/v1/models"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False
