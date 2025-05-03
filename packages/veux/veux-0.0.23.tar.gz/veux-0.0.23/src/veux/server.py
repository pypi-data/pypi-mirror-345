#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# Claudio Perez
# Summer 2024
#
import sys
import threading
import bottle
from wsgiref.simple_server import make_server



class Server:
    def __init__(self, viewer=None, html=None):
        self._app = bottle.Bottle()
        self._server = None

        if html is not None:
            self._app.route("/")(lambda : html )
            return

        if viewer is not None:

            html = viewer.get_html()
            self._app.route("/")(lambda : html )
            @self._app.route("/quit")
            def _quit():
                threading.Thread(target=self._shutdown).start()
                return "Shutting down..."


            for path, page in viewer.resources():
                self._app.route(path)(page)

    def _shutdown(self):
        if self._server:
            self._server.shutdown()

    def run(self, port=None):
        if port is None:
            port = 8081

        print(f"  Displaying at http://localhost:{port}/ \n  Press Ctrl-C to quit.\n")
        self._server = make_server("localhost", port, self._app)
        self._server.serve_forever()
        # try:
        #     bottle.run(self._app, host="localhost", port=port, quiet=True)
        # except KeyboardInterrupt:
        #     print()

if __name__ == "__main__":

    options = {
        "viewer": None
    }
    argi = iter(sys.argv[1:])

    for arg in argi:
        if arg == "--viewer":
            options["viewer"] = next(argi)
        else:
            filename = arg

    with open(filename, "rb") as f:
        glb = f.read()

    Server(glb=glb, **options).run()
