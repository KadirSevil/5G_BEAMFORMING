# 5G NR Beamforming Coverage Studio

Nokia-first web frontend prototype for 5G NR beamforming configuration and coverage simulation workflow.

## Current Scope (MVP)

- Web UI built with Plotly Dash
- Vendor selector with Nokia active (Huawei and ZTE marked as planned)
- RU capability selector (`8T8R`, `32T32R`, `64T64R`)
- Beam set selection panel for Nokia presets
- Antenna optimization controls (mechanical/electrical tilt, downlink power split)
- Conceptual preview charts for beam footprint and beam utilization

> Note: This phase intentionally focuses on frontend design. Beam propagation and RF equations are placeholders and will be replaced by your technical models.

## Run Locally

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app.py
```

4. Open `http://127.0.0.1:8050`.

## Next Integration Step

When you share beamforming technical material, we can add:

- Vendor-specific parameter schemas
- Real beamforming and coverage equations
- Drive-test / map overlay integration
- FR1/FR2 behavior with RU and panel constraints