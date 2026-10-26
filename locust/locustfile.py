"""Cenários (variável de ambiente SCENARIO):
 1 = post com imagem ~1MB | 2 = post com texto ~400KB | 3 = post com imagem ~300KB
Cada usuário virtual abre o post e, nos cenários 1 e 3, baixa também a imagem (como um navegador)."""
import os
import re
from urllib.parse import urlparse

from locust import HttpUser, task, between

SCENARIO = os.getenv("SCENARIO", "1")
POSTS = {
    "1": "/?name=cenario-1-imagem-1mb",
    "2": "/?name=cenario-2-texto-400kb",
    "3": "/?name=cenario-3-imagem-300kb",
}
IMG_RE = re.compile(r'<img[^>]+src="([^"]*/wp-content/uploads/[^"]+)"')


class BlogReader(HttpUser):
    wait_time = between(1, 3)

    @task
    def read_post(self):
        html = ""
        with self.client.get(POSTS[SCENARIO], name=f"post (cenario {SCENARIO})",
                             catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
            else:
                html = resp.text
        if SCENARIO in ("1", "3") and html:
            m = IMG_RE.search(html)
            if m:
                self.client.get(urlparse(m.group(1)).path, name=f"imagem (cenario {SCENARIO})")
