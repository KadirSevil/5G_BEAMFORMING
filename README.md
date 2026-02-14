# 5G Beamforming Planner (Nokia-first)

Interactive 5G NR beamforming simulator and coverage planning app built with Dash + Plotly.

## Current Status

This project is no longer a placeholder UI. Core beam and coverage behavior is now functional and tied to parameters.

Implemented:

- Vendor selector (Nokia active terminology profile)
- RU configuration support (`8T8R`, `32T32R`, `64T64R`)
- Nokia beam set selection and edge-angle steering controls
- Functional advanced controls:
	- `NRCELL-beamSet.nrBtsBeamRefinementP2`
	- `mMIMOAntArrayMode`
	- `NRCELL.numDftBeamMuteLeft`
	- `NRCELL.numDftBeamMuteRight`
- 3D beam lobe view + beam grid view
- Ground coverage estimation on map using:
	- Array gain + element pattern
	- Simplified 3GPP UMa-like path loss
	- RU Tx power, antenna coordinates, antenna azimuth, antenna height
- RSRP visibility threshold filtering
- Hover details including beam/cell serving information and 3D distance
- Ghost overlay mode (previous parameter state comparison)
- Correct beam ID mapping in 2D coverage hover
- Improved top layout split (`~65/35`) with clearer beam IDs in beam grid
- 2D map UX controls:
	- Perspective toggle (`Flat 2D` / `Near 3D`)
	- Map theme dropdown (multiple basemap styles)
	- Free zoom-out support
- Cluster coverage milestone (2D):
	- Multi-cell dominant coverage painting (best-serving cell paints each location)
	- Secondary-cell visibility in hover for overlap analysis
	- Per-cell marker + azimuth direction overlay
	- Manual multi-cell entry (quick rows)
	- CSV upload support for larger cluster scenarios
	- Downloadable CSV template: `assets/cluster_cells_template.csv`

## Coverage Views

- `2D Map (Current)`: primary planning view, now supports single-cell and cluster-cell coverage
- `3D Urban Base Layer (Stage 1)`: standalone non-satellite urban base map (propagation overlay deferred)

## Cluster Input Format

For bulk cluster runs, upload CSV with this column set:

- `cell_id,lat,lon,antenna_azimuth_deg,beam_set,ru_type,freq_ghz,d_h_lam,d_v_lam,tilt_offset,upper_edge,lower_edge,left_edge,right_edge,nr_bts_beam_refinement_p2,mmimo_ant_array_mode,num_dft_beam_mute_right,num_dft_beam_mute_left,antenna_height,tx_power_w`

Notes:

- If some optional columns are omitted in manual entry, app-level defaults are used.
- Manual quick-entry format (one cell per line):
	- `cell_id,lat,lon,azimuth_deg,beam_set`
- Template file is available in `assets/cluster_cells_template.csv`.

## Run Locally

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app.py
```

4. Open in browser:

```text
http://127.0.0.1:8051
```

## Known Limitations

- Huawei and ZTE terminology profiles are not fully mapped yet.
- 3D urban mode is currently base-layer-first and not yet full propagation-on-3D terrain/building GIS.
- Full building blockage/diffraction modeling is not yet implemented.
- Current cluster rendering paints dominant serving cell on map; secondary visibility is hover-based.

## Next Session Plan

Agreed next development order:

1. Add propagation overlay on top of the standalone 3D base layer.
2. Extend cluster analysis outputs (e.g., optional top-3 serving cells, SINR-like summaries).
3. Calibrate RF realism (urban attenuation model, performance, and UX tuning).