#!/usr/bin/env bash

while true; do
  python3 <<'PYEOF' 2>/dev/null
import asyncio, json, websockets
try:
    async def f():
        async with websockets.connect('ws://127.0.0.1:23560/poll', open_timeout=0.3) as ws:
            await ws.send(json.dumps({}))
            msg = await asyncio.wait_for(ws.recv(), timeout=0.3)
            d = json.loads(msg)
            status = d.get('playback_status', '')
            lyrics = d.get('lyrics')
            if status != 'playing' or not lyrics:
                print('')
            else:
                line = (lyrics.get('current_lyric', '') or '').split('|')[0].strip()
                print(line)
    asyncio.run(f())
except:
    pass
PYEOF
  sleep 0.3
done
