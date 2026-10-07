from docker.observability.demo_metrics import sample


def test_default_scenario_stays_steady():
    assert sample(100) == (4500, 200, 0.42, 0)


def test_peak_increases_rate_and_recovers_without_counter_reset():
    before = sample(59, 'high-traffic')
    start = sample(60, 'high-traffic')
    peak = sample(61, 'high-traffic')
    end = sample(150, 'high-traffic')
    recovered = sample(151, 'high-traffic')
    assert start[0] - before[0] == 45
    assert peak[0] - start[0] == 1380
    assert peak[1] - start[1] == 120
    assert peak[2:] == (1.8, 1)
    assert recovered[0] - end[0] == 45
    assert recovered[2:] == (0.42, 0)


def test_overload_raises_tail_latency_and_preserves_counters_on_recovery():
    from docker.observability.demo_metrics import incident_sample
    baseline = incident_sample(59)
    start = incident_sample(60)
    fault = incident_sample(61)
    recovery = incident_sample(301)
    end = incident_sample(300)
    assert start['successes'] - baseline['successes'] == 199
    assert fault['successes'] - start['successes'] == 1600
    assert fault['errors'] - start['errors'] == 400
    assert fault['all_p95'] == 2.4
    assert fault['queue_depth'] == 850
    assert recovery['successes'] - end['successes'] == 1990
    assert recovery['all_p95'] == 0.45
    assert recovery['rejections'] == end['rejections']
