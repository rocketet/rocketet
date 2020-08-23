import logging

from aiohttp import web
import aiohttp_jinja2
import jinja2

from settings import config, BASE_DIR
from routes import setup_routes, setup_static_routes
from middlewares import setup_middlewares
from db import init_pg, close_pg


async def close_ws(app):
    for ws in app["websockets"].values():
        await ws.close()
    app["websockets"].clear()


logging.basicConfig(level=logging.DEBUG)

app = web.Application()
app["websockets"] = {}
app["config"] = config
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(str(BASE_DIR / "rocketet" / "templates"))
)
setup_routes(app)
setup_static_routes(app)
setup_middlewares(app)
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
app.on_shutdown.append(close_ws)
web.run_app(app)
