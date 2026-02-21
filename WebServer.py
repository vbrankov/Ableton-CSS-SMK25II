"""Simple HTTP server for serving status page to browsers."""

import threading
import json
try:
    # Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
except ImportError:
    # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn


class WebServer:
    """HTTP server that serves status page and provides JSON API."""

    def __init__(self, port, controller, log_func):
        """Initialize web server.

        Args:
            port: Port to listen on
            controller: Reference to MyController instance
            log_func: Logging function
        """
        self._port = port
        self._controller = controller
        self._log = log_func
        self._server = None
        self._thread = None
        self._running = False

    def start(self):
        """Start the web server in a background thread."""
        if self._running:
            return

        try:
            # Create request handler with access to controller
            handler = self._make_handler()

            # Create HTTP server
            self._server = ThreadedHTTPServer(('0.0.0.0', self._port), handler)
            self._running = True

            # Start server in background thread
            self._thread = threading.Thread(target=self._server.serve_forever)
            self._thread.daemon = True  # Thread dies when main program exits
            self._thread.start()

            self._log(f"Web server started on port {self._port}")
            self._log(f"Open http://YOUR_PC_IP:{self._port} in browser")
        except Exception as e:
            self._log(f"ERROR starting web server: {e}")
            self._running = False

    def stop(self):
        """Stop the web server."""
        if not self._running:
            return

        try:
            self._running = False
            if self._server:
                self._server.shutdown()
                self._server.server_close()
            self._log("Web server stopped")
        except Exception as e:
            self._log(f"ERROR stopping web server: {e}")

    def _make_handler(self):
        """Create request handler class with access to controller."""
        controller = self._controller
        log = self._log

        class RequestHandler(BaseHTTPRequestHandler):
            """HTTP request handler."""

            def log_message(self, format, *args):
                """Override to use our logging."""
                pass  # Suppress default HTTP logging

            def do_GET(self):
                """Handle GET requests."""
                try:
                    if self.path == '/' or self.path == '/index.html':
                        self._serve_reference()
                    elif self.path == '/status':
                        self._serve_status()
                    elif self.path == '/events':
                        self._serve_events()
                    elif self.path == '/modes':
                        self._serve_modes_data()
                    elif self.path == '/manifest.json':
                        self._serve_manifest()
                    elif self.path == '/sw.js':
                        self._serve_service_worker()
                    else:
                        self.send_error(404, "Not Found")
                except Exception as e:
                    log(f"ERROR handling request: {e}")
                    self.send_error(500, str(e))

            def _serve_html(self):
                """Serve the main HTML page."""
                html = self._get_html()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(html))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))

            def _serve_reference(self):
                """Serve the reference page."""
                html = self._get_reference_html()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(html))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))

            def _serve_status(self):
                """Serve JSON status."""
                status = self._get_status()
                json_data = json.dumps(status)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(json_data))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json_data.encode('utf-8'))

            def _serve_modes_data(self):
                """Serve mode reference data as JSON."""
                from .ModeReference import ModeReference
                modes_data = ModeReference.MODES
                json_data = json.dumps(modes_data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(json_data))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json_data.encode('utf-8'))

            def _serve_manifest(self):
                """Serve manifest.json for PWA."""
                import os
                script_dir = os.path.dirname(os.path.abspath(__file__))
                manifest_path = os.path.join(script_dir, 'manifest.json')
                try:
                    with open(manifest_path, 'r') as f:
                        manifest_data = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(manifest_data))
                    self.end_headers()
                    self.wfile.write(manifest_data.encode('utf-8'))
                except Exception as e:
                    log(f"ERROR loading manifest: {e}")
                    self.send_error(404, "Manifest not found")

            def _serve_service_worker(self):
                """Serve service worker for PWA."""
                import os
                script_dir = os.path.dirname(os.path.abspath(__file__))
                sw_path = os.path.join(script_dir, 'sw.js')
                try:
                    with open(sw_path, 'r') as f:
                        sw_data = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/javascript')
                    self.send_header('Content-Length', len(sw_data))
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self.wfile.write(sw_data.encode('utf-8'))
                except Exception as e:
                    log(f"ERROR loading service worker: {e}")
                    self.send_error(404, "Service worker not found")

            def _serve_events(self):
                """Serve Server-Sent Events stream for real-time updates."""
                import time

                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.end_headers()

                last_status = None

                try:
                    while True:
                        # Get current status
                        status = self._get_status()
                        status_json = json.dumps(status)

                        # Only send if changed
                        if status_json != last_status:
                            # Send SSE message
                            self.wfile.write(f"data: {status_json}\n\n".encode('utf-8'))
                            self.wfile.flush()
                            last_status = status_json

                        # Check every 50ms
                        time.sleep(0.05)

                except (BrokenPipeError, ConnectionResetError):
                    # Client disconnected
                    pass
                except Exception as e:
                    log(f"ERROR in SSE stream: {e}")

            def _get_status(self):
                """Get current controller status as dict."""
                return controller.get_status()

            def _get_reference_html(self):
                """Get reference page HTML."""
                import os
                # Read template file
                script_dir = os.path.dirname(os.path.abspath(__file__))
                template_path = os.path.join(script_dir, 'reference_template.html')
                try:
                    with open(template_path, 'r') as f:
                        return f.read()
                except Exception as e:
                    log(f"ERROR loading reference template: {e}")
                    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMK25II Reference - Session Mode</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #000;
            color: #fff;
            overflow: hidden;
        }
        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 10px;
        }
        .header {
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            color: #ff5555;
        }
        .main {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 10px;
            flex: 1;
        }
        .section {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            overflow-y: auto;
        }
        .section h2 {
            font-size: 20px;
            margin-bottom: 15px;
            color: #00ff88;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 8px;
        }
        .knob, .pad-row {
            background: #2a2a2a;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .knob-num, .pad-num {
            background: #00ff88;
            color: #000;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            min-width: 40px;
            text-align: center;
            margin-right: 12px;
        }
        .knob-desc, .pad-desc {
            flex: 1;
        }
        .knob-name, .pad-name {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 2px;
        }
        .knob-detail, .pad-detail {
            font-size: 12px;
            color: #aaa;
        }
        .pad-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 4px;
            margin-bottom: 15px;
        }
        .pad-cell {
            background: #2a2a2a;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            font-size: 11px;
        }
        .pad-cell.clip {
            background: #1a3a2a;
            border: 2px solid #00ff88;
        }
        .pad-cell.scene {
            background: #3a1a1a;
            border: 2px solid #ff5555;
        }
        .pad-legend {
            background: #2a2a2a;
            padding: 12px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 12px;
        }
        .legend-color {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 2px;
            margin-right: 6px;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>0. Session Mode</h1>
        </div>
        <div class="main">
            <div class="section">
                <h2>Knobs (8)</h2>
                <div class="knob">
                    <div class="knob-num">K0</div>
                    <div class="knob-desc">
                        <div class="knob-name">Scroll Horizontal</div>
                        <div class="knob-detail">Move session box left/right</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K1</div>
                    <div class="knob-desc">
                        <div class="knob-name">Scroll Vertical</div>
                        <div class="knob-detail">Move session box up/down</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K2</div>
                    <div class="knob-desc">
                        <div class="knob-name">Pad Mode</div>
                        <div class="knob-detail">0=Play/Stop, 1=Stop Only, 2=Record</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K3</div>
                    <div class="knob-desc">
                        <div class="knob-name">Quantization</div>
                        <div class="knob-detail">Adjust clip trigger quantization</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K4</div>
                    <div class="knob-desc">
                        <div class="knob-name">Tempo</div>
                        <div class="knob-detail">Adjust BPM (20-999)</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K5</div>
                    <div class="knob-desc">
                        <div class="knob-name">Metronome</div>
                        <div class="knob-detail">Right=ON, Left=OFF</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K6</div>
                    <div class="knob-desc">
                        <div class="knob-name">Master Volume</div>
                        <div class="knob-detail">Adjust master track volume</div>
                    </div>
                </div>
                <div class="knob">
                    <div class="knob-num">K7</div>
                    <div class="knob-desc">
                        <div class="knob-name">Undo/Redo</div>
                        <div class="knob-detail">Left=Undo, Right=Redo</div>
                    </div>
                </div>
            </div>
            <div class="section">
                <h2>Pads (16) - 7×2 Clip Grid + Scene Launch</h2>
                <div class="pad-grid">
                    <div class="pad-cell clip">Clip<br/>T1S1</div>
                    <div class="pad-cell clip">Clip<br/>T2S1</div>
                    <div class="pad-cell clip">Clip<br/>T3S1</div>
                    <div class="pad-cell clip">Clip<br/>T4S1</div>
                    <div class="pad-cell clip">Clip<br/>T5S1</div>
                    <div class="pad-cell clip">Clip<br/>T6S1</div>
                    <div class="pad-cell clip">Clip<br/>T7S1</div>
                    <div class="pad-cell scene">Scene<br/>1</div>
                    <div class="pad-cell clip">Clip<br/>T1S2</div>
                    <div class="pad-cell clip">Clip<br/>T2S2</div>
                    <div class="pad-cell clip">Clip<br/>T3S2</div>
                    <div class="pad-cell clip">Clip<br/>T4S2</div>
                    <div class="pad-cell clip">Clip<br/>T5S2</div>
                    <div class="pad-cell clip">Clip<br/>T6S2</div>
                    <div class="pad-cell clip">Clip<br/>T7S2</div>
                    <div class="pad-cell scene">Scene<br/>2</div>
                </div>
                <div class="pad-legend">
                    <div class="legend-item">
                        <span class="legend-color" style="background: #555"></span>
                        Dim = No clip
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #0f0"></span>
                        Bright = Has clip
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #fff"></span>
                        White blend = Playing
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #f00"></span>
                        Red blend = Recording
                    </div>
                </div>
                <div style="margin-top: 15px; padding: 12px; background: #2a2a2a; border-radius: 4px; font-size: 13px;">
                    <strong>Clip Pads (0-6, 8-14):</strong> Launch/stop clips on 7 tracks × 2 scenes. Color matches track.<br/>
                    <strong>Scene Pads (7, 15):</strong> Launch all clips in scene 1 or 2.
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

            def _get_html(self):
                """Get HTML page content."""
                return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMK25II Controller Status</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .mode-box {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .mode-box h1 {
            margin: 0;
            font-size: 32px;
            color: #ff5555;
        }
        .browser-box {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
        }
        .browser-box h2 {
            margin: 0 0 20px 0;
            font-size: 24px;
        }
        .level {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            background: #1a1a1a;
            border: 2px solid transparent;
            transition: all 0.2s;
        }
        .level.active {
            border-color: #00ff88;
            background: #1a3a2a;
        }
        .level-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }
        .level-content {
            font-size: 18px;
            font-weight: 500;
        }
        .level-content.empty {
            color: #555;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="mode-box">
            <h1 id="mode">Loading...</h1>
        </div>
        <div class="browser-box">
            <h2>Browser</h2>
            <div class="level" id="level1-box">
                <div class="level-label">Level 1</div>
                <div class="level-content" id="level1">-</div>
            </div>
            <div class="level" id="level2-box">
                <div class="level-label">Level 2</div>
                <div class="level-content" id="level2">-</div>
            </div>
            <div class="level" id="level3-box">
                <div class="level-label">Level 3</div>
                <div class="level-content" id="level3">-</div>
            </div>
            <div class="level" id="level4-box">
                <div class="level-label">Level 4</div>
                <div class="level-content" id="level4">-</div>
            </div>
        </div>
    </div>
    <script>
        // Poll for status updates
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // Update mode
                    document.getElementById('mode').textContent =
                        data.mode.number + '. ' + data.mode.name;

                    // Update browser levels
                    for (let i = 1; i <= 4; i++) {
                        const content = document.getElementById('level' + i);
                        const box = document.getElementById('level' + i + '-box');
                        const value = data.browser['level' + i];

                        if (value) {
                            content.textContent = value;
                            content.classList.remove('empty');
                        } else {
                            content.textContent = '(empty)';
                            content.classList.add('empty');
                        }

                        // Highlight active level
                        if (data.browser.active_level === i - 1) {
                            box.classList.add('active');
                        } else {
                            box.classList.remove('active');
                        }
                    }
                })
                .catch(err => console.error('Error fetching status:', err));
        }

        // Update every 200ms
        setInterval(updateStatus, 200);
        updateStatus();
    </script>
</body>
</html>'''

        return RequestHandler


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP server with threading support."""
    daemon_threads = True  # Threads die when main program exits
    allow_reuse_address = True  # Allow quick restart
