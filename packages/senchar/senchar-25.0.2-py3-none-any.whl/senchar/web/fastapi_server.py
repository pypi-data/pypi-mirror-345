"""
Configure and start fastapi application using uvicorn.
"""

import os
import threading

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.wsgi import WSGIMiddleware

import senchar
from senchar.web.status.status_web import StatusWeb


class WebServer(object):
    """
    senchar web server.
    """

    def __init__(self):
        self.templates_folder = ""
        self.index = ""
        self.favicon_path = ""

        self.logcommands = 0
        self.logstatus = 0
        self.message = ""
        self.datafolder = ""

        # port for webserver
        self.port = 2500

        self.is_running = 0

        senchar.db.webserver = self

    def initialize(self):
        """
        Initialize application.
        """

        # create app
        app = FastAPI()
        self.app = app

        if self.datafolder == "":
            self.datafolder = os.path.dirname(__file__)

        if self.favicon_path == "":
            self.favicon_path = os.path.join(os.path.dirname(__file__), "favicon.ico")

        if self.index == "":
            self.index = os.path.join(os.path.dirname(__file__), "index.html")

        # Plotly Dash webs
        statusweb = StatusWeb()
        app.mount("/status", WSGIMiddleware(statusweb.app.server))

        # templates folder
        try:
            templates = Jinja2Templates(directory=os.path.dirname(self.index))
        except Exception:
            pass

        # ******************************************************************************
        # Home - /
        # ******************************************************************************
        @app.get("/", response_class=HTMLResponse)
        def home(request: Request):
            index = os.path.basename(self.index)
            return templates.TemplateResponse(
                index,
                {
                    "request": request,
                    "message": self.message,
                    "webport": self.port,
                },
            )

    # ******************************************************************************
    # webserver methods
    # ******************************************************************************

    def add_router(self, router):
        """
        Add router.
        """

        self.app.include_router(router)

        return

    def stop(self):
        """
        Stops command server running in thread.
        """

        senchar.log("Stopping the webserver is not supported")

        return

    def start(self):
        """
        Start web server.
        """

        self.initialize()

        senchar.log(f"Starting webserver - listening on port {self.port}")

        # uvicorn.run(self.app)

        arglist = [self.app]
        kwargs = {"port": self.port, "host": "0.0.0.0", "log_level": "critical"}

        thread = threading.Thread(
            target=uvicorn.run, name="uvicorn", args=arglist, kwargs=kwargs
        )
        thread.daemon = True  # terminates when main process exits
        thread.start()

        self.is_running = 1

        return
