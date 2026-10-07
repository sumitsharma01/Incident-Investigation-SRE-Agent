"""Keep offered traffic constant across a capacity intervention; local lab only."""
import asyncio
import argparse
import time
import httpx


async def run(seconds, rps):
    outcomes = {}
    tasks = set()
    async with httpx.AsyncClient(timeout=3, limits=httpx.Limits(max_connections=200)) as client:
        async def request():
            try:
                response = await client.get('http://127.0.0.1:9201/checkout')
                key = str(response.status_code)
            except httpx.HTTPError:
                key = 'client_error'
            outcomes[key] = outcomes.get(key, 0)+1
        start = time.monotonic()
        for index in range(int(seconds*rps)):
            await asyncio.sleep(max(0, start+index/rps-time.monotonic()))
            task = asyncio.create_task(request())
            tasks.add(task)
            task.add_done_callback(tasks.discard)
        await asyncio.gather(*tasks)
    print({'offered_rps': rps, 'duration_seconds': seconds, 'outcomes': outcomes})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, default=240)
    parser.add_argument('--rps', type=float, default=50)
    args = parser.parse_args()
    if not 0 < args.rps <= 100 or not 0 < args.seconds <= 600:
        parser.error('Use 0–100 RPS and 0–600 seconds')
    asyncio.run(run(args.seconds, args.rps))
