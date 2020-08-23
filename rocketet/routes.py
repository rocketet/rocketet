import logging

import aiohttp
from aiohttp import web
import aiohttp_jinja2

# from views import index, login, chat, chat_ws
from settings import BASE_DIR

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/", name="index")
async def index(request):
    return aiohttp_jinja2.render_template("index.html", request, {})


@routes.post("/")
async def login(request):
    form_data = await request.post()

    name = form_data.get('name')
    if name:
        raise web.HTTPFound(request.app.router["chat"].url_for(name=name))
    else:
        raise web.HTTPFound(request.app.router["index"].url_for())


@routes.get("/{name}/", name="chat")
async def chat(request):
    return aiohttp_jinja2.render_template("chat.html", request, {})


@routes.get("/{name}/ws/")
async def chat_ws(request):
    print(1)
    ws_current = web.WebSocketResponse()
    name = request.match_info["name"]
    await ws_current.prepare(request)

    log.info("%s joined.", name)

    await ws_current.send_json({"action": "connect", "name": name})

    for ws in request.app["websockets"].values():
        await ws.send_json({"action": "join", "name": name})
    request.app["websockets"][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            # data = msg.json()

            # if data["type"] =
            for ws in request.app["websockets"].values():
                if ws is not ws_current:
                    data = msg.json()
                    await ws.send_json(
                        {"action": "sent", "name": name, "text": data["text"]})
        else:
            break

    del request.app["websockets"][name]
    log.info("%s disconnected.", name)
    for ws in request.app["websockets"].values():
        await ws.send_json({"action": "disconnect", "name": name})

    return ws_current


def setup_routes(app):
    # app.router.add_get("/", index, name="index")
    # app.router.add_post("/", login)
    # app.router.add_get("/{name}/chat/", chat, name="chat")
    # app.router.add_get("/{name}/chat/ws", chat_ws)
    app.router.add_routes(routes)


def setup_static_routes(app):
    app.router.add_static("/static/",
                          path=BASE_DIR / "rocketet" / "static",
                          name="static")
