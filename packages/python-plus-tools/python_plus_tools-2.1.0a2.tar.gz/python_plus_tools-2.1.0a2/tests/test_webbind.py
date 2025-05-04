import http.server
import socketserver
from multiprocessing import Process
import os
import webbrowser


def _run_server(html_path, port, auto_open):
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/":
                try:
                    with open(html_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_error(404, f"File not found: {html_path}")
            else:
                self.send_error(404, "Page not found")

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving {html_path} at http://127.0.0.1:{port}")
        if auto_open:
            webbrowser.open(f"http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def serve_html(html_path, port, background=True, auto_open=False):
    html_path = os.path.abspath(html_path)

    if background:
        process = Process(target=_run_server, args=(html_path, port, auto_open))
        process.start()
        return process
    else:
        _run_server(html_path, port, auto_open)
