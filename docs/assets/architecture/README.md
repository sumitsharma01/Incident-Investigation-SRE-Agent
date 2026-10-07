# Architecture graphics

Three original diagrams explain the project without implying an existing
production deployment or unsupported integrations:

| Graphic | Purpose |
| --- | --- |
| `production-placement` | Separate serving, observability and investigation boundaries |
| `investigation-flow` | HTTP request, orchestration, OpenSRE/tool loop and engineer review |
| `overload-proof` | Rounded values from the recorded baseline, incident and recovery snapshots |

Each graphic has an editable SVG and a high-resolution PNG export. Logos are
embedded as data URLs in the SVG so the file is self-contained. SVG titles and
descriptions provide text context; the documentation supplies the full explanation.

## Regenerate

From the repository root, with the screenshots extra and browser installed:

```bash
pip install -e '.[screenshots]'
playwright install chromium
python examples/generate_architecture_graphics.py
```

Use `--executable-path` for an installed Chrome/Chromium executable. The script
renders at twice the SVG dimensions for crisp PNG exports. Review text fit,
arrows and component claims after editing. These are architecture illustrations,
not screenshots of running services.

## Brand asset attribution

| Asset | Source | Retained license/source notes |
| --- | --- | --- |
| Grafana mark | OpenSRE `docs/assets/icons/grafana.webp` | Copied from reviewed OpenSRE source; upstream Apache 2.0 license retained |
| Azure mark | OpenSRE `docs/assets/icons/azure.png` | Copied from reviewed OpenSRE source; upstream Apache 2.0 license retained |
| OpenSRE wordmark | OpenSRE `docs/logo/opensre-logo-white.svg` | Copied unchanged from reviewed OpenSRE source; upstream Apache 2.0 license retained |
| Prometheus icon | [Simple Icons source](https://github.com/simple-icons/simple-icons/blob/develop/icons/prometheus.svg) | CC0 license retained; rendered in Prometheus orange |
| FastAPI icon | [Simple Icons source](https://github.com/simple-icons/simple-icons/blob/develop/icons/fastapi.svg) | CC0 license retained; rendered in teal |
| People, servers, routes, report and shield icons | Original vector paths in the generator | Project-specific illustrations, not third-party logos |

OpenSRE source commit: `288a82456af27ce75487527b2b21c7ab1cbf5d6b`.
Simple Icons files were retrieved on 7 October 2026. Local copies are retained
under `brands/`; license texts are under `licenses/`. Product names and marks
belong to their respective owners and are used to identify integrations.

The reference graphics were reviewed for layout conventions. Tracer architecture
images and banners were not copied into this project. Diagram wording, layout,
color grouping and generic icons were created for this repository.
