"""Serveur de santé du recorder — :8788, JAMAIS :8787 (ADR-002).

Lecture seule, deux routes :
  GET /health   état par flux (synchro, âge du dernier message, lignes, trous)
  GET /gaps     les trous récents, pour vérifier d'un coup d'œil qu'ils sont
                marqués et non maquillés
"""
from __future__ import annotations

import asyncio

import orjson
from aiohttp import web

from gondetect import config as C


def build_app(engine) -> web.Application:
    async def health(_req):
        return web.Response(body=orjson.dumps(engine.health()),
                            content_type="application/json")

    async def gaps(_req):
        out = []
        for (venue, sym), started in engine.in_gap.items():
            s = engine.streams[(venue, sym)]
            out.append(dict(venue=venue, sym=sym, in_gap=bool(started),
                            since_ms=started or None, gaps_total=s.gaps,
                            reason=s.reason if not s.synced else None))
        return web.Response(body=orjson.dumps(out), content_type="application/json")

    app = web.Application()
    app.add_routes([web.get("/", health), web.get("/health", health),
                    web.get("/gaps", gaps)])
    return app


async def serve(engine) -> None:
    runner = web.AppRunner(build_app(engine))
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", C.RECORDER_PORT)
    await site.start()
    engine.log(f"santé : http://127.0.0.1:{C.RECORDER_PORT}/health")
    await asyncio.Event().wait()
