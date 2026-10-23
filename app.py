import io
import numpy as np
import streamlit as st
from PIL import Image
from scipy.io import wavfile
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Earth Information Jukebox", page_icon="🌍", layout="wide")


def get_pentatonic_scale(base_freq=130.81, octaves=3):
    """
    Generates frequencies for a C Major Pentatonic Scale across multiple octaves.
    Base freq 130.81 Hz = C3
    Pentatonic intervals (semitones): 0, 2, 4, 7, 9
    """
    scale = []
    intervals = [0, 2, 4, 7, 9]
    for octave in range(octaves):
        for interval in intervals:
            semitone = octave * 12 + interval
            freq = base_freq * (2 ** (semitone / 12.0))
            scale.append(freq)
    return np.array(scale)


def synthesize_tone(freq, duration, sample_rate=22050):
    """Generates a soft sine wave tone with an ADSR-style envelope to eliminate clicks."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    waveform = np.sin(2 * np.pi * freq * t)

    # Apply fade-in and fade-out envelope
    envelope_len = int(sample_rate * 0.02)  # 20ms fade
    if len(waveform) > 2 * envelope_len:
        fade_in = np.linspace(0, 1, envelope_len)
        fade_out = np.linspace(1, 0, envelope_len)
        waveform[:envelope_len] *= fade_in
        waveform[-envelope_len:] *= fade_out

    return waveform


def image_to_sonification(image, num_steps=64, step_duration=0.12, sample_rate=22050):
    """
    Converts an Earth observation image frame into a musical audio track.
    Scans the image from left to right in 'num_steps' slices.
    """
    # Convert image to grayscale array
    img_gray = image.convert("L")
    img_arr = np.array(img_gray)

    height, width = img_arr.shape
    step_width = width // num_steps

    scale = get_pentatonic_scale(base_freq=130.81, octaves=3)
    num_notes = len(scale)

    audio_segments = []
    data_profile = []

    for i in range(num_steps):
        # Extract slice along the X-axis
        col_start = i * step_width
        col_end = (i + 1) * step_width
        slice_data = img_arr[:, col_start:col_end]

        # Calculate average pixel intensity (0 to 255) for this slice
        avg_intensity = np.mean(slice_data)
        data_profile.append(avg_intensity)

        # Map intensity (0-255) to a pitch in the pentatonic scale
        note_index = int(np.clip(avg_intensity / 255.0 * (num_notes - 1), 0, num_notes - 1))
        target_freq = scale[note_index]

        # Synthesize tone for this step
        tone = synthesize_tone(target_freq, duration=step_duration, sample_rate=sample_rate)
        
        # Scale volume slightly by intensity
        volume = 0.3 + 0.7 * (avg_intensity / 255.0)
        audio_segments.append(tone * volume)

    # Concatenate all audio segments into one continuous signal
    full_audio = np.concatenate(audio_segments)

    # Normalize audio to 16-bit PCM range
    max_val = np.max(np.abs(full_audio))
    if max_val > 0:
        full_audio = full_audio / max_val
    audio_int16 = (full_audio * 32767).astype(np.int16)

    return audio_int16, data_profile, sample_rate


# --- STREAMLIT DASHBOARD INTERFACE ---

st.title("🌍 The Earth Information Jukebox")
st.markdown(
    "Translating Earth Information Center (EIC) visual data frames into dynamic real-time audio."
)

col1, col2 = st.sidebar, st.container()

with col1:
    st.header("1. Controls & Audio Tuning")

    uploaded_file = st.file_uploader(
        "Upload an Earth Visual Frame (JPEG/PNG)", type=["jpg", "jpeg", "png"]
    )

    num_steps = st.slider("Scanning Resolution (Notes)", min_value=16, max_value=128, value=64, step=8)
    step_duration = st.slider("Note Duration (seconds)", min_value=0.05, max_value=0.30, value=0.12, step=0.01)

# Main Workspace
if uploaded_file is not None:
    image = Image.open(uploaded_file)

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Source Image Frame")
        st.image(image, use_column_width=True)

    # Process audio
    audio_data, data_profile, sample_rate = image_to_sonification(
        image, num_steps=num_steps, step_duration=step_duration
    )

    # Convert to WAV in-memory buffer
    wav_io = io.BytesIO()
    wavfile.write(wav_io, sample_rate, audio_data)
    wav_bytes = wav_io.getvalue()

    with c2:
        st.subheader("Data Sonification Output")
        st.audio(wav_bytes, format="audio/wav")

        # Plot the data scanline
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(data_profile, color="#00A8E8", linewidth=2)
        ax.set_title("Extracted Data Intensity Scanline")
        ax.set_xlabel("Time Step (Longitude Scan)")
        ax.set_ylabel("Average Intensity / Value")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

else:
    st.info("👈 Upload an Earth satellite image from the sidebar to generate sonification.")

    # Generate a demo synthetic earth-like grid if no file uploaded
    if st.button("Generate Demo Earth Pattern"):
        x = np.linspace(-2 * np.pi, 2 * np.pi, 256)
        y = np.linspace(-2 * np.pi, 2 * np.pi, 256)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y) * 127.5 + 127.5
        demo_img = Image.fromarray(Z.astype(np.uint8))

        st.subheader("Demo Earth Frame (Harmonic Wave)")
        st.image(demo_img, width=400)

        audio_data, data_profile, sample_rate = image_to_sonification(
            demo_img, num_steps=num_steps, step_duration=step_duration
        )

        wav_io = io.BytesIO()
        wavfile.write(wav_io, sample_rate, audio_data)
        st.audio(wav_io.getvalue(), format="audio/wav")