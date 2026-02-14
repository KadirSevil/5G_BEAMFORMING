from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple
import math
import re

import dash
from dash import Dash, Input, Output, State, dcc, html, callback_context
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go

# ============================================================
# 5G NR Beamforming 3D Simulator — Light Theme
# Nokia-style 3D beam lobe visualization
# ============================================================

# --- BEAM SET DEFINITIONS (Nokia nomenclature) ---
BEAM_SET_DEFS = {
    "beamSet_1":            {"rows": [1],          "label": "#1",          "az_opening": 90},
    "beamSet_2":            {"rows": [2],          "label": "#2",          "az_opening": 120},
    "beamSet_4":            {"rows": [4],          "label": "#4",          "az_opening": 90},
    "beamSet_6":            {"rows": [6],          "label": "#6",          "az_opening": 120},
    "beamSet_8":            {"rows": [8],          "label": "#8",          "az_opening": 90},
    "beamSet_2_2":          {"rows": [2, 2],       "label": "#2#2",       "az_opening": 90},
    "beamSet_3_1":          {"rows": [3, 1],       "label": "#3#1",       "az_opening": 90},
    "beamSet_3_3":          {"rows": [3, 3],       "label": "#3#3",       "az_opening": 120},
    "beamSet_4_2":          {"rows": [4, 2],       "label": "#4#2",       "az_opening": 120},
    "beamSet_4_4":          {"rows": [4, 4],       "label": "#4#4",       "az_opening": 90},
    "beamSet_5_1":          {"rows": [5, 1],       "label": "#5#1",       "az_opening": 90},
    "beamSet_5_3":          {"rows": [5, 3],       "label": "#5#3",       "az_opening": 120},
    "beamSet_6_2":          {"rows": [6, 2],       "label": "#6#2",       "az_opening": 90},
    "beamSet_3_3_2_square": {"rows": [3, 3, 2],    "label": "#3#3#2 (sq)","az_opening": 120},
    "beamSet_3_3_2_azimuth":{"rows": [3, 3, 2],    "label": "#3#3#2 (az)","az_opening": 120},
    "beamSet_2_2_2_2":      {"rows": [2, 2, 2, 2], "label": "#2#2#2#2",   "az_opening": 90},
}

# --- RU CONFIGURATIONS ---
RU_CONFIGS = {
    "8T8R":   {"n_col": 4,  "n_row": 1, "max_layers": 4,  "fr": ["FR1"]},
    "32T32R": {"n_col": 8,  "n_row": 2, "max_layers": 8,  "fr": ["FR1"]},
    "64T64R": {"n_col": 8,  "n_row": 4, "max_layers": 16, "fr": ["FR1"]},
}

VENDOR_OPTIONS = ["Nokia", "Huawei", "ZTE"]

TERMINOLOGY = {
    "Nokia": {
        "controls_title": "⚙️ Nokia Beam Management Parameters",
        "ru_type": "RU Type (TRX Configuration)",
        "beam_set": "NRCELL-beamSet.basicBeamSet",
        "carrier_freq": "NR Carrier Frequency (FR1, GHz)",
        "d_h": "Horizontal Element Spacing d_h (λ)",
        "d_v": "Vertical Element Spacing d_v (λ)",
        "steering_title": "📐 Beam Steering / Vertical Tilt",
        "tilt_offset": "Beam Vertical Tilt Offset (°)",
        "upper_edge": "NRCELL-beamSet.upperedgeangle (°)",
        "lower_edge": "NRCELL-beamSet.loweredgeangle (°)",
        "left_edge": "NRCELL-beamSet.leftEdgeAngle (°)",
        "right_edge": "NRCELL-beamSet.rightEdgeAngle (°)",
        "install_title": "🏗️ Antenna / RU Installation",
        "antenna_height": "Antenna Height AGL (m)",
        "viz_title": "🎨 Visualization",
        "lobe_scale": "Beam Lobe Scale",
        "gain_threshold": "Beam Gain Cutoff (dB below peak)",
        "grid_resolution": "Beam Pattern Grid Resolution",
        "info_vendor": "Vendor",
        "info_beam_set": "NRCELL-beamSet.basicBeamSet",
        "info_total_beams": "Total Beams",
        "info_rows": "Beam Rows",
        "info_beams_per_row": "basicBeamSet Structure (#k#l#m)",
        "info_az_opening": "Azimuth Opening Angle",
        "info_ru_array": "RU TRX Layout (N1×N2)",
        "info_lambda": "Wavelength λ",
        "info_az_bw": "Approx. Azimuth BW / beam",
        "info_el_bw": "Approx. Elevation BW / beam",
        "info_el_range": "Elevation Range",
        "info_tilt": "Beam Vertical Tilt Offset",
        "info_height": "Antenna Height AGL",
    },
    "Huawei": {
        "controls_title": "⚙️ Huawei Beamforming Configuration",
        "ru_type": "Radio Unit Type",
        "beam_set": "Beam Set",
        "carrier_freq": "Carrier Frequency (GHz)",
        "d_h": "Horizontal Spacing d_h (λ)",
        "d_v": "Vertical Spacing d_v (λ)",
        "steering_title": "📐 Beam Steering & Tilt",
        "tilt_offset": "Tilt Offset (°)",
        "upper_edge": "Upper Edge Angle (°)",
        "lower_edge": "Lower Edge Angle (°)",
        "left_edge": "Left Edge Angle (°)",
        "right_edge": "Right Edge Angle (°)",
        "install_title": "🏗️ Antenna Installation",
        "antenna_height": "Antenna Height AGL (m)",
        "viz_title": "🎨 Visualization",
        "lobe_scale": "Lobe Scale",
        "gain_threshold": "Gain Threshold (dB below peak)",
        "grid_resolution": "Grid Resolution",
        "info_vendor": "Vendor",
        "info_beam_set": "Beam Set",
        "info_total_beams": "Total Beams",
        "info_rows": "Rows",
        "info_beams_per_row": "Beams/Row",
        "info_az_opening": "Az Opening",
        "info_ru_array": "RU Array",
        "info_lambda": "λ",
        "info_az_bw": "≈ Az BW/beam",
        "info_el_bw": "≈ El BW/beam",
        "info_el_range": "El range",
        "info_tilt": "Tilt offset",
        "info_height": "Antenna Height",
    },
    "ZTE": {
        "controls_title": "⚙️ ZTE Beamforming Configuration",
        "ru_type": "Radio Unit Type",
        "beam_set": "Beam Set",
        "carrier_freq": "Carrier Frequency (GHz)",
        "d_h": "Horizontal Spacing d_h (λ)",
        "d_v": "Vertical Spacing d_v (λ)",
        "steering_title": "📐 Beam Steering & Tilt",
        "tilt_offset": "Tilt Offset (°)",
        "upper_edge": "Upper Edge Angle (°)",
        "lower_edge": "Lower Edge Angle (°)",
        "left_edge": "Left Edge Angle (°)",
        "right_edge": "Right Edge Angle (°)",
        "install_title": "🏗️ Antenna Installation",
        "antenna_height": "Antenna Height AGL (m)",
        "viz_title": "🎨 Visualization",
        "lobe_scale": "Lobe Scale",
        "gain_threshold": "Gain Threshold (dB below peak)",
        "grid_resolution": "Grid Resolution",
        "info_vendor": "Vendor",
        "info_beam_set": "Beam Set",
        "info_total_beams": "Total Beams",
        "info_rows": "Rows",
        "info_beams_per_row": "Beams/Row",
        "info_az_opening": "Az Opening",
        "info_ru_array": "RU Array",
        "info_lambda": "λ",
        "info_az_bw": "≈ Az BW/beam",
        "info_el_bw": "≈ El BW/beam",
        "info_el_range": "El range",
        "info_tilt": "Tilt offset",
        "info_height": "Antenna Height",
    },
}


def get_terms(vendor: str) -> dict:
    return TERMINOLOGY.get(vendor, TERMINOLOGY["Nokia"])


def apply_mmimo_array_mode(n_col: int, n_row: int, mode: int) -> tuple[int, int]:
    if mode in (1, 2):
        return max(1, n_col // 2), n_row
    if mode in (3, 4):
        return n_col, max(1, n_row // 2)
    if mode in (5, 6, 7):
        return max(1, n_col // 2), max(1, n_row // 2)
    return n_col, n_row


def apply_dft_beam_mute(az_positions: list[float], mute_left: int, mute_right: int) -> list[float]:
    if not az_positions:
        return az_positions

    n = len(az_positions)
    left = max(0, min(int(mute_left), max(0, n - 1)))
    right = max(0, min(int(mute_right), max(0, n - left - 1)))
    end_idx = n - right
    active = az_positions[left:end_idx]

    if not active:
        return [az_positions[n // 2]]
    return active


def get_refined_centers(az_center: float, el_center: float,
                        az_half: float, el_half: float,
                        refinement_enabled: bool) -> list[tuple[float, float]]:
    if not refinement_enabled:
        return [(az_center, el_center)]

    az_delta = max(0.8, az_half * 0.35)
    el_delta = max(0.8, el_half * 0.35)
    return [
        (az_center - az_delta, el_center - el_delta),
        (az_center - az_delta, el_center + el_delta),
        (az_center + az_delta, el_center - el_delta),
        (az_center + az_delta, el_center + el_delta),
    ]


def parse_lat_lon(coord_text: str | None) -> tuple[float, float]:
    if not coord_text:
        return 40.75503684862242, 29.94555084488382

    try:
        parts = [p.strip() for p in str(coord_text).split(",")]
        if len(parts) != 2:
            raise ValueError("Invalid coordinate format")
        lat = float(parts[0])
        lon = float(parts[1])
        return lat, lon
    except Exception:
        return 40.75503684862242, 29.94555084488382


def meters_to_latlon(dx_m: np.ndarray, dy_m: np.ndarray, lat0_deg: float, lon0_deg: float) -> tuple[np.ndarray, np.ndarray]:
    lat_scale = 1.0 / 111320.0
    lon_scale = 1.0 / (111320.0 * max(np.cos(np.deg2rad(lat0_deg)), 1e-6))
    lat = lat0_deg + dy_m * lat_scale
    lon = lon0_deg + dx_m * lon_scale
    return lat, lon


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    c = hex_color.lstrip('#')
    if len(c) != 6:
        return 128, 128, 128
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def beam_shaded_color(base_hex: str, power_dbm: float,
                      min_dbm: float = -130.0, max_dbm: float = -60.0) -> str:
    r, g, b = hex_to_rgb(base_hex)
    norm = (power_dbm - min_dbm) / (max_dbm - min_dbm + 1e-12)
    norm = max(0.0, min(1.0, norm))
    whiten = (1.0 - norm) * 0.82
    rr = int(r + (255 - r) * whiten)
    gg = int(g + (255 - g) * whiten)
    bb = int(b + (255 - b) * whiten)
    return f'rgb({rr},{gg},{bb})'

# --- DISTINCT BEAM COLOR PALETTE (high contrast on white) ---
BEAM_COLORS = [
    "#B71C1C",  # deep red
    "#1E5A7A",  # deep steel blue
    "#00695C",  # deep teal
    "#A67C00",  # dark gold
    "#B85C00",  # dark orange
    "#1B3A4B",  # deep dark teal
    "#4A2A73",  # deep purple
    "#0F5D8A",  # deep blue
    "#4E8F00",  # deep green
    "#C62828",  # deep coral red
    "#B28704",  # deep yellow-gold
    "#3E6F2A",  # deep olive green
    "#8E2E32",  # deep brick red
    "#1D5FD2",  # deep vivid blue
    "#5E20B8",  # deep violet
    "#C44545",  # deep salmon
]

# --- ANTENNA ELEMENT PATTERN (3GPP TR 38.901) ---
def element_pattern_h(phi_deg, phi_3dB=65, Am=30):
    return -np.minimum(12 * (phi_deg / phi_3dB)**2, Am)

def element_pattern_v(theta_deg, theta_3dB=65, SLA_v=30):
    return -np.minimum(12 * (theta_deg / theta_3dB)**2, SLA_v)

def element_pattern_2d(phi_deg, theta_deg, G_max=8):
    return G_max - np.minimum(-(element_pattern_h(phi_deg) + element_pattern_v(theta_deg)), 30)

# --- ARRAY FACTOR ---
def array_factor_2d(phi_rad, theta_rad, n_col, n_row, d_h, d_v, k,
                    phi_steer_rad, theta_steer_rad):
    psi_h = k * d_h * (np.sin(phi_rad) * np.cos(theta_rad) -
                        np.sin(phi_steer_rad) * np.cos(theta_steer_rad))
    psi_v = k * d_v * (np.sin(theta_rad) - np.sin(theta_steer_rad))
    if n_col > 1:
        af_h = np.sin(n_col * psi_h / 2) / (n_col * np.sin(psi_h / 2 + 1e-20))
    else:
        af_h = np.ones_like(phi_rad)
    if n_row > 1:
        af_v = np.sin(n_row * psi_v / 2) / (n_row * np.sin(psi_v / 2 + 1e-20))
    else:
        af_v = np.ones_like(theta_rad)
    return af_h * af_v


def compute_single_beam_lobe(n_col, n_row, freq_ghz, d_h_lam, d_v_lam,
                              phi_steer_deg, theta_steer_deg,
                              az_half_width=None, el_half_width=None,
                              n_pts=60, gain_threshold_dB=6):
    c = 3e8
    freq = freq_ghz * 1e9
    lam = c / freq
    k = 2 * np.pi / lam
    d_h = d_h_lam * lam
    d_v = d_v_lam * lam

    if az_half_width is None:
        bw_az_rad = 0.886 * lam / (n_col * d_h + 1e-6)
        az_half_width = max(np.rad2deg(bw_az_rad) * 2.5, 8)
    if el_half_width is None:
        bw_el_rad = 0.886 * lam / (n_row * d_v + 1e-6)
        el_half_width = max(np.rad2deg(bw_el_rad) * 2.5, 8)

    phi_min = max(phi_steer_deg - az_half_width, -90)
    phi_max = min(phi_steer_deg + az_half_width, 90)
    theta_min = max(theta_steer_deg - el_half_width, -45)
    theta_max = min(theta_steer_deg + el_half_width, 45)

    phi_deg = np.linspace(phi_min, phi_max, n_pts)
    theta_deg = np.linspace(theta_min, theta_max, n_pts)
    PHI_DEG, THETA_DEG = np.meshgrid(phi_deg, theta_deg)
    PHI_RAD = np.deg2rad(PHI_DEG)
    THETA_RAD = np.deg2rad(THETA_DEG)
    phi_s = np.deg2rad(phi_steer_deg)
    theta_s = np.deg2rad(theta_steer_deg)

    AF = array_factor_2d(PHI_RAD, THETA_RAD, n_col, n_row, d_h, d_v, k, phi_s, theta_s)
    EP = element_pattern_2d(PHI_DEG, THETA_DEG)
    total_dB = 20 * np.log10(np.abs(AF) + 1e-12) + EP

    peak = np.max(total_dB)
    rel_dB = total_dB - peak
    mask = rel_dB > -gain_threshold_dB
    R = np.where(mask, (rel_dB + gain_threshold_dB) / gain_threshold_dB, np.nan)

    X = R * np.cos(THETA_RAD) * np.sin(PHI_RAD)
    Y = R * np.sin(THETA_RAD)
    Z = R * np.cos(THETA_RAD) * np.cos(PHI_RAD)
    return X, Y, Z, total_dB, mask


def generate_beam_set_figure(beam_set_key, ru_type, freq_ghz, d_h_lam, d_v_lam,
                              tilt_offset, az_opening_override, n_pts,
                              gain_threshold, show_envelope, lobe_scale,
                              upper_edge_angle, lower_edge_angle, antenna_height_m,
                              vendor="Nokia", mmimo_ant_array_mode=0,
                              nr_bts_beam_refinement_p2=False,
                              num_dft_beam_mute_right=0,
                              num_dft_beam_mute_left=0,
                              antenna_x_m=0.0,
                              antenna_y_m=0.0,
                              antenna_azimuth_deg=0.0,
                              active_beam_ids=None):
    bs = BEAM_SET_DEFS[beam_set_key]
    ru = RU_CONFIGS[ru_type]
    rows = bs["rows"]
    n_rows = len(rows)
    total_beams = sum(rows)
    az_opening = az_opening_override if az_opening_override else bs["az_opening"]
    az_half = az_opening / 2
    n_col, n_row = apply_mmimo_array_mode(ru["n_col"], ru["n_row"], mmimo_ant_array_mode)

    # Normalize antenna height for display (scale factor)
    # Map real height (5-80m) to visual units
    height_scale = antenna_height_m / 30.0  # 30m = 1.0 visual unit

    if n_rows == 1:
        el_centers = [tilt_offset]
    else:
        el_span = upper_edge_angle - lower_edge_angle
        el_centers = [upper_edge_angle - i * el_span / (n_rows - 1) + tilt_offset
                      for i in range(n_rows)]

    world_scale_m = 30.0
    site_x = antenna_x_m / world_scale_m
    site_y = antenna_y_m / world_scale_m
    az_rot = np.deg2rad(float(antenna_azimuth_deg))
    c_rot = np.cos(az_rot)
    s_rot = np.sin(az_rot)

    fig = go.Figure()
    beam_idx = 1

    for row_i, n_beams_in_row in enumerate(rows):
        el_center = el_centers[row_i]
        if n_beams_in_row == 1:
            az_positions = [0.0]
        else:
            step = az_opening / n_beams_in_row
            az_positions = [(-az_half + step/2) + j * step for j in range(n_beams_in_row)]
        az_positions = apply_dft_beam_mute(az_positions, num_dft_beam_mute_left, num_dft_beam_mute_right)

        active_beams_in_row = max(1, len(az_positions))
        az_beam_half = (az_opening / active_beams_in_row) / 2 * 1.3
        el_beam_half = (abs(upper_edge_angle - lower_edge_angle) / max(n_rows, 1)) / 2 * 1.3 if n_rows > 1 else 12

        for col_j, az_center in enumerate(az_positions):
            beam_is_active = active_beam_ids is None or beam_idx in active_beam_ids
            refined_centers = get_refined_centers(
                az_center, el_center, az_beam_half, el_beam_half, nr_bts_beam_refinement_p2
            )
            for az_ref, el_ref in refined_centers:
                X, Y, Z, gain_dB, mask = compute_single_beam_lobe(
                    n_col, n_row, freq_ghz, d_h_lam, d_v_lam,
                    az_ref, el_ref,
                    az_half_width=az_beam_half,
                    el_half_width=el_beam_half,
                    n_pts=n_pts,
                    gain_threshold_dB=gain_threshold
                )

                X_s = X * lobe_scale
                Y_s = Y * lobe_scale + height_scale  # offset beams to antenna height
                Z_s = Z * lobe_scale

                X_w = Z_s * c_rot - X_s * s_rot + site_x
                Y_w = Z_s * s_rot + X_s * c_rot + site_y

                color = BEAM_COLORS[beam_idx % len(BEAM_COLORS)]

                fig.add_trace(go.Surface(
                    x=X_w, y=Y_w, z=Y_s,
                    surfacecolor=gain_dB,
                    colorscale=[
                        [0, '#1A1A1A'],
                        [0.35, color],
                        [1, color]
                    ],
                    opacity=0.96,
                    showscale=False,
                    name=f'Beam {beam_idx} (R{row_i+1}C{col_j+1})',
                    legendgroup=f'beam-{beam_idx}',
                    hovertemplate=(
                        f'<b>Beam {beam_idx}</b> (Row {row_i+1}, Col {col_j+1})<br>'
                        f'Az steer: {az_ref:.1f}°<br>'
                        f'El steer: {el_ref:.1f}°<br>'
                        f'Gain: %{{surfacecolor:.1f}} dB<extra></extra>'
                    ),
                    showlegend=(az_ref, el_ref) == refined_centers[0],
                    visible=True if beam_is_active else 'legendonly',
                ))
            beam_idx += 1

    # --- ANTENNA TOWER / MAST ---
    # Tower base at ground (z=0), top at antenna height
    tower_segments = 20
    tower_z = np.linspace(0, height_scale, tower_segments)

    # Main mast (vertical pole)
    fig.add_trace(go.Scatter3d(
        x=[site_x]*tower_segments, y=[site_y]*tower_segments, z=tower_z.tolist(),
        mode='lines',
        line=dict(color='#555555', width=6),
        name='Tower Mast',
        showlegend=True,
        hovertemplate=(
            f'Tower Mast<br>Height: {antenna_height_m:.0f} m'
            f'<br>Local beam-space origin<extra></extra>'
        ),
    ))

    # Tower cross-braces (lattice effect)
    brace_interval = max(1, tower_segments // 5)
    for i in range(0, tower_segments, brace_interval):
        z_val = tower_z[i]
        w = 0.03 * (1 - z_val / (height_scale + 0.01) * 0.5)  # taper
        fig.add_trace(go.Scatter3d(
            x=[site_x - 0.01, site_x - 0.01, site_x - 0.01],
            y=[site_y - w, site_y, site_y + w],
            z=[z_val, z_val, z_val],
            mode='lines',
            line=dict(color='#888888', width=2),
            showlegend=False, hoverinfo='skip',
        ))

    # Antenna panel at top of tower
    panel_w = 0.06
    panel_h_vis = 0.08
    fig.add_trace(go.Mesh3d(
        x=[site_x - 0.015, site_x - 0.015, site_x - 0.015, site_x - 0.015],
        y=[site_y - panel_w, site_y + panel_w, site_y + panel_w, site_y - panel_w],
        z=[height_scale - panel_h_vis, height_scale - panel_h_vis,
           height_scale + panel_h_vis, height_scale + panel_h_vis],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color='#37474F',
        opacity=0.95,
        name=f'Antenna ({antenna_height_m:.0f}m)',
        showlegend=True,
        hovertemplate=f'Antenna Panel<br>Height: {antenna_height_m:.0f} m AGL<extra></extra>',
    ))

    # Ground plane
    gnd_size = lobe_scale * 1.5
    fig.add_trace(go.Mesh3d(
        x=[site_x - gnd_size*0.3, site_x + gnd_size*1.2, site_x + gnd_size*1.2, site_x - gnd_size*0.3],
        y=[site_y - gnd_size, site_y - gnd_size, site_y + gnd_size, site_y + gnd_size],
        z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color='#E8F5E9',
        opacity=0.4,
        name='Ground Level',
        showlegend=True,
        hovertemplate='Ground Level (0m AGL)<extra></extra>',
    ))

    # Height annotation line (dashed vertical with label)
    fig.add_trace(go.Scatter3d(
        x=[site_x - 0.08, site_x - 0.08], y=[site_y + 0.12, site_y + 0.12], z=[0, height_scale],
        mode='lines+text',
        line=dict(color='#D32F2F', width=2, dash='dash'),
        text=['', f'{antenna_height_m:.0f}m AGL'],
        textposition='top center',
        textfont=dict(size=11, color='#D32F2F', family='Arial Black'),
        showlegend=False, hoverinfo='skip',
    ))

    # Axis reference lines
    max_r = lobe_scale * 1.2
    boresight_dx = max_r * c_rot
    boresight_dy = max_r * s_rot
    az_axis_dx = -max_r * 0.3 * s_rot
    az_axis_dy = max_r * 0.3 * c_rot
    for axis_line, color, name in [
        ([boresight_dx, boresight_dy, height_scale], '#B71C1C', 'Boresight →'),
        ([az_axis_dx, az_axis_dy, height_scale], '#1B5E20', '← Azimuth →'),
        ([0, 0, height_scale + max_r*0.2], '#0D47A1', '↑ Elevation'),
    ]:
        fig.add_trace(go.Scatter3d(
            x=[site_x, site_x + axis_line[0]], y=[site_y, site_y + axis_line[1]], z=[height_scale, axis_line[2]],
            mode='lines+text',
            line=dict(color=color, width=2, dash='dot'),
            text=['', name],
            textposition='top center',
            textfont=dict(size=10, color=color, family='Arial'),
            showlegend=False, hoverinfo='skip',
        ))

    max_z = max(height_scale + max_r * 0.5, height_scale + 0.3)

    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Arial, Helvetica, sans-serif', size=13, color='#212121'),
        title=dict(
            text=(f'<b>{vendor} 5G NR Beam Set {bs["label"]}</b> — {ru_type} @ {freq_ghz} GHz'
                  f'<br><span style="font-size:12px;color:#666">{total_beams} beams | {n_rows} row(s) | '
                  f'Az opening: {az_opening}° | Tilt: {tilt_offset}° | '
                f'Antenna Az: {antenna_azimuth_deg:.0f}° | '
                f'Height: {antenna_height_m:.0f}m</span>'),
            font=dict(size=16, color='#1a1a1a'),
        ),
        scene=dict(
            xaxis=dict(
                title=dict(text='Boresight →', font=dict(size=12, color='#333')),
                range=[-0.1, max_r],
                backgroundcolor='#FAFAFA',
                gridcolor='#E0E0E0',
                showbackground=True,
            ),
            yaxis=dict(
                title=dict(text='← Azimuth →', font=dict(size=12, color='#333')),
                range=[-max_r*0.8, max_r*0.8],
                backgroundcolor='#FAFAFA',
                gridcolor='#E0E0E0',
                showbackground=True,
            ),
            zaxis=dict(
                title=dict(text='Height / Elevation', font=dict(size=12, color='#333')),
                range=[-0.05, max_z],
                backgroundcolor='#F5F5F5',
                gridcolor='#E0E0E0',
                showbackground=True,
            ),
            camera=dict(eye=dict(x=1.6, y=-1.3, z=0.9)),
            aspectmode='manual',
            aspectratio=dict(x=2, y=1.2, z=1.0),
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#CCCCCC',
            borderwidth=1,
            font=dict(color='#333333', size=11, family='Arial'),
            x=1.0, y=1.0,
            groupclick='togglegroup',
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        height=520,
    )
    return fig


def generate_beam_grid_diagram(beam_set_key, num_dft_beam_mute_right=0, num_dft_beam_mute_left=0):
    bs = BEAM_SET_DEFS[beam_set_key]
    rows = bs["rows"]
    n_rows = len(rows)
    max_cols = max(rows)

    fig = go.Figure()

    for row_i, n_beams in enumerate(rows):
        y = n_rows - 1 - row_i
        x_offset = (max_cols - n_beams) / 2
        base_positions = [x_offset + col_j for col_j in range(n_beams)]
        active_positions = apply_dft_beam_mute(base_positions, num_dft_beam_mute_left, num_dft_beam_mute_right)

        for col_j, x in enumerate(active_positions):
            color = BEAM_COLORS[(row_i * max_cols + col_j) % len(BEAM_COLORS)]
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                marker=dict(size=42, color=color,
                            line=dict(width=2, color='#333333'),
                            symbol='circle'),
                text=[f'{row_i+1}.{col_j+1}'],
                textposition='middle center',
                textfont=dict(size=10, color='white', family='Arial Black'),
                showlegend=False,
                hovertemplate=f'Row {row_i+1}, Col {col_j+1}<extra></extra>',
            ))

    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Arial', color='#333333'),
        title=dict(text=f'<b>Beam Grid: {bs["label"]}</b>', font=dict(size=14, color='#333')),
        xaxis=dict(visible=False, range=[-0.8, max_cols - 0.2]),
        yaxis=dict(visible=False, range=[-0.7, n_rows - 0.3], scaleanchor='x'),
        height=200 + n_rows * 55,
        margin=dict(l=10, r=10, t=45, b=15),
        annotations=[
            dict(x=max_cols/2 - 0.5, y=n_rows - 0.15, text='↑ Upper edge (top row)',
                 showarrow=False, font=dict(size=10, color='#888')),
            dict(x=max_cols/2 - 0.5, y=-0.5, text='↓ Lower edge (bottom row)',
                 showarrow=False, font=dict(size=10, color='#888')),
        ]
    )
    return fig


def generate_az_el_heatmap(beam_set_key, ru_type, freq_ghz, d_h_lam, d_v_lam,
                            tilt_offset, az_opening_override,
                            upper_edge_angle, lower_edge_angle,
                            mmimo_ant_array_mode=0,
                            nr_bts_beam_refinement_p2=False,
                            num_dft_beam_mute_right=0,
                            num_dft_beam_mute_left=0,
                            tx_power_w=320.0,
                            rsrp_threshold_dbm=-130.0,
                            antenna_lat=40.75503684862242,
                            antenna_lon=29.94555084488382,
                            antenna_azimuth_deg=0.0,
                            antenna_height_m=30.0,
                            active_beam_ids=None):
    bs = BEAM_SET_DEFS[beam_set_key]
    ru = RU_CONFIGS[ru_type]
    rows = bs["rows"]
    n_rows = len(rows)
    az_opening = az_opening_override if az_opening_override else bs["az_opening"]
    az_half = az_opening / 2

    c = 3e8
    freq = freq_ghz * 1e9
    lam = c / freq
    k = 2 * np.pi / lam
    d_h = d_h_lam * lam
    d_v = d_v_lam * lam
    n_col, n_row = apply_mmimo_array_mode(ru["n_col"], ru["n_row"], mmimo_ant_array_mode)

    if n_rows == 1:
        el_centers = [tilt_offset]
    else:
        el_span = upper_edge_angle - lower_edge_angle
        el_centers = [upper_edge_angle - i * el_span / (n_rows - 1) + tilt_offset
                      for i in range(n_rows)]

    coverage_radius_m = 8000.0
    grid_n = 151
    x_local = np.linspace(-coverage_radius_m, coverage_radius_m, grid_n)
    y_local = np.linspace(-coverage_radius_m, coverage_radius_m, grid_n)
    X, Y = np.meshgrid(x_local, y_local)

    dx = X
    dy = Y
    d2d = np.sqrt(dx**2 + dy**2) + 1e-6
    h_ue = 1.5
    d3d = np.sqrt(d2d**2 + (antenna_height_m - h_ue)**2)

    abs_bearing = np.rad2deg(np.arctan2(dy, dx))
    rel_az = ((abs_bearing - antenna_azimuth_deg + 180) % 360) - 180
    rel_el = np.rad2deg(np.arctan2(h_ue - antenna_height_m, d2d))

    PHI_RAD = np.deg2rad(rel_az)
    THETA_RAD = np.deg2rad(rel_el)

    combined_gain = np.full_like(X, -80.0)
    beam_owner = np.full(X.shape, -1, dtype=int)
    beam_counter = 1

    for row_i, n_beams_in_row in enumerate(rows):
        el_center = el_centers[row_i]
        if n_beams_in_row == 1:
            az_positions = [0.0]
        else:
            step = az_opening / n_beams_in_row
            az_positions = [(-az_half + step/2) + j * step for j in range(n_beams_in_row)]
        az_positions = apply_dft_beam_mute(az_positions, num_dft_beam_mute_left, num_dft_beam_mute_right)

        active_beams_in_row = max(1, len(az_positions))
        az_beam_half = (az_opening / active_beams_in_row) / 2 * 1.3
        el_beam_half = (abs(upper_edge_angle - lower_edge_angle) / max(n_rows, 1)) / 2 * 1.3 if n_rows > 1 else 12

        for az_center in az_positions:
            current_beam_id = beam_counter
            beam_counter += 1
            if active_beam_ids is not None and current_beam_id not in active_beam_ids:
                continue
            for az_ref, el_ref in get_refined_centers(
                az_center, el_center, az_beam_half, el_beam_half, nr_bts_beam_refinement_p2
            ):
                phi_s = np.deg2rad(az_ref)
                theta_s = np.deg2rad(el_ref)
                AF = array_factor_2d(PHI_RAD, THETA_RAD, n_col, n_row, d_h, d_v, k, phi_s, theta_s)
                EP = element_pattern_2d(rel_az, rel_el)
                gain = 20 * np.log10(np.abs(AF) + 1e-12) + EP
                mask = gain > combined_gain
                combined_gain = np.where(mask, gain, combined_gain)
                beam_owner = np.where(mask, current_beam_id, beam_owner)

    pl_los = 32.4 + 21 * np.log10(d3d) + 20 * np.log10(freq_ghz)
    pl_nlos = 13.54 + 39.08 * np.log10(d3d) + 20 * np.log10(freq_ghz) - 0.6 * (h_ue - 1.5)
    path_loss = np.maximum(pl_los, pl_nlos)

    tx_power_dbm = 10 * np.log10(max(tx_power_w, 1e-6) * 1000)
    rx_power_dbm = tx_power_dbm + combined_gain - path_loss

    edge_start_m = coverage_radius_m * 0.78
    edge_norm = np.clip((d2d - edge_start_m) / max(coverage_radius_m - edge_start_m, 1e-6), 0.0, 1.0)
    edge_taper_db = 18.0 * (edge_norm ** 1.6)
    rx_power_dbm = rx_power_dbm - edge_taper_db

    lat_grid, lon_grid = meters_to_latlon(dx, dy, antenna_lat, antenna_lon)
    thr = float(rsrp_threshold_dbm)
    stride = 1 if thr >= -110 else 2
    lat_all = lat_grid[::stride, ::stride].ravel()
    lon_all = lon_grid[::stride, ::stride].ravel()
    rx_all = rx_power_dbm[::stride, ::stride].ravel()
    beam_all = beam_owner[::stride, ::stride].ravel()
    dist_all = d2d[::stride, ::stride].ravel()
    beam_display_all = np.where(beam_all >= 0, beam_all + 1, 0)

    show_mask = rx_all >= thr
    lat_flat = lat_all[show_mask]
    lon_flat = lon_all[show_mask]
    rx_flat = rx_all[show_mask]
    beam_display = beam_display_all[show_mask]
    dist_flat = dist_all[show_mask]

    edge_delta_db = 1.3
    edge_mask = np.abs(rx_all - thr) <= edge_delta_db
    lat_edge = lat_all[edge_mask]
    lon_edge = lon_all[edge_mask]

    fig = go.Figure()
    if len(lat_flat) > 0:
        fig.add_trace(go.Scattermapbox(
            lat=lat_flat,
            lon=lon_flat,
            mode='markers',
            marker=dict(
                size=8,
                color=rx_flat,
                colorscale='Turbo',
                cmin=max(-130, thr),
                cmax=-60,
                opacity=0.80,
                colorbar=dict(
                    title=dict(text='Estimated RSRP [dBm]')
                ),
            ),
            customdata=np.stack([beam_display, rx_flat, dist_flat], axis=1),
            hovertemplate=(
                'Lat: %{lat:.6f}<br>Lon: %{lon:.6f}<br>'
                'Beam ID: %{customdata[0]:.0f}<br>'
                'RSRP: %{customdata[1]:.1f} dBm<br>'
                'Distance to antenna: %{customdata[2]:.0f} m (%{customdata[2]:.2f} km)<extra></extra>'
            ),
            showlegend=False,
        ))
    else:
        fig.add_trace(go.Scattermapbox(
            lat=[antenna_lat],
            lon=[antenna_lon],
            mode='markers',
            marker=dict(size=1, color='rgba(0,0,0,0)'),
            hoverinfo='skip',
            showlegend=False,
        ))

    if len(lat_edge) > 0:
        fig.add_trace(go.Scattermapbox(
            lat=lat_edge,
            lon=lon_edge,
            mode='markers',
            marker=dict(size=9, color='rgba(255,255,255,0.85)'),
            hoverinfo='skip',
            showlegend=False,
        ))
        fig.add_trace(go.Scattermapbox(
            lat=lat_edge,
            lon=lon_edge,
            mode='markers',
            marker=dict(size=4, color='rgba(0,0,0,0.85)'),
            hoverinfo='skip',
            showlegend=False,
        ))

    fig.add_trace(go.Scattermapbox(
        lat=[antenna_lat], lon=[antenna_lon],
        mode='markers+text',
        marker=dict(size=12, color='#111111'),
        text=['Antenna'], textposition='top right',
        hovertemplate='Antenna Site<br>Lat: %{lat:.6f}<br>Lon: %{lon:.6f}<extra></extra>',
        showlegend=False,
    ))

    direction_len = coverage_radius_m * 0.35
    dx_dir = direction_len * np.cos(np.deg2rad(antenna_azimuth_deg))
    dy_dir = direction_len * np.sin(np.deg2rad(antenna_azimuth_deg))
    lat_dir, lon_dir = meters_to_latlon(np.array([0.0, dx_dir]), np.array([0.0, dy_dir]), antenna_lat, antenna_lon)
    fig.add_trace(go.Scattermapbox(
        lat=lat_dir.tolist(), lon=lon_dir.tolist(),
        mode='lines', line=dict(width=4, color='#111111'),
        hoverinfo='skip', showlegend=False,
    ))

    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Arial', size=12, color='#333333'),
        title=dict(
            text=(
                '<b>Estimated Ground Coverage (Path Loss + Beam Gain)</b>'
                f'<br><span style="font-size:11px;color:#666">'
                f'Tx: {tx_power_w:.0f} W ({tx_power_dbm:.1f} dBm) | '
                f'3GPP UMa simplified path loss | f={freq_ghz:.1f} GHz</span>'
            ),
            font=dict(size=14, color='#333')
        ),
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=antenna_lat, lon=antenna_lon),
            zoom=11,
            pitch=72,
            bearing=float(antenna_azimuth_deg),
        ),
        height=980,
        margin=dict(l=55, r=20, t=60, b=45),
    )
    return fig


# ============================================================
# DASH APP — LIGHT THEME
# ============================================================
app = Dash(__name__,
           external_stylesheets=[dbc.themes.FLATLY],
           title="5G NR Beamforming 3D Simulator")
server = app.server

controls_card = dbc.Card([
    dbc.CardHeader(
        html.H5("⚙️ Nokia Beamforming Configuration", id="controls_title", className="mb-0",
                style={"color": "#1a1a1a", "fontWeight": "bold"}),
        style={"backgroundColor": "#F0F4F8"}
    ),
    dbc.CardBody([
        html.Label("Vendor", className="fw-bold mt-1", style={"color": "#333", "fontSize": "13px"}),
        dcc.Dropdown(id="vendor", options=[{"label": v, "value": v} for v in VENDOR_OPTIONS],
                     value="Nokia", clearable=False, className="mb-2"),

        html.Label("Radio Unit Type", id="label_ru_type", className="fw-bold mt-1", style={"color": "#333", "fontSize": "13px"}),
        dcc.Dropdown(id="ru_type", options=[{"label": k, "value": k} for k in RU_CONFIGS],
                     value="64T64R", clearable=False, className="mb-2"),

        html.Label("Beam Set (basicBeamSet)", id="label_beam_set", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Dropdown(id="beam_set", options=[{"label": f'{v["label"]}  ({k})', "value": k} for k, v in BEAM_SET_DEFS.items()],
                     value="beamSet_3_3_2_square", clearable=False, className="mb-2"),

        html.Hr(style={"borderColor": "#DDD"}),
        html.Label("Carrier Frequency (GHz)", id="label_carrier_freq", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="freq_ghz", min=2.5, max=6.0, step=0.1, value=3.5,
                   marks={2.5: "2.5", 3.5: "3.5", 4.5: "4.5", 6.0: "6.0"}, tooltip={"placement": "bottom"}),

        html.Label("Horizontal Spacing d_h (λ)", id="label_d_h", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="d_h_lam", min=0.3, max=1.0, step=0.05, value=0.5,
                   marks={0.3: "0.3", 0.5: "0.5λ", 0.7: "0.7", 1.0: "1.0"}, tooltip={"placement": "bottom"}),

        html.Label("Vertical Spacing d_v (λ)", id="label_d_v", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="d_v_lam", min=0.3, max=1.2, step=0.05, value=0.7,
                   marks={0.3: "0.3", 0.5: "0.5", 0.7: "0.7λ", 1.2: "1.2"}, tooltip={"placement": "bottom"}),

        html.Hr(style={"borderColor": "#DDD"}),
        html.H6("📐 Beam Steering & Tilt", id="label_steering_title", style={"color": "#1a1a1a", "fontWeight": "bold"}),
        html.Label("Tilt Offset (°)", id="label_tilt_offset", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="tilt_offset", min=-13, max=13, step=0.5, value=0,
                   marks={-13: "-13", -6: "-6", 0: "0", 6: "6", 13: "13"}, tooltip={"placement": "bottom"}),

        html.Label("Upper Edge Angle (°)", id="label_upper_edge", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="upper_edge", min=0, max=15, step=0.5, value=8,
                   marks={0: "0", 4: "4", 8: "8", 12: "12", 15: "15"}, tooltip={"placement": "bottom"}),

        html.Label("Lower Edge Angle (°)", id="label_lower_edge", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="lower_edge", min=-10, max=0, step=0.5, value=-4,
                   marks={-10: "-10", -6: "-6", -4: "-4", 0: "0"}, tooltip={"placement": "bottom"}),

        html.Label("NRCELL-beamSet.leftEdgeAngle (°)", id="label_left_edge", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="left_edge", min=0, max=90, step=1, value=45,
                   marks={0: "0", 30: "30", 45: "45", 60: "60", 90: "90"}, tooltip={"placement": "bottom"}),

        html.Label("NRCELL-beamSet.rightEdgeAngle (°)", id="label_right_edge", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="right_edge", min=0, max=90, step=1, value=45,
                   marks={0: "0", 30: "30", 45: "45", 60: "60", 90: "90"}, tooltip={"placement": "bottom"}),

        html.Hr(style={"borderColor": "#DDD"}),
        html.H6("🧩 Nokia Advanced Beamforming Parameters", style={"color": "#1a1a1a", "fontWeight": "bold"}),
        html.Label("NRCELL-beamSet.nrBtsBeamRefinementP2", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Dropdown(id="nr_bts_beam_refinement_p2", options=[{"label": "false", "value": False}, {"label": "true", "value": True}],
                     value=False, clearable=False, className="mb-2"),

        html.Label("mMIMOAntArrayMode", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Dropdown(id="mmimo_ant_array_mode", options=[{"label": str(v), "value": v} for v in range(0, 8)],
                     value=0, clearable=False, className="mb-2"),

        html.Label("NRCELL.numDftBeamMuteRight", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="num_dft_beam_mute_right", min=0, max=32, step=1, value=0,
                   marks={0: "0", 8: "8", 16: "16", 24: "24", 32: "32"}, tooltip={"placement": "bottom"}),

        html.Label("NRCELL.numDftBeamMuteLeft", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="num_dft_beam_mute_left", min=0, max=32, step=1, value=0,
                   marks={0: "0", 8: "8", 16: "16", 24: "24", 32: "32"}, tooltip={"placement": "bottom"}),

        html.Hr(style={"borderColor": "#DDD"}),
        html.H6("🏗️ Antenna Installation", id="label_install_title", style={"color": "#1a1a1a", "fontWeight": "bold"}),
        html.Label("Antenna Height AGL (m)", id="label_antenna_height", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="antenna_height", min=5, max=80, step=1, value=30,
                   marks={5: "5m", 15: "15m", 25: "25m", 30: "30m", 40: "40m", 50: "50m", 60: "60m", 80: "80m"},
                   tooltip={"placement": "bottom"}),

        html.Label("RU Tx Power (W)", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="tx_power_w", min=20, max=640, step=10, value=320,
                   marks={20: "20", 80: "80", 160: "160", 320: "320", 640: "640"}, tooltip={"placement": "bottom"}),

        html.Label("Antenna Coordinate (lat, lon)", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Input(id="antenna_coord", type="text", value="40.75503684862242, 29.94555084488382", className="mb-2", style={"width": "100%"}),

        html.Label("Antenna Azimuth Bearing (°)", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
        dcc.Slider(id="antenna_azimuth_deg", min=0, max=359, step=1, value=0,
                   marks={0: "0", 90: "90", 180: "180", 270: "270", 359: "359"}, tooltip={"placement": "bottom"}),
    ], style={"backgroundColor": "#FFFFFF"})
], className="mb-3 shadow-sm", style={"border": "1px solid #DEE2E6"})

info_card = dbc.Card([
    dbc.CardHeader(
        html.H5("📊 Beam Set Info", className="mb-0", style={"color": "#1a1a1a", "fontWeight": "bold"}),
        style={"backgroundColor": "#F0F4F8"}
    ),
    dbc.CardBody(id="info_panel", style={"backgroundColor": "#FFFFFF"})
], className="mb-3 shadow-sm", style={"border": "1px solid #DEE2E6"})

app.layout = dbc.Container([
    dcc.Store(id="prev_params_store"),
    dcc.Store(id="active_beams_store"),
    dbc.Row([
        dbc.Col([
            html.H2("📡 Nokia 5G NR Beamforming 3D Simulator", id="app_title", className="text-center my-3", style={"color": "#1565C0", "fontWeight": "bold"}),
            html.P("Nokia-style 3D beam visualization — see how beam set parameters affect beam patterns",
                   id="app_subtitle", className="text-center mb-4", style={"color": "#666666", "fontSize": "14px"}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([controls_card, info_card], width=3, className="pe-1"),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="beam_3d", config={"displayModeBar": True}, style={"height": "48vh"}),
                        ], style={"backgroundColor": "#FFFFFF"})
                    ], className="shadow-sm", style={"border": "1px solid #DEE2E6"}),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="beam_grid", config={"displayModeBar": False}, style={"height": "48vh"}),
                        ], style={"backgroundColor": "#FFFFFF"})
                    ], className="shadow-sm", style={"border": "1px solid #DEE2E6"}),
                ], width=6),
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.Label("RSRP Visibility Threshold (dBm)", className="fw-bold", style={"color": "#333", "fontSize": "13px"}),
                    dcc.Slider(id="rsrp_threshold_dbm", min=-156, max=-55, step=1, value=-130,
                               marks={-156: "-156", -140: "-140", -130: "-130", -110: "-110", -90: "-90", -70: "-70", -55: "-55"},
                               tooltip={"placement": "bottom"}),
                    dcc.Graph(id="beam_heatmap", config={"displayModeBar": True, "scrollZoom": True}, style={"height": "86vh"}),
                ], style={"backgroundColor": "#FFFFFF"})
            ], className="shadow-sm", style={"border": "1px solid #DEE2E6"}),
        ], width=9, className="ps-1"),
    ]),
], fluid=True, style={"backgroundColor": "#F5F7FA", "minHeight": "100vh"})


# --- CALLBACKS ---
@app.callback(
    Output("controls_title", "children"),
    Output("label_ru_type", "children"),
    Output("label_beam_set", "children"),
    Output("label_carrier_freq", "children"),
    Output("label_d_h", "children"),
    Output("label_d_v", "children"),
    Output("label_steering_title", "children"),
    Output("label_tilt_offset", "children"),
    Output("label_upper_edge", "children"),
    Output("label_lower_edge", "children"),
    Output("label_left_edge", "children"),
    Output("label_right_edge", "children"),
    Output("label_install_title", "children"),
    Output("label_antenna_height", "children"),
    Output("app_title", "children"),
    Output("app_subtitle", "children"),
    Input("vendor", "value"),
)
def update_terminology(vendor):
    terms = get_terms(vendor)
    return (
        terms["controls_title"],
        terms["ru_type"],
        terms["beam_set"],
        terms["carrier_freq"],
        terms["d_h"],
        terms["d_v"],
        terms["steering_title"],
        terms["tilt_offset"],
        terms["upper_edge"],
        terms["lower_edge"],
        terms["left_edge"],
        terms["right_edge"],
        terms["install_title"],
        terms["antenna_height"],
        f"📡 {vendor} 5G NR Beamforming 3D Simulator",
        (
            f"{vendor}-style 3D beam visualization — see how beam set parameters affect beam patterns"
            if vendor == "Nokia"
            else f"{vendor} terminology profile pending — using generic naming until documentation is provided"
        ),
    )


@app.callback(
    Output("active_beams_store", "data"),
    Input("beam_3d", "restyleData"),
    State("beam_3d", "figure"),
    State("active_beams_store", "data"),
    prevent_initial_call=True,
)
def sync_active_beams_from_legend(restyle_data, beam_figure, current_store):
    if not beam_figure or "data" not in beam_figure:
        return current_store

    active = set()
    all_beams = set()
    for trace in beam_figure.get("data", []):
        name = trace.get("name", "")
        if not isinstance(name, str):
            continue
        m = re.match(r"^Beam\s+(\d+)", name)
        if not m:
            continue

        beam_id = int(m.group(1))
        all_beams.add(beam_id)
        visible = trace.get("visible", True)
        if visible is True or visible is None:
            active.add(beam_id)

    if not all_beams:
        return current_store

    return {
        "all_beams": sorted(all_beams),
        "active_beams": sorted(active),
    }


@app.callback(
    Output("beam_3d", "figure"),
    Output("beam_grid", "figure"),
    Output("beam_heatmap", "figure"),
    Output("info_panel", "children"),
    Output("prev_params_store", "data"),
    Input("vendor", "value"),
    Input("ru_type", "value"),
    Input("beam_set", "value"),
    Input("freq_ghz", "value"),
    Input("d_h_lam", "value"),
    Input("d_v_lam", "value"),
    Input("tilt_offset", "value"),
    Input("upper_edge", "value"),
    Input("lower_edge", "value"),
    Input("left_edge", "value"),
    Input("right_edge", "value"),
    Input("nr_bts_beam_refinement_p2", "value"),
    Input("mmimo_ant_array_mode", "value"),
    Input("num_dft_beam_mute_right", "value"),
    Input("num_dft_beam_mute_left", "value"),
    Input("antenna_height", "value"),
    Input("tx_power_w", "value"),
    Input("rsrp_threshold_dbm", "value"),
    Input("antenna_coord", "value"),
    Input("antenna_azimuth_deg", "value"),
    Input("active_beams_store", "data"),
    State("prev_params_store", "data"),
)
def update_all(vendor, ru_type, beam_set, freq_ghz, d_h_lam, d_v_lam,
               tilt_offset, upper_edge, lower_edge, left_edge, right_edge,
               nr_bts_beam_refinement_p2, mmimo_ant_array_mode,
               num_dft_beam_mute_right,
               num_dft_beam_mute_left, antenna_height,
               tx_power_w, rsrp_threshold_dbm, antenna_coord, antenna_azimuth_deg, active_beams_store,
               prev_params_store):

    lobe_scale = 1.0
    gain_threshold = 6
    n_pts = 50
    antenna_lat, antenna_lon = parse_lat_lon(antenna_coord)
    active_beam_ids = set(active_beams_store.get("active_beams", [])) if isinstance(active_beams_store, dict) and active_beams_store.get("active_beams") else None

    current_params = {
        "vendor": vendor,
        "ru_type": ru_type,
        "beam_set": beam_set,
        "freq_ghz": freq_ghz,
        "d_h_lam": d_h_lam,
        "d_v_lam": d_v_lam,
        "tilt_offset": tilt_offset,
        "upper_edge": upper_edge,
        "lower_edge": lower_edge,
        "left_edge": left_edge,
        "right_edge": right_edge,
        "nr_bts_beam_refinement_p2": nr_bts_beam_refinement_p2,
        "mmimo_ant_array_mode": mmimo_ant_array_mode,
        "num_dft_beam_mute_right": num_dft_beam_mute_right,
        "num_dft_beam_mute_left": num_dft_beam_mute_left,
        "antenna_height": antenna_height,
        "tx_power_w": tx_power_w,
        "rsrp_threshold_dbm": rsrp_threshold_dbm,
        "antenna_coord": antenna_coord,
        "antenna_lat": antenna_lat,
        "antenna_lon": antenna_lon,
        "antenna_azimuth_deg": antenna_azimuth_deg,
        "active_beams": sorted(active_beam_ids) if active_beam_ids else None,
    }

    prev_params = (prev_params_store or {}).get("last_params") if isinstance(prev_params_store, dict) else None
    ghost_available = isinstance(prev_params, dict) and prev_params != current_params

    bs = BEAM_SET_DEFS[beam_set]
    ru = RU_CONFIGS[ru_type]
    total_beams = sum(bs["rows"])
    n_rows = len(bs["rows"])
    az_opening = (left_edge or 0) + (right_edge or 0)
    az_op = az_opening if az_opening > 0 else bs["az_opening"]

    fig_3d = generate_beam_set_figure(
        beam_set, ru_type, freq_ghz, d_h_lam, d_v_lam,
        tilt_offset, az_op,
        n_pts, gain_threshold, False, lobe_scale,
        upper_edge, lower_edge, float(antenna_height), vendor,
        mmimo_ant_array_mode, nr_bts_beam_refinement_p2,
        num_dft_beam_mute_right, num_dft_beam_mute_left,
        0.0, 0.0, float(antenna_azimuth_deg or 0),
        active_beam_ids,
    )

    if ghost_available:
        prev_az_opening = (prev_params.get("left_edge", 0) or 0) + (prev_params.get("right_edge", 0) or 0)
        ghost_fig = generate_beam_set_figure(
            prev_params.get("beam_set", beam_set),
            prev_params.get("ru_type", ru_type),
            prev_params.get("freq_ghz", freq_ghz),
            prev_params.get("d_h_lam", d_h_lam),
            prev_params.get("d_v_lam", d_v_lam),
            prev_params.get("tilt_offset", tilt_offset),
            prev_az_opening if prev_az_opening > 0 else None,
            prev_params.get("n_pts", n_pts),
            prev_params.get("gain_threshold", gain_threshold),
            False,
            prev_params.get("lobe_scale", lobe_scale),
            prev_params.get("upper_edge", upper_edge),
            prev_params.get("lower_edge", lower_edge),
            float(prev_params.get("antenna_height", antenna_height)),
            prev_params.get("vendor", vendor),
            prev_params.get("mmimo_ant_array_mode", mmimo_ant_array_mode),
            prev_params.get("nr_bts_beam_refinement_p2", nr_bts_beam_refinement_p2),
            prev_params.get("num_dft_beam_mute_right", num_dft_beam_mute_right),
            prev_params.get("num_dft_beam_mute_left", num_dft_beam_mute_left),
            0.0,
            0.0,
            float(prev_params.get("antenna_azimuth_deg", antenna_azimuth_deg) or 0),
            set(prev_params.get("active_beams", [])) if prev_params.get("active_beams") else None,
        )

        for tr in ghost_fig.data:
            if getattr(tr, "type", "") == "surface":
                fig_3d.add_trace(go.Surface(
                    x=tr.x,
                    y=tr.y,
                    z=tr.z,
                    surfacecolor=tr.surfacecolor,
                    colorscale=[[0, "#5C5C5C"], [1, "#A0A0A0"]],
                    opacity=0.18,
                    showscale=False,
                    name="Previous pattern (ghost)",
                    hoverinfo="skip",
                    showlegend=False,
                ))

        fig_3d.update_layout(
            title=dict(
                text=(fig_3d.layout.title.text +
                      '<br><span style="font-size:11px;color:#757575">Ghost overlay: previous parameter set</span>')
            )
        )

    fig_grid = generate_beam_grid_diagram(
        beam_set, num_dft_beam_mute_right, num_dft_beam_mute_left
    )

    fig_heatmap = generate_az_el_heatmap(
        beam_set, ru_type, freq_ghz, d_h_lam, d_v_lam,
        tilt_offset, az_op,
        upper_edge, lower_edge,
        mmimo_ant_array_mode,
        nr_bts_beam_refinement_p2,
        num_dft_beam_mute_right,
        num_dft_beam_mute_left,
        float(tx_power_w or 0),
        float(rsrp_threshold_dbm or -130),
        float(antenna_lat),
        float(antenna_lon),
        float(antenna_azimuth_deg or 0),
        float(antenna_height or 0),
        active_beam_ids,
    )

    c = 3e8
    lam = c / (freq_ghz * 1e9)
    tx_power_dbm = 10 * np.log10(max(float(tx_power_w or 0), 1e-6) * 1000)
    bw_az = np.rad2deg(0.886 * lam / (ru["n_col"] * d_h_lam * lam + 1e-6))
    bw_el = np.rad2deg(0.886 * lam / (ru["n_row"] * d_v_lam * lam + 1e-6))

    table_style = {"fontSize": "13px", "color": "#333"}
    td_label_style = {"padding": "3px 10px 3px 0", "color": "#555", "fontWeight": "normal"}
    td_value_style = {"padding": "3px 0", "fontWeight": "bold", "color": "#1a1a1a"}
    terms = get_terms(vendor)
    changed_control = callback_context.triggered[0]["prop_id"].split(".")[0] if callback_context.triggered else "none"
    ghost_status = "ON" if ghost_available else "Waiting for first parameter change"

    info = html.Div([
        html.Table([
            html.Tr([html.Td("Comparison Mode", style=td_label_style),
                     html.Td(f"Ghost overlay: {ghost_status}", style=td_value_style)]),
            html.Tr([html.Td("Last Changed Control", style=td_label_style),
                     html.Td(changed_control, style=td_value_style)]),
            html.Tr([html.Td(terms["info_vendor"], style=td_label_style),
                     html.Td(vendor, style=td_value_style)]),
            html.Tr([html.Td(terms["info_beam_set"], style=td_label_style),
                     html.Td(bs["label"], style=td_value_style)]),
            html.Tr([html.Td(terms["info_total_beams"], style=td_label_style),
                     html.Td(str(total_beams), style=td_value_style)]),
            html.Tr([html.Td(terms["info_rows"], style=td_label_style),
                     html.Td(str(n_rows), style=td_value_style)]),
            html.Tr([html.Td(terms["info_beams_per_row"], style=td_label_style),
                     html.Td(" × ".join(str(r) for r in bs["rows"]), style=td_value_style)]),
            html.Tr([html.Td(terms["info_az_opening"], style=td_label_style),
                     html.Td(f"{az_op}°", style=td_value_style)]),
            html.Tr([html.Td("NRCELL-beamSet.leftEdgeAngle", style=td_label_style),
                     html.Td(f"{left_edge}°", style=td_value_style)]),
            html.Tr([html.Td("NRCELL-beamSet.rightEdgeAngle", style=td_label_style),
                     html.Td(f"{right_edge}°", style=td_value_style)]),
            html.Tr([html.Td(terms["info_ru_array"], style=td_label_style),
                     html.Td(f"{ru['n_col']}×{ru['n_row']}", style=td_value_style)]),
            html.Tr([html.Td(terms["info_lambda"], style=td_label_style),
                     html.Td(f"{lam*1000:.1f} mm", style=td_value_style)]),
            html.Tr([html.Td(terms["info_az_bw"], style=td_label_style),
                     html.Td(f"{bw_az:.1f}°", style=td_value_style)]),
            html.Tr([html.Td(terms["info_el_bw"], style=td_label_style),
                     html.Td(f"{bw_el:.1f}°", style=td_value_style)]),
            html.Tr([html.Td(terms["info_el_range"], style=td_label_style),
                     html.Td(f"{lower_edge}° to {upper_edge}°", style=td_value_style)]),
            html.Tr([html.Td(terms["info_tilt"], style=td_label_style),
                     html.Td(f"{tilt_offset}°", style=td_value_style)]),
            html.Tr([html.Td(terms["info_height"], style={**td_label_style, "color": "#D32F2F"}),
                     html.Td(f"{antenna_height} m AGL",
                             style={**td_value_style, "color": "#D32F2F"})]),
                html.Tr([html.Td("RU Tx Power", style=td_label_style),
                     html.Td(f"{tx_power_w:.0f} W ({tx_power_dbm:.1f} dBm)", style=td_value_style)]),
                html.Tr([html.Td("RSRP Display Threshold", style=td_label_style),
                         html.Td(f"{float(rsrp_threshold_dbm):.0f} dBm", style=td_value_style)]),
                html.Tr([html.Td("Antenna Coordinates", style=td_label_style),
                         html.Td(f"{antenna_lat:.8f}, {antenna_lon:.8f}", style=td_value_style)]),
                html.Tr([html.Td("Antenna Azimuth Bearing", style=td_label_style),
                     html.Td(f"{float(antenna_azimuth_deg or 0):.1f}°", style=td_value_style)]),
            html.Tr([html.Td("NRCELL-beamSet.nrBtsBeamRefinementP2", style=td_label_style),
                     html.Td(str(nr_bts_beam_refinement_p2).lower(), style=td_value_style)]),
            html.Tr([html.Td("mMIMOAntArrayMode", style=td_label_style),
                     html.Td(str(mmimo_ant_array_mode), style=td_value_style)]),
            html.Tr([html.Td("NRCELL.numDftBeamMuteRight", style=td_label_style),
                     html.Td(str(num_dft_beam_mute_right), style=td_value_style)]),
            html.Tr([html.Td("NRCELL.numDftBeamMuteLeft", style=td_label_style),
                     html.Td(str(num_dft_beam_mute_left), style=td_value_style)]),
        ], style={"width": "100%", "borderCollapse": "collapse"}),
    ])

    return fig_3d, fig_grid, fig_heatmap, info, {"last_params": current_params}


if __name__ == "__main__":
    app.run(debug=True, port=8051)
