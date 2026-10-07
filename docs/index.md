# LibreSRE documentation

[Project home](../README.md) · [Changelog](../CHANGELOG.md)

## Start with the proof run

- [Checkout overload: measurements, agent findings, proposed fixes and replay steps](case-studies/checkout-overload/README.md)
- [Recorded evidence and full agent response](case-studies/checkout-overload/run.json)

## Understand the architecture

- [Production placement, investigation flow and recorded proof diagrams](ARCHITECTURE.md)

## Set up and use the project

- [Grafana/Prometheus step-by-step quickstart](GRAFANA_PROMETHEUS_QUICKSTART.md)
- [Model and provider configuration](MODEL_CONFIGURATION.md)
- [OpenSRE integration: what changed and why](OPENSRE_INTEGRATION.md)
- [Grafana/Prometheus connection details](GRAFANA_PROMETHEUS.md)
- [Replay the smaller high-traffic demo](PEAK_TRAFFIC_DEMO.md)

## Understand the limits

- [Original functionality assessment](ASSESSMENT.md)
- [Live verification history](LIVE_VERIFICATION.md)
- [Version history](../CHANGELOG.md)

The demos use generated metrics. The proof report distinguishes direct
Prometheus measurements, OpenSRE observations, model hypotheses and programmed
recovery. Production readiness and root-cause accuracy require further work.

## Incident workspace

- [Persistent incidents and recovery verification](INCIDENT_WORKSPACE.md)
- [Real worker-capacity recovery proof](case-studies/worker-capacity/README.md)
