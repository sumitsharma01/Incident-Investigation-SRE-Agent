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
