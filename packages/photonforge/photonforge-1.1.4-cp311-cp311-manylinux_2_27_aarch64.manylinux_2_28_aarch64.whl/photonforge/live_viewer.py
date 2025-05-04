import threading
import queue
import logging
import time
import warnings

try:
    from flask import Flask, Response, render_template
    from flask_cors import CORS
    from werkzeug.serving import make_server

    _flask_available = True
except ImportError:
    _flask_available = False
    warnings.warn(
        "The 'live_viewer' submodule requires more dependencies than the base photonforge module. "
        "Please install all dependencies by, e.g., 'pip install photonforge[live_viewer]'.",
        stacklevel=2,
    )


class LiveViewer:
    """Live viewer for PhotonForge objects.

    Args:
        port: Port number used by the viewer server.
        start: If ``True``, the viewer server is automatically started.

    Example:
        >>> from photonforge.live_viewer import LiveViewer
        >>> viewer = LiveViewer()

        >>> component = pf.parametric.straight(port_spec="Strip", length=3)
        >>> viewer(component)

        >>> terminal = pf.Terminal("METAL", pf.Circle(2))
        >>> viewer(terminal)
    """

    def __init__(self, port=5001, start=True):
        if not _flask_available:
            return
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self.queue = queue.Queue()
        self.current_data = ""
        self.server = None

        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        @self.app.route("/")
        def home():
            return render_template("index.html")

        @self.app.route("/events")
        def events():
            def generate():
                while self.server is not None:
                    try:
                        while not self.queue.empty():
                            self.current_data = self.queue.get_nowait()
                    except queue.Empty:
                        pass
                    if self.current_data:
                        yield f"data: {self.current_data}\n\n"
                    else:
                        yield "data: Waiting for data…\n\n"
                    time.sleep(0.25)

            return Response(generate(), mimetype="text/event-stream")

        if start:
            self.start()

    def _run_server(self):
        self.server = make_server("0.0.0.0", self.port, self.app)
        self.server.serve_forever()

    def start(self):
        """Start the server."""
        if not _flask_available:
            return
        print(f"Starting live viewer at http://localhost:{self.port}")
        # Don't mark this thread as daemon, so it keeps the process alive.
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = False
        self.server_thread.start()
        return self

    def stop(self):
        """Stop the server."""
        if not _flask_available:
            return
        if self.server is not None:
            self.server.shutdown()
            self.server = None
            print("Server stopped successfully")

    def __call__(self, item):
        """Display an item with an SVG representation.

        Args:
            item: Item to be displayed.

        Returns:
            'item'.
        """
        if _flask_available and self.server is not None and hasattr(item, "_repr_svg_"):
            self.queue.put(item._repr_svg_())
        return item

    def display(self, item):
        """Display an item with an SVG representation.

        Args:
            item: Item to be displayed.

        Returns:
            'item'.
        """
        return self(item)

    def _repr_html_(self):
        """Returns a clickable link for Jupyter."""
        if not _flask_available:
            return "LiveViewer dependencies not installed."
        if self.server is None:
            return "LiveViewer not started."
        return (
            f'Live viewer at <a href="http://localhost:{self.server.port}" target="_blank">'
            f"http://localhost:{self.server.port}</a>"
        )

    def __str__(self):
        if not _flask_available:
            return "LiveViewer dependencies not installed."
        if self.server is None:
            return "LiveViewer not started."
        return f"Live viewer at http://localhost:{self.server.port}"
