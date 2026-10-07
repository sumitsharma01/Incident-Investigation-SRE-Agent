"""Local-only HTTP workload with real queueing and manual worker capacity changes."""
import asyncio
import math
import time
from collections import deque

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title='Recovery verification lab')
capacity = 2
active = 0
waiting = 0
condition = asyncio.Condition()
counts = {'200': 0, '500': 0}
latencies = deque(maxlen=10000)


class Capacity(BaseModel):
    workers: int = Field(ge=1, le=100)


@app.post('/capacity')
async def change_capacity(request: Capacity):
    global capacity
    async with condition:
        capacity = request.workers
        condition.notify_all()
    return {'workers': capacity, 'changed_at': time.time(), 'note': 'Operator intervention; not performed by the investigation agent.'}


@app.get('/checkout')
async def checkout():
    global active, waiting
    start = time.monotonic()
    acquired = False
    status = '200'
    try:
        async with condition:
            waiting += 1
            try:
                await asyncio.wait_for(condition.wait_for(lambda: active < capacity), timeout=.7)
                active += 1
                acquired = True
            finally:
                waiting -= 1
        await asyncio.sleep(.12)
        return {'status': 'completed'}
    except asyncio.TimeoutError:
        status = '500'
        return JSONResponse({'error': 'worker queue timeout'}, status_code=500)
    finally:
        if acquired:
            async with condition:
                active -= 1
                condition.notify_all()
        counts[status] += 1
        latencies.append((time.monotonic(), time.monotonic()-start))


@app.get('/metrics', response_class=PlainTextResponse)
async def metrics():
    cutoff = time.monotonic()-30
    values = sorted(value for timestamp, value in latencies if timestamp >= cutoff)
    p95 = values[max(0, math.ceil(len(values)*.95)-1)] if values else 0
    return '\n'.join([
        '# TYPE sre_lab_requests_total counter',
        *(f'sre_lab_requests_total{{service="checkout-lab",status="{status}"}} {count}' for status,count in counts.items()),
        '# TYPE sre_lab_latency_seconds gauge',
        f'sre_lab_latency_seconds{{service="checkout-lab",quantile="0.95"}} {p95}',
        '# TYPE sre_lab_queue_depth gauge',
        f'sre_lab_queue_depth{{service="checkout-lab"}} {waiting}',
        '# TYPE sre_lab_workers gauge',
        f'sre_lab_workers{{service="checkout-lab"}} {capacity}',
        '# TYPE sre_lab_active gauge',
        f'sre_lab_active{{service="checkout-lab"}} {active}',
        '',
    ])
