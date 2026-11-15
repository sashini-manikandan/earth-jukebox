import base64
import io
import json
import os
import tempfile

import imageio.v3 as iio
import matplotlib.pyplot as plt
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
from scipy.io import wavfile

# ---------------------------------------------------------------------
# EARTH//SOUND — NASA Earth Information Center (EIC) Multi-Sensory Jukebox
# Real-time Web Audio browser synthesis + Python WAV export + Multimodal AI
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="EARTH//SOUND | NASA EIC Multi-Sensory Jukebox",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

NASA_API = "https://svs.gsfc.nasa.gov/api"

CATALOG = {
    "Global Sea Surface Currents & Temperature": {
        "id": 3912,
        "theme": "OCEAN",
        "default_profile": "Ocean currents & temperature",
        "legend_hint": (-2.0, 32.0, "°C"),
        "layman_planet": (
            "Oceans are Earth's giant heating and cooling conveyor belt. Warm currents carry heat "
            "from the tropics toward the poles—when those currents warm up or shift, they reshape "
            "rainfall, coastal weather, and storm intensity around the world."
        ),
        "summary": (
            "Ocean surface currents coloured by sea-surface temperature using "
            "NASA ECCO2 model output synthesizing satellite and in-situ observations."
        ),
        "mapping": (
            "Colour and brightness act as visual proxies for the rendered thermal "
            "palette; latitude bands separate polar vs. equatorial currents across octaves."
        ),
        "source": "https://svs.gsfc.nasa.gov/3912/",
    },
    "Perpetual Ocean 2: Western Boundary Currents": {
        "id": 5425,
        "theme": "OCEAN FLOWS",
        "default_profile": "Ocean currents & temperature",
        "legend_hint": (0.0, 2.0, "m/s"),
        "layman_planet": (
            "Fast-moving ocean 'rivers' like the Gulf Stream and Kuroshio Current transport huge "
            "amounts of heat and nutrients along coastlines, regulating regional climates and marine ecosystems."
        ),
        "summary": (
            "High-contrast ECCO-2 visualization (2021–2023) of major western boundary "
            "currents including the Kuroshio, Agulhas, and Gulf Stream."
        ),
        "mapping": (
            "High-contrast flow filaments drive edge-weighted harmonic richness and "
            "rhythmic pulse across stereo longitude."
        ),
        "source": "https://svs.gsfc.nasa.gov/5425/",
    },
    "Change in Night Lights (2012–2023)": {
        "id": 5313,
        "theme": "HUMAN ACTIVITY",
        "default_profile": "Night lights & urban change",
        "legend_hint": (0.0, 100.0, "% radiance proxy"),
        "layman_planet": (
            "Tracking Earth's glow at night shows where cities are growing, where new electricity grids "
            "are reaching communities, and how human infrastructure is expanding across the planet."
        ),
        "summary": (
            "NASA Black Marble visualization comparing annual nighttime illumination "
            "from 2012 to 2023 to highlight urban growth and shifting human activity."
        ),
        "mapping": (
            "Bright-pixel occupancy controls note presence and pitch, while clustered "
            "urban boundaries trigger crisp transient accents."
        ),
        "source": "https://svs.gsfc.nasa.gov/5313/",
    },
    "DYAMOND Global Carbon Dioxide": {
        "id": 5196,
        "theme": "ATMOSPHERE",
        "default_profile": "Atmosphere & aerosols",
        "legend_hint": (405.0, 425.0, "ppm CO₂"),
        "layman_planet": (
            "Carbon dioxide acts like an invisible thermal blanket trapping heat around Earth. "
            "This map reveals how global winds swirl emissions from cities and forests across entire oceans in days."
        ),
        "summary": (
            "Global atmospheric CO₂ plumes (Jan–Mar 2020) illustrating how weather "
            "systems and jet streams transport carbon around Earth."
        ),
        "mapping": (
            "Colour saturation and plume gradients modulate harmonic texture and "
            "ambient choir swell as visual proxies (not calibrated ppm values)."
        ),
        "source": "https://svs.gsfc.nasa.gov/5196/",
    },
    "GEDI Forest Height": {
        "id": 4950,
        "theme": "BIODIVERSITY",
        "default_profile": "Forest canopy (colour proxy)",
        "legend_hint": (0.0, 50.0, "m canopy"),
        "layman_planet": (
            "Taller, older forests store massive amounts of carbon and shelter most of Earth's land wildlife. "
            "Measuring tree height from space helps scientists see where Earth's 'green lungs' are thriving or shrinking."
        ),
        "summary": (
            "Global canopy elevation map from NASA's GEDI lidar mission on the ISS, "
            "depicting shorter vegetation in darker tones and taller forests in bright greens/whites."
        ),
        "mapping": (
            "Green dominance and brightness serve as visual height-category proxies "
            "mapped to pitch register, not direct canopy height in metres."
        ),
        "source": "https://svs.gsfc.nasa.gov/4950/",
    },
    "Air Quality Model Runs (GEOS-CF)": {
        "id": 5533,
        "theme": "AIR QUALITY",
        "default_profile": "Atmosphere & aerosols",
        "legend_hint": (0.0, 100.0, "AQI proxy"),
        "layman_planet": (
            "The air we breathe connects every continent. This visualization tracks everyday pollutants "
            "like smoke, ozone, and exhaust as weather systems carry them across borders."
        ),
        "summary": (
            "NASA GEOS-CF model visualization tracking carbon monoxide, PM2.5, ozone, "
            "and nitrogen oxides across Earth's atmosphere."
        ),
        "mapping": (
            "Rendered colour saturation and spatial edge gradients drive multi-band "
            "harmonic textures as a visual proxy."
        ),
        "source": "https://svs.gsfc.nasa.gov/5533/",
    },
    "GEOS Aerosols": {
        "id": 5669,
        "theme": "ATMOSPHERE",
        "default_profile": "Atmosphere & aerosols",
        "legend_hint": (0.0, 1.5, "AOD proxy"),
        "layman_planet": (
            "Tiny airborne particles—like wildfire smoke, Sahara desert dust, and ocean sea spray—travel "
            "thousands of miles, influencing cloud formation, sunlight, and air quality worldwide."
        ),
        "summary": (
            "NASA GEOS global visualization of atmospheric aerosols including smoke, "
            "mineral dust, and sea salt carried by planetary winds."
        ),
        "mapping": (
            "Multi-layered colour fields and spatial dispersion shape timbre and "
            "stereo movement across latitude bands."
        ),
        "source": "https://svs.gsfc.nasa.gov/5669/",
    },
    "Lightning Events from the ISS (2017–2023)": {
        "id": 5011,
        "theme": "WEATHER",
        "default_profile": "Lightning & transient events",
        "legend_hint": (0.0, 100.0, "flash density proxy"),
        "layman_planet": (
            "Lightning is a direct pulse of storm energy in our atmosphere. Watching where flashes cluster "
            "helps meteorologists track severe weather hotspots as the planet warms."
        ),
        "summary": (
            "Global lightning flashes detected by the Lightning Imaging Sensor aboard "
            "the International Space Station between 2017 and 2023."
        ),
        "mapping": (
            "High-luminance peaks trigger punctuated percussive chimes and crystalline "
            "transients mapped to latitude and stereo longitude."
        ),
        "source": "https://svs.gsfc.nasa.gov/5011/",
    },
    "Atmospheric River (3D Earth System Model)": {
        "id": 4960,
        "theme": "WATER CYCLE",
        "default_profile": "Ocean currents & temperature",
        "legend_hint": (0.0, 60.0, "kg/m² vapour"),
        "layman_planet": (
            "Atmospheric rivers are narrow 'sky rivers' carrying more water vapour than the Amazon River. "
            "They bring vital rain and snow to coastlines—or trigger major flooding when they stall."
        ),
        "summary": (
            "3D NASA Earth System Model visualization showing narrow corridors of "
            "concentrated water vapour transporting moisture across oceans."
        ),
        "mapping": (
            "Spatial contrast and moisture-plume brightness shape flowing legato "
            "voices and choir resonance."
        ),
        "source": "https://svs.gsfc.nasa.gov/4960/",
    },
}

SCALES = {
    "Lydian (Cosmic Wonder)": [0, 2, 4, 6, 7, 9, 11],
    "Pentatonic (Meditative Earth)": [0, 2, 4, 7, 9],
    "Dorian (Oceanic Mystery)": [0, 2, 3, 5, 7, 9, 10],
    "Harmonic Minor (Climate Urgency)": [0, 2, 3, 5, 7, 8, 11],
}


# ---------------------------------------------------------------------
# NASA Data Retrieval & Fallbacks
# ---------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_svs_page(page_id: int):
    url = f"{NASA_API}/{page_id}/"
    response = requests.get(url, timeout=20, headers={"User-Agent": "EarthSoundJukebox/3.1"})
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_image_bytes(url: str):
    response = requests.get(url, timeout=30, headers={"User-Agent": "EarthSoundJukebox/3.1"})
    response.raise_for_status()
    return response.content


def generate_offline_fallback_image(title: str) -> Image.Image:
    w, h = 640, 320
    x = np.linspace(0, 4 * np.pi, w)
    y = np.linspace(0, 2 * np.pi, h)
    xx, yy = np.meshgrid(x, y)
    wave = 0.5 + 0.3 * np.sin(xx + np.cos(yy * 1.5)) + 0.2 * np.cos(yy * 2.0 - xx * 0.5)
    wave = np.clip(wave, 0, 1)
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[:, :, 0] = (wave ** 2 * 235).astype(np.uint8)
    rgb[:, :, 1] = (np.sin(wave * np.pi) * 210).astype(np.uint8)
    rgb[:, :, 2] = ((1.0 - wave * 0.6) * 220).astype(np.uint8)
    img = Image.fromarray(rgb, mode="RGB")
    draw = ImageDraw.Draw(img)
    draw.text((16, 14), f"OFFLINE DEMO PROXY: {title}", fill=(255, 255, 255))
    return img


def choose_preview_image(page_data):
    main = page_data.get("main_image") or {}
    if main.get("url"):
        return main["url"]
    for group in page_data.get("media_groups", []):
        for item in group.get("items", []):
            instance = item.get("instance") or {}
            if instance.get("media_type") == "Image" and instance.get("url"):
                return instance["url"]
    return None


def choose_small_video(page_data):
    candidates = []
    for group in page_data.get("media_groups", []):
        for item in group.get("items", []):
            instance = item.get("instance") or {}
            url = instance.get("url", "")
            if instance.get("media_type") == "Movie" and url.lower().endswith(".mp4"):
                filename = instance.get("filename", "").lower()
                score = 0
                if "1080" in filename:
                    score += 4
                if "720" in filename:
                    score += 3
                if "2160" in filename or "4k" in filename:
                    score -= 2
                if "5760" in filename or "7680" in filename:
                    score -= 5
                candidates.append((score, url))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def download_video_limited(url: str, max_mb: int = 60):
    response = requests.get(
        url, stream=True, timeout=(15, 90),
        headers={"User-Agent": "EarthSoundJukebox/3.1"},
    )
    response.raise_for_status()
    length = response.headers.get("content-length")
    if length and int(length) > max_mb * 1024 * 1024:
        response.close()
        raise ValueError(f"NASA video exceeds the {max_mb} MB download limit.")
    data = bytearray()
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            data.extend(chunk)
            if len(data) > max_mb * 1024 * 1024:
                response.close()
                raise ValueError(f"Video exceeded the {max_mb} MB safety limit.")
    response.close()
    return bytes(data)


def extract_sampled_frames(video_bytes: bytes, max_frames: int = 16):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        path = tmp.name
    try:
        frames = []
        meta = iio.immeta(path, plugin="FFMPEG")
        raw_total = meta.get("nframes")
        try:
            total = int(raw_total) if raw_total is not None and np.isfinite(float(raw_total)) else 0
        except (TypeError, ValueError, OverflowError):
            total = 0
        if total <= 0:
            fps = float(meta.get("fps") or 30)
            duration = float(meta.get("duration") or 0)
            total = max(1, int(fps * duration))
        if total <= 1:
            for frame in iio.imiter(path, plugin="FFMPEG"):
                frames.append(np.asarray(frame))
                break
        else:
            indices = np.linspace(0, max(total - 1, 0), min(max_frames, total), dtype=int)
            wanted = set(indices.tolist())
            for index, frame in enumerate(iio.imiter(path, plugin="FFMPEG")):
                if index in wanted:
                    frames.append(np.asarray(frame))
                if index > indices[-1]:
                    break
        if not frames:
            raise ValueError("No frames could be decoded from this video.")
        return [Image.fromarray(f).convert("RGB") for f in frames]
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


# ---------------------------------------------------------------------
# 2D Computer Vision & Feature Extraction
# ---------------------------------------------------------------------

def extract_2d_features(frame: Image.Image, cols: int = 24, rows: int = 4):
    """Extract a 2D (Latitude x Longitude) visual feature grid."""
    image = frame.convert("RGB").resize((480, 240))
    rgb = np.asarray(image, dtype=np.float32) / 255.0
    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    gx = np.abs(np.diff(lum, axis=1, prepend=lum[:, :1]))
    gy = np.abs(np.diff(lum, axis=0, prepend=lum[:1, :]))
    edges = np.clip((gx + gy) * 2.0, 0, 1)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    hue = (rgb[:, :, 0] - rgb[:, :, 2] + 1.0) * 0.5
    green = np.clip(rgb[:, :, 1] - (rgb[:, :, 0] + rgb[:, :, 2]) * 0.5 + 0.5, 0, 1)
    bright_mask = (lum > 0.74).astype(np.float32)

    col_bounds = np.linspace(0, 480, cols + 1, dtype=int)
    row_bounds = np.linspace(0, 240, rows + 1, dtype=int)

    grids = {k: np.zeros((rows, cols), dtype=np.float32)
             for k in ("lum", "sat", "edge", "hue", "green", "bright")}

    for r in range(rows):
        r0, r1 = row_bounds[r], row_bounds[r + 1]
        for c in range(cols):
            c0, c1 = col_bounds[c], col_bounds[c + 1]
            grids["lum"][r, c] = float(np.mean(lum[r0:r1, c0:c1]))
            grids["sat"][r, c] = float(np.mean(sat[r0:r1, c0:c1]))
            grids["edge"][r, c] = float(np.mean(edges[r0:r1, c0:c1]))
            grids["hue"][r, c] = float(np.mean(hue[r0:r1, c0:c1]))
            grids["green"][r, c] = float(np.mean(green[r0:r1, c0:c1]))
            grids["bright"][r, c] = float(np.mean(bright_mask[r0:r1, c0:c1]))
    return grids


def compute_difference_frames(img_before: Image.Image, img_after: Image.Image, steps: int = 8):
    a = np.asarray(img_before.convert("RGB").resize((480, 240)), dtype=np.float32)
    b = np.asarray(img_after.convert("RGB").resize((480, 240)), dtype=np.float32)
    diff = np.clip(np.abs(b - a) * 2.2, 0, 255)
    seq = []
    for i in range(steps):
        alpha = i / max(1, steps - 1)
        if alpha < 0.5:
            t = alpha * 2.0
            blend = (1.0 - t) * a + t * b
        else:
            t = (alpha - 0.5) * 2.0
            blend = (1.0 - t) * b + t * diff
        seq.append(Image.fromarray(blend.astype(np.uint8)))
    return seq


# ---------------------------------------------------------------------
# Python Stereo WAV Synthesizer (Lossless Export & Native Scrubbing)
# ---------------------------------------------------------------------

def build_scale_freqs(scale_name: str, base: float = 110.0, octaves: int = 3):
    intervals = SCALES.get(scale_name, SCALES["Lydian (Cosmic Wonder)"])
    return np.array([
        base * (2.0 ** ((12 * octave + interval) / 12.0))
        for octave in range(octaves)
        for interval in intervals
    ], dtype=np.float32)


def apply_stereo_delay(stereo: np.ndarray, sample_rate: int = 22050, wet: float = 0.22):
    d1 = int(sample_rate * 0.19)
    d2 = int(sample_rate * 0.29)
    out = stereo.copy()
    if len(stereo) > d1:
        out[d1:, 0] += wet * 0.65 * stereo[:-d1, 1]
        out[d1:, 1] += wet * 0.65 * stereo[:-d1, 0]
    if len(stereo) > d2:
        out[d2:, 0] += wet * 0.35 * stereo[:-d2, 0]
        out[d2:, 1] += wet * 0.35 * stereo[:-d2, 1]
    return out


def synthesize_wav_from_features(
    features: list,
    slices: int = 24,
    note_seconds: float = 0.085,
    sample_rate: int = 22050,
    profile_name: str = "Balanced Earth",
    scale_name: str = "Lydian (Cosmic Wonder)",
    enable_drone: bool = True,
    enable_transients: bool = True,
    reverb_wet: float = 0.22,
):
    scale = build_scale_freqs(scale_name, base=110.0, octaves=3)
    num_frames = len(features)
    total_steps = num_frames * slices
    grain_seconds = note_seconds * 1.75
    tail_seconds = 0.35
    total_samples = int(sample_rate * (total_steps * note_seconds + grain_seconds + tail_seconds))
    stereo = np.zeros((total_samples, 2), dtype=np.float32)

    if enable_drone and total_samples > 0:
        t_all = np.arange(total_samples, dtype=np.float32) / sample_rate
        frame_means = np.array([float(np.mean(ft["lum"])) for ft in features], dtype=np.float32)
        env_curve = np.interp(
            np.linspace(0, max(num_frames - 1, 0), total_samples),
            np.arange(num_frames),
            frame_means,
        ).astype(np.float32)
        root = scale[0] * 0.5
        fifth = root * 1.4983
        drone_l = (
            0.55 * np.sin(2 * np.pi * root * t_all)
            + 0.30 * np.sin(2 * np.pi * fifth * t_all + 0.4)
            + 0.15 * np.sin(2 * np.pi * (root * 2.0) * t_all)
        )
        drone_r = (
            0.55 * np.sin(2 * np.pi * (root * 1.003) * t_all + 0.2)
            + 0.30 * np.sin(2 * np.pi * fifth * t_all + 1.1)
            + 0.15 * np.sin(2 * np.pi * (root * 2.0) * t_all + 0.7)
        )
        fade_len = min(total_samples // 4, int(sample_rate * 0.35))
        drone_env = np.ones(total_samples, dtype=np.float32)
        if fade_len > 1:
            drone_env[:fade_len] = np.linspace(0, 1, fade_len)
            drone_env[-fade_len:] = np.linspace(1, 0, fade_len)
        bed_gain = 0.11 * (0.45 + 0.75 * env_curve) * drone_env
        stereo[:, 0] += drone_l * bed_gain
        stereo[:, 1] += drone_r * bed_gain

    row_octave_shifts = [12, 7, 0, -5]
    rng = np.random.default_rng(42)
    prev_lum = None

    for f_idx, ft in enumerate(features):
        lum, sat, edge = ft["lum"], ft["sat"], ft["edge"]
        hue, green, bright = ft["hue"], ft["green"], ft["bright"]
        delta = np.zeros_like(lum) if prev_lum is None else np.clip(np.abs(lum - prev_lum) * 2.5, 0, 1)
        prev_lum = lum

        for c in range(slices):
            step_idx = f_idx * slices + c
            start_sample = int(step_idx * note_seconds * sample_rate)
            pan = c / max(1, slices - 1)
            gain_l = float(np.sqrt(1.0 - pan))
            gain_r = float(np.sqrt(pan))

            for r in range(4):
                b_val, s_val, e_val = float(lum[r, c]), float(sat[r, c]), float(edge[r, c])
                h_val, g_val, br_val = float(hue[r, c]), float(green[r, c]), float(bright[r, c])
                ch_val = float(delta[r, c])

                if profile_name == "Ocean currents & temperature":
                    val, tex, acc = 0.65 * b_val + 0.35 * s_val, 0.60 * s_val + 0.40 * e_val, ch_val
                elif profile_name == "Night lights & urban change":
                    val = 0.30 * b_val + 0.70 * br_val
                    tex = 0.25 * s_val + 0.75 * e_val
                    acc = float(np.clip(0.6 * ch_val + 0.4 * br_val, 0, 1))
                elif profile_name == "Forest canopy (colour proxy)":
                    val = 0.25 * b_val + 0.75 * g_val
                    tex = 0.55 * g_val + 0.45 * e_val
                    acc = float(np.clip(0.65 * ch_val + 0.35 * g_val, 0, 1))
                elif profile_name == "Atmosphere & aerosols":
                    val = 0.45 * b_val + 0.55 * s_val
                    tex = 0.55 * s_val + 0.45 * e_val
                    acc = float(np.clip(0.5 * ch_val + 0.5 * e_val, 0, 1))
                elif profile_name == "Lightning & transient events":
                    val, tex = 0.40 * b_val + 0.60 * e_val, e_val
                    acc = float(np.clip(0.75 * br_val + 0.25 * ch_val, 0, 1))
                else:
                    val, tex, acc = 0.70 * b_val + 0.30 * s_val, 0.60 * s_val + 0.40 * e_val, ch_val

                note_idx = int(np.clip(round(val * (len(scale) - 1)), 0, len(scale) - 1))
                freq = scale[note_idx] * (2.0 ** (row_octave_shifts[r] / 12.0))
                freq *= 2.0 ** (((h_val - 0.5) * 0.45) / 12.0)

                dur = grain_seconds * (0.85 + 0.35 * acc)
                n_samp = max(16, int(sample_rate * dur))
                end_sample = min(total_samples, start_sample + n_samp)
                n_actual = end_sample - start_sample
                if n_actual <= 0:
                    continue

                t = np.arange(n_actual, dtype=np.float32) / sample_rate
                if r == 0:
                    env = np.exp(-t / (dur * 0.32)) * np.minimum(1.0, t / 0.008)
                    wave = np.sin(2 * np.pi * freq * t) + 0.35 * tex * np.sin(2 * np.pi * 2.756 * freq * t)
                elif r in (1, 2):
                    env = np.exp(-t / (dur * 0.45)) * np.minimum(1.0, t / 0.012)
                    wave = (
                        np.sin(2 * np.pi * freq * t)
                        + 0.28 * tex * np.sin(2 * np.pi * 2.0 * freq * t)
                        + 0.12 * tex * np.sin(2 * np.pi * 3.0 * freq * t)
                    )
                else:
                    att = min(n_actual // 3, int(sample_rate * 0.045))
                    rel = min(n_actual // 3, int(sample_rate * 0.06))
                    env = np.ones(n_actual, dtype=np.float32)
                    if att > 1:
                        env[:att] = np.linspace(0, 1, att)
                    if rel > 1:
                        env[-rel:] = np.linspace(1, 0, rel)
                    wave = np.sin(2 * np.pi * freq * t) + 0.35 * tex * np.sin(2 * np.pi * 2.0 * freq * t)

                amp = 0.045 + 0.11 * b_val + 0.08 * acc
                if profile_name == "Night lights & urban change":
                    amp *= (0.20 + 1.15 * br_val)

                voice = wave * env * amp
                stereo[start_sample:end_sample, 0] += voice * gain_l
                stereo[start_sample:end_sample, 1] += voice * gain_r

                if enable_transients and (br_val > 0.38 or acc > 0.55) and (r in (0, 1)):
                    spark_len = min(total_samples - start_sample, int(sample_rate * 0.09))
                    if spark_len > 8:
                        ts = np.arange(spark_len, dtype=np.float32) / sample_rate
                        spark_env = np.exp(-ts / 0.018) * np.minimum(1.0, ts / 0.002)
                        noise_burst = rng.standard_normal(spark_len).astype(np.float32) * 0.15
                        spark = (
                            (np.sin(2 * np.pi * (freq * 4.0) * ts) + noise_burst)
                            * spark_env
                            * (0.06 * max(br_val, acc))
                        )
                        stereo[start_sample:start_sample + spark_len, 0] += spark * gain_l
                        stereo[start_sample:start_sample + spark_len, 1] += spark * gain_r

    if reverb_wet > 0:
        stereo = apply_stereo_delay(stereo, sample_rate=sample_rate, wet=reverb_wet)

    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo = stereo / peak * 0.92
    pcm = (stereo * 32767.0).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm)
    return buffer.getvalue()


# ---------------------------------------------------------------------
# Climate Diagnostics, Layman Translator & Multimodal AI API
# ---------------------------------------------------------------------

def analyze_climate_patterns(lum_stack: np.ndarray, calib: dict | None = None):
    n_frames, _, n_cols = lum_stack.shape
    band_names = [
        "High North (Arctic/Subarctic)",
        "Northern Mid-Latitudes",
        "Southern Mid-Latitudes",
        "High South (Antarctic/Southern)",
    ]
    lon_names = [
        "Western Sector (Americas / E. Pacific)",
        "Central Sector (Atlantic / Europe / Africa)",
        "Eastern Sector (Asia / Indo-Pacific)",
    ]

    if calib and calib.get("enabled"):
        lo, hi = float(calib["min_val"]), float(calib["max_val"])
        unit = str(calib["unit"]).strip() or "units"
        work_stack = lo + lum_stack * (hi - lo)
    else:
        unit = "norm. intensity"
        work_stack = lum_stack

    global_series = work_stack.mean(axis=(1, 2))
    band_series = work_stack.mean(axis=2)

    if n_frames >= 2:
        x = np.arange(n_frames, dtype=np.float32)
        global_slope = float(np.polyfit(x, global_series, 1)[0])
        north_slope = float(np.polyfit(x, band_series[:, 0], 1)[0])
        net_delta = float(global_series[-1] - global_series[0])
        denom = abs(float(global_series[0])) if abs(float(global_series[0])) > 1e-4 else 1.0
        net_change_pct = float((net_delta / denom) * 100.0)
    else:
        global_slope = north_slope = net_delta = net_change_pct = 0.0

    polar_amp = round(north_slope / global_slope, 2) if abs(global_slope) > 1e-5 else 1.0

    mean_val = float(np.mean(work_stack))
    std_val = float(np.std(work_stack)) + 1e-6
    z_grid = (work_stack - mean_val) / std_val
    peak_f, peak_r, peak_c = np.unravel_index(int(np.argmax(z_grid)), z_grid.shape)
    peak_z = float(z_grid[peak_f, peak_r, peak_c])
    peak_val = float(work_stack[peak_f, peak_r, peak_c])
    lon_sector = lon_names[min(2, int((int(peak_c) / max(1, n_cols)) * 3))]

    flat = np.sort(np.clip(lum_stack[-1].ravel(), 0.0, 1.0))
    idx = np.arange(1, len(flat) + 1)
    concentration = float(
        (2.0 * np.sum(idx * flat)) / (len(flat) * np.sum(flat) + 1e-6)
        - (len(flat) + 1.0) / len(flat)
    )

    if calib and calib.get("enabled"):
        shift_str = f"{net_delta:+.2f} {unit} ({net_change_pct:+.1f}%)"
        peak_val_str = f"{peak_val:.2f} {unit} (Z = {peak_z:.2f})"
    else:
        shift_str = f"{net_change_pct:+.1f}%"
        peak_val_str = f"Z = {peak_z:.2f}"

    insight_narration = (
        f"Climate Pattern Analysis: Net sequence shift is {shift_str}. "
        f"The High North band changes at {polar_amp:.2f} times the global rate. "
        f"Peak spatial anomaly occurs at frame {int(peak_f) + 1} in the {band_names[int(peak_r)]}, "
        f"{lon_sector}, with {peak_val_str}."
    )

    return {
        "band_series": band_series,
        "band_names": band_names,
        "net_change_pct": round(net_change_pct, 1),
        "shift_display": shift_str,
        "polar_amplification": polar_amp,
        "peak_hotspot": {
            "frame": int(peak_f) + 1,
            "latitude": band_names[int(peak_r)],
            "longitude": lon_sector,
            "z_score": round(peak_z, 2),
            "display": peak_val_str,
        },
        "spatial_concentration": round(concentration, 3),
        "unit": unit,
        "insight_narration": insight_narration,
    }


def generate_layman_planet_story(layman_base: str, climate: dict, num_frames: int):
    """Translate technical 2D visual-proxy metrics into everyday human terms."""
    amp = climate["polar_amplification"]
    hotspot = climate["peak_hotspot"]
    conc = climate["spatial_concentration"]
    net_pct = climate["net_change_pct"]

    if num_frames > 1:
        if net_pct > 4.0:
            trend_bullet = (
                f"**Overall Trend:** Planetary activity rises by **{net_pct:+.1f}%** across this timeline—"
                "you will hear the soundscape gradually swell brighter and more energetic."
            )
        elif net_pct < -4.0:
            trend_bullet = (
                f"**Overall Trend:** Planetary activity drops by **{net_pct:+.1f}%** across this timeline—"
                "you will hear the music gradually soften and calm down."
            )
        else:
            trend_bullet = (
                "**Overall Trend:** Overall planetary intensity stays fairly steady across time, "
                "with most movement shifting geographically from region to region."
            )
    else:
        trend_bullet = (
            "**How to Listen:** This is a single planetary snapshot—as the glowing line sweeps from "
            "West to East, you are hearing a live cross-section of Earth from the Americas to Asia."
        )

    if amp > 1.2 and num_frames > 1:
        arctic_bullet = (
            f"**Why the North Sounds Active:** The far North is shifting **{amp:.1f}× faster** than the global average. "
            "In real climate science, this mirrors *Arctic amplification*—polar regions react first and fastest to warming."
        )
    else:
        arctic_bullet = (
            f"**Biggest Hotspot to Listen For:** Peak activity stands out in the **{hotspot['latitude']}** "
            f"({hotspot['longitude']}), where the notes ring brightest."
        )

    if conc > 0.28:
        spread_bullet = (
            "**Pattern Shape:** Tightly clustered into sharp local hotspots (like bright cities or storm cells) "
            "rather than spread evenly across the globe."
        )
    else:
        spread_bullet = (
            "**Pattern Shape:** Spread broadly like a planetary blanket across vast stretches of ocean or atmosphere."
        )

    return {
        "headline": layman_base,
        "bullets": [trend_bullet, arctic_bullet, spread_bullet],
    }


def run_multimodal_ai_analysis(
    provider: str,
    api_key: str,
    model_name: str,
    frame: Image.Image,
    title: str,
    summary: str,
    climate_stats: dict,
):
    """Call OpenRouter, Google Gemini, or OpenAI Vision API via REST."""
    clean_key = api_key.strip()
    if clean_key.startswith("sk-or-"):
        provider = "OpenRouter"

    buf = io.BytesIO()
    frame.convert("RGB").resize((640, 320)).save(buf, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    prompt = (
        f"You are an Earth science communicator and accessibility specialist for NASA's Earth Information Center.\n"
        f"Dataset Title: {title}\n"
        f"NASA Context: {summary}\n"
        f"Extracted Visual-Proxy Diagnostics:\n"
        f"- Net Sequence Shift: {climate_stats['shift_display']}\n"
        f"- High-North Amplification Ratio: {climate_stats['polar_amplification']}x\n"
        f"- Peak Anomaly Hotspot: {climate_stats['peak_hotspot']['latitude']}, "
        f"{climate_stats['peak_hotspot']['longitude']} (Frame {climate_stats['peak_hotspot']['frame']}, "
        f"{climate_stats['peak_hotspot']['display']})\n"
        f"- Spatial Concentration Index: {climate_stats['spatial_concentration']}\n\n"
        f"Provide three clear, engaging sections:\n"
        f"1. **In Plain English: What This Means for Our Planet**: Explain in simple, jargon-free language "
        f"why this data matters to everyday people, food, weather, or communities on Earth.\n"
        f"2. **Scientific & Regional Breakdown**: Point out the key geographic patterns visible in the frame "
        f"(note clearly that pixel-derived metrics are visual proxies).\n"
        f"3. **Blind & Low-Vision Audio Story**: Write a vivid 3-sentence spoken narration guiding a listener "
        f"through what they hear from North (high chimes) to South (bass) and West to East."
    )

    if provider == "OpenRouter":
        or_model = model_name if "/" in model_name else f"google/{model_name}"
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_key}",
            "HTTP-Referer": "https://earth-sound-jukebox.local",
            "X-Title": "EARTH//SOUND NASA Space Apps Prototype",
        }
        payload = {
            "model": or_model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                ],
            }],
            "max_tokens": 600,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            raise ValueError(f"OpenRouter API error ({resp.status_code}): {resp.text[:300]}")
        return resp.json()["choices"][0]["message"]["content"]

    elif provider == "Google Gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": clean_key,
        }
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
                ]
            }]
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            raise ValueError(f"Gemini API error ({resp.status_code}): {resp.text[:300]}")
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_key}",
        }
        payload = {
            "model": model_name,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                ],
            }],
            "max_tokens": 600,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            raise ValueError(f"OpenAI API error ({resp.status_code}): {resp.text[:300]}")
        return resp.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------
# Real-Time In-Browser Web Audio Synthesizer + Touch/Hover Explorer
# ---------------------------------------------------------------------

def encode_frames_base64(frames):
    encoded = []
    for f in frames:
        resized = f.convert("RGB").resize((640, 320))
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=80)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        encoded.append(f"data:image/jpeg;base64,{b64}")
    return encoded


def render_browser_webaudio_jukebox(
    frames,
    features: list,
    cols: int,
    step_seconds: float,
    scale_name: str,
    profile_name: str,
    enable_drone: bool,
    enable_transients: bool,
    title: str,
    narration_text: str,
):
    frame_urls = encode_frames_base64(frames)
    serialized_features = []
    for ft in features:
        serialized_features.append({
            "lum": np.round(ft["lum"], 3).tolist(),
            "sat": np.round(ft["sat"], 3).tolist(),
            "edge": np.round(ft["edge"], 3).tolist(),
            "bright": np.round(ft["bright"], 3).tolist(),
            "green": np.round(ft["green"], 3).tolist(),
        })

    payload = json.dumps({
        "frames": frame_urls,
        "features": serialized_features,
        "cols": cols,
        "stepMs": int(step_seconds * 1000),
        "scales": SCALES,
        "initialScale": scale_name,
        "profile": profile_name,
        "enableDrone": enable_drone,
        "enableTransients": enable_transients,
        "title": title,
        "narration": narration_text,
    })

    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8" />
    <style>
      body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #071923;
        color: #eaf6f6;
      }}
      .jukebox-shell {{
        border: 1px solid #1e596b;
        border-radius: 16px;
        padding: 14px;
        background: radial-gradient(circle at top right, #0e3b4c, #06151e);
      }}
      .stage-wrap {{
        position: relative;
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2b6e82;
        background: #020a0f;
        cursor: crosshair;
      }}
      canvas {{
        display: block;
        width: 100%;
        height: auto;
      }}
      .controls-bar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 12px;
      }}
      button, select {{
        background: #104959;
        color: #ffffff;
        border: 1px solid #2c7a8f;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.86rem;
        font-weight: 600;
        cursor: pointer;
      }}
      button:hover, button:focus, select:focus {{
        background: #1b6f85;
        outline: 2px solid #6ef3d6;
        outline-offset: 1px;
      }}
      button.primary {{
        background: #15847b;
        border-color: #4ce0cf;
      }}
      button.stop-btn {{
        background: #6b2635;
        border-color: #d95b76;
      }}
      .legend-bar {{
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #173f4d;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
      }}
      .legend-label {{
        font-size: 0.8rem;
        color: #9ec8d1;
        margin-right: 4px;
      }}
      .status-line {{
        margin-top: 8px;
        font-size: 0.83rem;
        color: #9be3dc;
      }}
    </style>
    </head>
    <body>
    <div class="jukebox-shell" role="region" aria-label="Real-Time Browser Web Audio Earth Jukebox">
      <div class="stage-wrap">
        <canvas id="stage" width="800" height="440"
          aria-label="Interactive Earth Canvas. Press Play to scan automatically, or move cursor over the map to listen to any region."></canvas>
      </div>

      <div class="controls-bar">
        <button id="playBtn" class="primary" aria-label="Start or Stop Live Browser Synthesizer (Shortcut: Space)">▶ Play Live Browser Synth (Space)</button>
        <button id="stopBtn" class="stop-btn" aria-label="Stop and Reset (Shortcut: R)">■ Stop / Reset (R)</button>
        <select id="liveScaleSelect" aria-label="Switch Musical Scale Live">
          <option value="Lydian (Cosmic Wonder)">Scale: Lydian (Cosmic Wonder)</option>
          <option value="Pentatonic (Meditative Earth)">Scale: Pentatonic (Meditative)</option>
          <option value="Dorian (Oceanic Mystery)">Scale: Dorian (Oceanic)</option>
          <option value="Harmonic Minor (Climate Urgency)">Scale: Harmonic Minor (Urgency)</option>
        </select>
        <button id="gridBtn" aria-label="Toggle 4-Latitude Voice Overlay">🌐 Toggle Latitude Bands</button>
        <button id="narrateBtn" aria-label="Speak Insights Aloud (Shortcut: V)">🔊 Speak Narration (V)</button>
      </div>

      <div class="legend-bar" role="group" aria-label="Ear-training audio legend cues">
        <span class="legend-label">🎧 Ear-Training Cues:</span>
        <button type="button" onclick="playCue('low')">1. Low Brightness (Bass)</button>
        <button type="button" onclick="playCue('high')">2. High Brightness (Bell)</button>
        <button type="button" onclick="playCue('spark')">3. Lightning / Burst</button>
        <button type="button" onclick="playCue('pan')">4. West → East Pan</button>
      </div>

      <div id="liveStatus" class="status-line" aria-live="polite">
        💡 Click <b>Play Live Browser Synth</b> for instant real-time audio, or <b>hover/drag over the Earth map</b> to listen to any region!
      </div>
    </div>

    <script>
      const DATA = {payload};
      const canvas = document.getElementById("stage");
      const ctx = canvas.getContext("2d");
      const liveStatus = document.getElementById("liveStatus");
      const playBtn = document.getElementById("playBtn");
      const scaleSelect = document.getElementById("liveScaleSelect");
      scaleSelect.value = DATA.initialScale;

      let showGrid = true;
      let isPlaying = false;
      let scanTimer = null;
      let currentFrame = 0;
      let currentCol = 0;
      let hoverCell = null;
      let lastHoverTime = 0;

      let audioCtx = null;
      let masterGain = null;
      let analyser = null;
      let freqData = null;
      let droneOsc1 = null;
      let droneOsc2 = null;
      let droneGain = null;

      const loadedImages = DATA.frames.map(src => {{
        const img = new Image();
        img.src = src;
        return img;
      }});

      function ensureAudio() {{
        if (!audioCtx) {{
          const AC = window.AudioContext || window.webkitAudioContext;
          audioCtx = new AC();
          masterGain = audioCtx.createGain();
          masterGain.gain.value = 0.72;
          analyser = audioCtx.createAnalyser();
          analyser.fftSize = 128;
          freqData = new Uint8Array(analyser.frequencyBinCount);
          masterGain.connect(analyser);
          analyser.connect(audioCtx.destination);
        }}
        if (audioCtx.state === "suspended") {{
          audioCtx.resume();
        }}
      }}

      function getScaleFreqs(scaleName) {{
        const intervals = DATA.scales[scaleName] || [0, 2, 4, 6, 7, 9, 11];
        const base = 110.0;
        const freqs = [];
        for (let oct = 0; oct < 3; oct++) {{
          for (const iv of intervals) {{
            freqs.push(base * Math.pow(2, (12 * oct + iv) / 12));
          }}
        }}
        return freqs;
      }}

      function startDrone() {{
        if (!DATA.enableDrone || droneOsc1) return;
        ensureAudio();
        const now = audioCtx.currentTime;
        const scale = getScaleFreqs(scaleSelect.value);
        const root = scale[0] * 0.5;
        droneGain = audioCtx.createGain();
        droneGain.gain.setValueAtTime(0.001, now);
        droneGain.gain.exponentialRampToValueAtTime(0.075, now + 0.4);

        droneOsc1 = audioCtx.createOscillator();
        droneOsc1.type = "sine";
        droneOsc1.frequency.setValueAtTime(root, now);

        droneOsc2 = audioCtx.createOscillator();
        droneOsc2.type = "triangle";
        droneOsc2.frequency.setValueAtTime(root * 1.498, now);

        droneOsc1.connect(droneGain);
        droneOsc2.connect(droneGain);
        droneGain.connect(masterGain);
        droneOsc1.start(now);
        droneOsc2.start(now);
      }}

      function stopDrone() {{
        if (!droneOsc1) return;
        try {{
          const now = audioCtx.currentTime;
          droneGain.gain.setTargetAtTime(0.0001, now, 0.08);
          droneOsc1.stop(now + 0.25);
          droneOsc2.stop(now + 0.25);
        }} catch (e) {{}}
        droneOsc1 = null;
        droneOsc2 = null;
        droneGain = null;
      }}

      function triggerCellVoice(fIdx, r, c, durSec) {{
        ensureAudio();
        const ft = DATA.features[fIdx];
        if (!ft) return;
        const lum = ft.lum[r][c];
        const sat = ft.sat[r][c];
        const edge = ft.edge[r][c];
        const bright = ft.bright[r][c];
        const green = ft.green[r][c];

        let val = 0.70 * lum + 0.30 * sat;
        if (DATA.profile === "Night lights & urban change") val = 0.30 * lum + 0.70 * bright;
        else if (DATA.profile === "Forest canopy (colour proxy)") val = 0.25 * lum + 0.75 * green;
        else if (DATA.profile === "Atmosphere & aerosols") val = 0.45 * lum + 0.55 * sat;
        else if (DATA.profile === "Lightning & transient events") val = 0.40 * lum + 0.60 * edge;

        const scale = getScaleFreqs(scaleSelect.value);
        const idx = Math.min(scale.length - 1, Math.max(0, Math.round(val * (scale.length - 1))));
        const rowShifts = [12, 7, 0, -5];
        const freq = scale[idx] * Math.pow(2, rowShifts[r] / 12);

        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const panner = audioCtx.createStereoPanner ? audioCtx.createStereoPanner() : null;

        if (r === 0) osc.type = "sine";
        else if (r === 1 || r === 2) osc.type = sat > 0.35 ? "triangle" : "sine";
        else osc.type = "triangle";

        osc.frequency.setValueAtTime(freq, now);

        let amp = 0.035 + 0.095 * lum;
        if (DATA.profile === "Night lights & urban change") amp *= (0.25 + 1.1 * bright);

        gain.gain.setValueAtTime(0.0005, now);
        gain.gain.exponentialRampToValueAtTime(Math.max(0.002, amp), now + 0.015);
        gain.gain.exponentialRampToValueAtTime(0.0005, now + durSec);

        if (panner) {{
          const pan = (c / Math.max(1, DATA.cols - 1)) * 2.0 - 1.0;
          panner.pan.setValueAtTime(pan, now);
          osc.connect(gain);
          gain.connect(panner);
          panner.connect(masterGain);
        }} else {{
          osc.connect(gain);
          gain.connect(masterGain);
        }}

        osc.start(now);
        osc.stop(now + durSec + 0.02);

        if (DATA.enableTransients && bright > 0.38 && (r === 0 || r === 1)) {{
          const spOsc = audioCtx.createOscillator();
          const spGain = audioCtx.createGain();
          spOsc.type = "sine";
          spOsc.frequency.setValueAtTime(freq * 4.0, now);
          spGain.gain.setValueAtTime(0.04 * bright, now);
          spGain.gain.exponentialRampToValueAtTime(0.0005, now + 0.08);
          spOsc.connect(spGain);
          spGain.connect(masterGain);
          spOsc.start(now);
          spOsc.stop(now + 0.09);
        }}
      }}

      function triggerColumn(fIdx, c) {{
        const durSec = Math.max(0.14, (DATA.stepMs / 1000) * 1.8);
        for (let r = 0; r < 4; r++) {{
          triggerCellVoice(fIdx, r, c, durSec);
        }}
      }}

      function startPlayback() {{
        ensureAudio();
        if (isPlaying) return;
        isPlaying = true;
        playBtn.textContent = "⏸ Pause Browser Synth (Space)";
        startDrone();

        triggerColumn(currentFrame, currentCol);
        scanTimer = setInterval(() => {{
          currentCol++;
          if (currentCol >= DATA.cols) {{
            currentCol = 0;
            currentFrame = (currentFrame + 1) % DATA.frames.length;
          }}
          triggerColumn(currentFrame, currentCol);
          liveStatus.textContent = `Live Web Audio Synth: Frame ${{currentFrame + 1}}/${{DATA.frames.length}} · Longitude Column ${{currentCol + 1}}/${{DATA.cols}}`;
        }}, DATA.stepMs);
      }}

      function pausePlayback() {{
        isPlaying = false;
        playBtn.textContent = "▶ Play Live Browser Synth (Space)";
        if (scanTimer) {{
          clearInterval(scanTimer);
          scanTimer = null;
        }}
        stopDrone();
      }}

      function stopAndReset() {{
        pausePlayback();
        currentFrame = 0;
        currentCol = 0;
        liveStatus.textContent = "Stopped and reset to Frame 1, Western Meridian.";
      }}

      playBtn.addEventListener("click", () => {{
        if (isPlaying) pausePlayback();
        else startPlayback();
      }});

      document.getElementById("stopBtn").addEventListener("click", stopAndReset);
      document.getElementById("gridBtn").addEventListener("click", () => {{ showGrid = !showGrid; }});

      function handlePointerExplore(clientX, clientY) {{
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const x = (clientX - rect.left) * scaleX;
        const y = (clientY - rect.top) * scaleY;
        const imgH = 360;
        if (y < 0 || y >= imgH || x < 0 || x >= canvas.width) {{
          hoverCell = null;
          return;
        }}
        const r = Math.min(3, Math.floor((y / imgH) * 4));
        const c = Math.min(DATA.cols - 1, Math.floor((x / canvas.width) * DATA.cols));
        hoverCell = {{ x, y, r, c }};

        const nowMs = performance.now();
        if (!isPlaying && nowMs - lastHoverTime > 65) {{
          lastHoverTime = nowMs;
          triggerCellVoice(currentFrame, r, c, 0.24);
          const bandNames = ["High North", "N. Mid-Lat", "S. Mid-Lat", "High South"];
          const lumVal = DATA.features[currentFrame].lum[r][c];
          liveStatus.textContent = `Exploring ${{bandNames[r]}}, Column ${{c + 1}}/${{DATA.cols}} — Brightness: ${{(lumVal * 100).toFixed(0)}}%`;
        }}
      }}

      canvas.addEventListener("mousemove", (e) => handlePointerExplore(e.clientX, e.clientY));
      canvas.addEventListener("touchmove", (e) => {{
        if (e.touches && e.touches.length > 0) {{
          handlePointerExplore(e.touches[0].clientX, e.touches[0].clientY);
        }}
      }}, {{ passive: true }});
      canvas.addEventListener("mouseleave", () => {{ hoverCell = null; }});

      function playCue(kind) {{
        ensureAudio();
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const panner = audioCtx.createStereoPanner ? audioCtx.createStereoPanner() : null;

        if (kind === "low") {{
          osc.type = "triangle";
          osc.frequency.setValueAtTime(110, now);
          gain.gain.setValueAtTime(0.001, now);
          gain.gain.exponentialRampToValueAtTime(0.25, now + 0.05);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
          liveStatus.textContent = "Ear-Training Cue: Low brightness maps to warm bass tones.";
        }} else if (kind === "high") {{
          osc.type = "sine";
          osc.frequency.setValueAtTime(880, now);
          gain.gain.setValueAtTime(0.001, now);
          gain.gain.exponentialRampToValueAtTime(0.22, now + 0.02);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
          liveStatus.textContent = "Ear-Training Cue: High brightness maps to high bell pitches.";
        }} else if (kind === "spark") {{
          osc.type = "sawtooth";
          osc.frequency.setValueAtTime(1760, now);
          osc.frequency.exponentialRampToValueAtTime(440, now + 0.18);
          gain.gain.setValueAtTime(0.25, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
          liveStatus.textContent = "Ear-Training Cue: Sudden lightning or urban spikes trigger crisp chimes.";
        }} else {{
          osc.type = "sine";
          osc.frequency.setValueAtTime(330, now);
          gain.gain.setValueAtTime(0.2, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.9);
          if (panner) {{
            panner.pan.setValueAtTime(-1, now);
            panner.pan.linearRampToValueAtTime(1, now + 0.85);
          }}
          liveStatus.textContent = "Ear-Training Cue: West-to-East longitude sweeps from left ear to right ear.";
        }}

        osc.connect(gain);
        if (panner) {{
          gain.connect(panner);
          panner.connect(masterGain);
        }} else {{
          gain.connect(masterGain);
        }}
        osc.start(now);
        osc.stop(now + 0.95);
      }}

      function speakNarration() {{
        if (!("speechSynthesis" in window)) {{
          liveStatus.textContent = DATA.narration;
          return;
        }}
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(DATA.title + ". " + DATA.narration);
        utter.rate = 1.02;
        window.speechSynthesis.speak(utter);
        liveStatus.textContent = "Speaking plain-English planet & climate narration aloud...";
      }}

      document.getElementById("narrateBtn").addEventListener("click", speakNarration);

      window.addEventListener("keydown", (e) => {{
        if (e.code === "Space") {{
          e.preventDefault();
          playBtn.click();
        }} else if (e.key === "r" || e.key === "R") {{
          stopAndReset();
        }} else if (e.key === "v" || e.key === "V") {{
          speakNarration();
        }}
      }});

      function draw() {{
        const w = canvas.width;
        const h = canvas.height;
        const imgH = 360;
        const specH = h - imgH;

        ctx.fillStyle = "#031017";
        ctx.fillRect(0, 0, w, h);

        const img = loadedImages[currentFrame];
        if (img && img.complete) {{
          ctx.drawImage(img, 0, 0, w, imgH);
        }}

        if (showGrid) {{
          const bandLabels = [
            "HIGH NORTH (Bell/Chime)",
            "N. MID-LAT (Marimba)",
            "S. MID-LAT (Harmonic)",
            "HIGH SOUTH (Bass/Cello)"
          ];
          ctx.strokeStyle = "rgba(110, 243, 214, 0.25)";
          ctx.fillStyle = "rgba(234, 246, 246, 0.82)";
          ctx.font = "11px sans-serif";
          for (let r = 1; r < 4; r++) {{
            const y = (imgH / 4) * r;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
          }}
          for (let r = 0; r < 4; r++) {{
            ctx.fillText(bandLabels[r], 10, (imgH / 4) * r + 16);
          }}
        }}

        const scanNorm = (currentCol + 0.5) / DATA.cols;
        const scanX = scanNorm * w;
        const grad = ctx.createLinearGradient(scanX - 24, 0, scanX + 4, 0);
        grad.addColorStop(0, "rgba(76, 224, 207, 0)");
        grad.addColorStop(1, isPlaying ? "rgba(76, 224, 207, 0.5)" : "rgba(76, 224, 207, 0.22)");
        ctx.fillStyle = grad;
        ctx.fillRect(Math.max(0, scanX - 24), 0, 28, imgH);

        ctx.strokeStyle = "#6ef3d6";
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(scanX, 0);
        ctx.lineTo(scanX, imgH);
        ctx.stroke();

        if (hoverCell) {{
          ctx.strokeStyle = "#ffd166";
          ctx.lineWidth = 1.8;
          ctx.beginPath();
          ctx.arc(hoverCell.x, hoverCell.y, 12, 0, Math.PI * 2);
          ctx.stroke();
        }}

        ctx.fillStyle = "rgba(4, 20, 29, 0.82)";
        ctx.fillRect(w - 190, 10, 180, 26);
        ctx.fillStyle = "#6ef3d6";
        ctx.font = "bold 12px sans-serif";
        ctx.fillText(`FRAME ${{currentFrame + 1}}/${{DATA.frames.length}} · COL ${{currentCol + 1}}/${{DATA.cols}}`, w - 180, 27);

        ctx.fillStyle = "#061a24";
        ctx.fillRect(0, imgH, w, specH);
        if (analyser && freqData) {{
          analyser.getByteFrequencyData(freqData);
          const bars = freqData.length;
          const barW = w / bars;
          for (let i = 0; i < bars; i++) {{
            const v = freqData[i] / 255.0;
            const bh = v * (specH - 12);
            ctx.fillStyle = `hsl(${{175 + v * 45}}, 85%, ${{42 + v * 28}}%)`;
            ctx.fillRect(i * barW + 1, h - bh - 4, Math.max(2, barW - 2), bh);
          }}
        }}

        requestAnimationFrame(draw);
      }}

      requestAnimationFrame(draw);
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=565)


# ---------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    .hero {
      padding: 1.4rem 1.7rem; border-radius: 18px;
      background: linear-gradient(120deg, #072230 0%, #0d4f5e 55%, #16736c 100%);
      color: white; margin-bottom: 1.1rem;
      border: 1px solid #2b7b8c;
    }
    .hero h1 {font-size: 2.35rem; margin: 0; letter-spacing: .06em;}
    .hero p {color: #d7eeee; margin: .4rem 0 0 0; font-size: 1.02rem;}
    .planet-card {
      padding: 1.15rem 1.35rem;
      border-radius: 14px;
      background: linear-gradient(135deg, #0b2e3d 0%, #114454 100%);
      border-left: 5px solid #4ce0cf;
      color: #eef9f9;
      margin-bottom: 1.1rem;
    }
    .planet-card h3 {margin: 0 0 0.45rem 0; color: #7ef7e6; font-size: 1.15rem;}
    .planet-card p {margin: 0 0 0.5rem 0; font-size: 0.98rem; line-height: 1.5;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>EARTH//SOUND 🌍</h1>
      <p>NASA Earth Information Center Multi-Sensory Jukebox — Translating Planetary Science into Plain English & Spatial Sound</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🎛️ Jukebox Controls")
    source_mode = st.radio(
        "1. Select Data Source",
        [
            "NASA EIC Gallery",
            "Before / After Change Comparison",
            "Upload an Image",
            "Upload a Video",
        ],
    )

    st.divider()
    st.subheader("🤖 AI Climate Analyst (Optional)")
    ai_provider = st.selectbox("AI Provider", ["OpenRouter", "Google Gemini", "OpenAI"])
    ai_api_key = st.text_input(
        "Enter API Key",
        type="password",
        placeholder="sk-or-v1-... / AIza... / sk-...",
        help="Your key stays in session memory only and is never written to disk.",
    )
    if ai_provider == "OpenRouter":
        or_choice = st.selectbox(
            "OpenRouter Vision Model",
            [
                "google/gemini-3.8-flash",
                "google/gemini-3.5-flash",
                "google/gemini-2.5-flash",
                "openai/gpt-4o-mini",
                "Custom Model Slug...",
            ],
        )
        if or_choice == "Custom Model Slug...":
            ai_model = st.text_input("OpenRouter Model ID", value="google/gemini-3.8-flash")
        else:
            ai_model = or_choice
    elif ai_provider == "Google Gemini":
        ai_model = st.selectbox("Gemini Model", ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"])
    else:
        ai_model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o"])

    st.divider()
    st.subheader("🎼 Browser & WAV Synth Tuning")
    scale_name = st.selectbox("Harmonic Scale", list(SCALES.keys()), index=0)
    slices = st.slider("Longitude Scan Resolution (columns)", 12, 48, 24, 4)
    note_seconds = st.slider("Scan Speed (seconds/column)", 0.04, 0.16, 0.085, 0.005)
    enable_drone = st.checkbox("Global Earth Choir / Sub-Bass Drone", value=True)
    enable_transients = st.checkbox("Lightning / Bright-Burst Chimes", value=True)
    reverb_wet = st.slider("WAV Export Reverb", 0.0, 0.45, 0.22, 0.02)

    st.divider()
    st.subheader("📏 Optional Legend Calibration")
    enable_calib = st.checkbox("Map Brightness to Colorbar Units", value=False)
    calib_min = st.number_input("Legend Min Value", value=-2.0, step=1.0, disabled=not enable_calib)
    calib_max = st.number_input("Legend Max Value", value=32.0, step=1.0, disabled=not enable_calib)
    calib_unit = st.text_input("Physical Unit", value="°C", disabled=not enable_calib)

frames = []
source_title = ""
source_description = ""
source_layman_base = ""
source_mapping = ""
source_url = None
source_credit = "NASA Scientific Visualization Studio (SVS)"
preview_image = None
recommended_profile = "Balanced Earth"

if source_mode == "NASA EIC Gallery":
    selected_title = st.selectbox("Select a NASA EIC Visualization", list(CATALOG.keys()))
    item = CATALOG[selected_title]
    source_title = selected_title
    source_description = item["summary"]
    source_layman_base = item["layman_planet"]
    source_mapping = item["mapping"]
    source_url = item["source"]
    recommended_profile = item["default_profile"]

    with st.spinner("Fetching NASA SVS metadata and official preview..."):
        try:
            page = fetch_svs_page(item["id"])
            image_url = choose_preview_image(page)
            if not image_url:
                raise ValueError("No preview image returned by NASA SVS API.")
            preview_bytes = fetch_image_bytes(image_url)
            preview_image = Image.open(io.BytesIO(preview_bytes)).convert("RGB")
            credits = page.get("main_credits", {})
            credit_names = [
                p["name"] for people in credits.values() for p in people if p.get("name")
            ]
            if credit_names:
                source_credit = "NASA SVS Credits: " + ", ".join(dict.fromkeys(credit_names))
            api_video = choose_small_video(page)
        except Exception as exc:
            st.warning(f"NASA SVS API unavailable ({exc}). Loaded offline demonstration proxy.")
            preview_image = generate_offline_fallback_image(selected_title)
            api_video = None

    if api_video:
        with st.expander("🎞️ Optional: Sample multi-frame NASA animation (MP4 ≤ 60 MB)"):
            if st.button("Fetch & Sample NASA Video"):
                try:
                    with st.spinner("Downloading and sampling NASA video frames..."):
                        vbytes = download_video_limited(api_video, max_mb=60)
                        frames = extract_sampled_frames(vbytes, max_frames=16)
                    st.session_state["nasa_video_frames"] = frames
                    st.session_state["nasa_video_id"] = item["id"]
                    st.success(f"Sampled {len(frames)} frames from NASA animation.")
                except Exception as exc:
                    st.error(f"Video sampling skipped: {exc}")

    if not frames and st.session_state.get("nasa_video_id") == item["id"]:
        frames = st.session_state.get("nasa_video_frames", [])
    if not frames:
        frames = [preview_image]

elif source_mode == "Before / After Change Comparison":
    st.subheader("🔄 Planetary Change Sonification (Era A vs. Era B)")
    c1, c2 = st.columns(2)
    with c1:
        f_before = st.file_uploader("Upload Era A (Before)", type=["png", "jpg", "jpeg"], key="before")
    with c2:
        f_after = st.file_uploader("Upload Era B (After)", type=["png", "jpg", "jpeg"], key="after")
    if f_before and f_after:
        img_a = Image.open(f_before).convert("RGB")
        img_b = Image.open(f_after).convert("RGB")
        frames = compute_difference_frames(img_a, img_b, steps=8)
        source_title = f"Change Analysis: {f_before.name} → {f_after.name}"
        source_layman_base = (
            "Comparing two snapshots from different years reveals where our planet is changing fastest—"
            "steady areas fade into the background while regions of rapid change sing loudest."
        )
        source_description = "8-step temporal transition culminating in an amplified visual-difference field."
        source_mapping = "Steady regions quiet down; rising harmonic intensity highlights areas of rapid change."

elif source_mode == "Upload an Image":
    uploaded = st.file_uploader("Upload a PNG or JPEG Earth visualization", type=["png", "jpg", "jpeg"])
    if uploaded:
        preview_image = Image.open(uploaded).convert("RGB")
        frames = [preview_image]
        source_title = uploaded.name
        source_layman_base = (
            "Every bright region, colour shift, and boundary in this satellite view represents real activity "
            "on Earth's surface or atmosphere, translated directly into spatial sound."
        )
        source_description = "User-supplied Earth visualization frame."
        source_mapping = "Visual-proxy sonification across 4 latitude bands and stereo longitude."

else:
    uploaded_video = st.file_uploader("Upload an MP4/MOV/WEBM clip (≤ 60 MB)", type=["mp4", "mov", "webm"])
    if uploaded_video:
        vbytes = uploaded_video.getvalue()
        if len(vbytes) > 60 * 1024 * 1024:
            st.error("Please upload a clip smaller than 60 MB.")
        else:
            with st.spinner("Sampling video frames..."):
                frames = extract_sampled_frames(vbytes, max_frames=16)
            source_title = uploaded_video.name
            source_layman_base = (
                "Watching Earth evolve over time helps scientists spot seasonal rhythms, storm tracks, "
                "and long-term environmental shifts that single photos miss."
            )
            source_description = "User-supplied animation sampled into evenly spaced visual frames."
            source_mapping = "Visual-proxy sonification tracking frame-to-frame luminance and colour shifts."

profile_options = [
    "Balanced Earth",
    "Ocean currents & temperature",
    "Night lights & urban change",
    "Forest canopy (colour proxy)",
    "Atmosphere & aerosols",
    "Lightning & transient events",
]
default_idx = profile_options.index(recommended_profile) if recommended_profile in profile_options else 0
profile_name = st.selectbox("Sonification Mapping Profile", profile_options, index=default_idx)

# ---------------------------------------------------------------------
# Instant Layman Planet Story + Live Browser Stage
# ---------------------------------------------------------------------

if frames:
    features = [extract_2d_features(f, cols=slices, rows=4) for f in frames]
    lum_stack = np.stack([ft["lum"] for ft in features], axis=0)
    calib_cfg = {
        "enabled": enable_calib,
        "min_val": calib_min,
        "max_val": calib_max,
        "unit": calib_unit,
    }
    climate = analyze_climate_patterns(lum_stack, calib=calib_cfg)
    layman_story = generate_layman_planet_story(source_layman_base, climate, len(frames))

    # TOP-OF-PAGE PLAIN-ENGLISH PLANETARY SUMMARY
    st.markdown(
        f"""
        <div class="planet-card">
          <h3>🌍 What Does This Mean for Our Planet? (In Plain English)</h3>
          <p>{layman_story['headline']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for bullet in layman_story["bullets"]:
        st.markdown(f"- {bullet}")

    ai_report = st.session_state.get("ai_reports", {}).get(source_title)
    default_spoken = f"{source_layman_base} {climate['insight_narration']}"
    spoken_text = ai_report if ai_report else default_spoken

    st.subheader(f"🎧 Interactive Live Browser Jukebox: {source_title}")
    render_browser_webaudio_jukebox(
        frames=frames,
        features=features,
        cols=slices,
        step_seconds=note_seconds,
        scale_name=scale_name,
        profile_name=profile_name,
        enable_drone=enable_drone,
        enable_transients=enable_transients,
        title=source_title,
        narration_text=spoken_text,
    )

    # AI Multimodal Analysis Panel (OpenRouter / Gemini / OpenAI)
    st.subheader("🤖 AI Climate & Accessibility Analyst")
    if ai_api_key:
        if st.button("✨ Analyze Visualization & Climate Signals with AI", type="primary"):
            with st.spinner(f"Analyzing Earth frame and 2D telemetry via {ai_provider} ({ai_model})..."):
                try:
                    mid_frame = frames[len(frames) // 2]
                    report = run_multimodal_ai_analysis(
                        provider=ai_provider,
                        api_key=ai_api_key,
                        model_name=ai_model,
                        frame=mid_frame,
                        title=source_title,
                        summary=source_description,
                        climate_stats=climate,
                    )
                    st.session_state.setdefault("ai_reports", {})[source_title] = report
                    st.rerun()
                except Exception as exc:
                    st.error(f"AI analysis failed: {exc}")
    else:
        st.info("🔑 Enter an **OpenRouter (`sk-or-...`)**, **Google Gemini**, or **OpenAI** API key in the sidebar for custom AI visual insights.")

    if ai_report:
        st.success("**AI Climate & Accessibility Report Ready** (Press **🔊 Speak Narration (V)** in the player above to listen aloud!)")
        st.markdown(ai_report)

    # Climate Diagnostics & Hovmöller Heatmap
    st.divider()
    st.subheader("📊 Automated Climate & Spatial Diagnostics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Net Sequence Shift", climate["shift_display"])
    m2.metric("High-North Amplification", f"{climate['polar_amplification']:.2f}×")
    m3.metric(
        "Peak Anomaly Hotspot",
        climate["peak_hotspot"]["display"],
        f"Frame {climate['peak_hotspot']['frame']} · {climate['peak_hotspot']['latitude'].split(' ')[0]}",
    )
    m4.metric("Spatial Concentration", f"{climate['spatial_concentration']:.3f}")

    h_col, s_col = st.columns([1.25, 1])
    with h_col:
        fig, ax = plt.subplots(figsize=(8, 3.0))
        vmin = float(calib_min) if enable_calib else 0.0
        vmax = float(calib_max) if enable_calib else 1.0
        if vmin >= vmax:
            vmin, vmax = 0.0, 1.0
        im = ax.imshow(climate["band_series"].T, aspect="auto", cmap="YlGnBu_r", vmin=vmin, vmax=vmax)
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels(["High North", "N. Mid-Lat", "S. Mid-Lat", "High South"])
        ax.set_xlabel("Sampled Frame (Time Progression)")
        ax.set_title("Hovmöller Time × Latitude Intensity Heatmap")
        plt.colorbar(im, ax=ax, label=climate["unit"])
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with s_col:
        st.markdown("**Scientific Context & Provenance**")
        st.write(source_description)
        st.caption(source_mapping)
        if source_url:
            st.markdown(f"[Official NASA SVS Dataset]({source_url}) · {source_credit}")

    # Native Streamlit WAV Renderer & Download
    st.divider()
    st.subheader("💾 High-Precision Stereo WAV Export & Native Player")
    if st.button("Render Lossless Stereo WAV File", use_container_width=True):
        with st.spinner("Synthesizing stereo PCM audio..."):
            wav_data = synthesize_wav_from_features(
                features,
                slices=slices,
                note_seconds=note_seconds,
                profile_name=profile_name,
                scale_name=scale_name,
                enable_drone=enable_drone,
                enable_transients=enable_transients,
                reverb_wet=reverb_wet,
            )
            st.session_state["rendered_wav"] = wav_data

    if "rendered_wav" in st.session_state:
        st.audio(st.session_state["rendered_wav"], format="audio/wav")
        st.download_button(
            "⬇️ Download Stereo WAV Soundscape",
            data=st.session_state["rendered_wav"],
            file_name="earth_jukebox_soundscape.wav",
            mime="audio/wav",
            use_container_width=True,
        )