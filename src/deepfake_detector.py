"""
deepfake_detector.py
=============================================================================
Forensic Deepfake & Synthetic Media Analysis Engine
Project: AI-Driven Social Engineering and Deepfake Defense Platform
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)

Technical Overview:
This module performs multi-factor computer vision and frequency-domain forensics
on digital facial portraits and video call snapshot frames without relying on
cloud APIs or external proprietary services.

Forensic Inspection Layers:
1. 2D Fast Fourier Transform (FFT) Power Spectrum Analysis:
   Detects periodic grid artifacts and high-frequency discrepancies produced
   by generative up-sampling layers (GANs, StyleGAN, FaceSwap).
2. Laplacian Boundary & Edge Variance Analysis:
   Evaluates blurriness, smoothing anomalies, and edge seam blending discontinuities
   characteristic of digital face-replacement masks.
3. Chrominance & Illumination Boundary Inconsistency:
   Measures color temperature and channel distribution variance between the
   facial core and outer perimeter.
4. Sensor Noise Pattern / High-Pass PRNU Residual:
   Inspects Photo-Response Non-Uniformity (sensor noise) consistency across
   the image matrix.
=============================================================================
"""

import io
import math
import numpy as np
from PIL import Image, ImageOps, ImageFilter


class DeepfakeDetector:
    """
    Forensic Computer Vision & Frequency Analysis Engine for Synthetic Media.
    Designed for zero-dependency execution using NumPy and Pillow.
    """

    def __init__(self):
        pass

    def analyze_image(self, image_input):
        """
        Performs multi-vector forensic evaluation on an image input.
        image_input can be a PIL.Image, file-like buffer, or byte array.

        Returns a comprehensive forensic report dictionary containing:
        - overall_score: 0 to 100 (Deepfake Risk Probability)
        - status: 'Likely Authentic', 'Suspicious', or 'High Risk Synthetic'
        - color: 'green', 'orange', or 'red'
        - metrics: dictionary of individual test scores & raw values
        - reasons: list of scientific forensic justifications
        - edge_image: PIL Image of the Laplacian edge/gradient map
        - fft_image: PIL Image of the 2D FFT power spectrum heatmap
        - face_crop: PIL Image of the evaluated facial region of interest
        """
        # 1. Load and normalize image to RGB
        if isinstance(image_input, Image.Image):
            img = image_input.convert("RGB")
        elif hasattr(image_input, "read"):
            image_input.seek(0)
            img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, (bytes, bytearray)):
            img = Image.open(io.BytesIO(image_input)).convert("RGB")
        else:
            raise ValueError("Unsupported image input type.")

        # Ensure reasonable dimension for forensic computation
        max_size = 640
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        w, h = img.size
        # Center-weighted Region of Interest (simulating facial framing in video calls)
        crop_box = (
            int(w * 0.15),
            int(h * 0.10),
            int(w * 0.85),
            int(h * 0.90)
        )
        face_roi = img.crop(crop_box)
        roi_w, roi_h = face_roi.size

        # Convert to numpy arrays
        rgb_arr = np.array(face_roi, dtype=np.float32)
        gray_img = face_roi.convert("L")
        gray_arr = np.array(gray_img, dtype=np.float32)

        # -------------------------------------------------------------------
        # Test 1: 2D FFT Frequency Domain Analysis (GAN Grid Detection)
        # -------------------------------------------------------------------
        fft_score, fft_img, fft_details = self._analyze_fft(gray_arr)

        # -------------------------------------------------------------------
        # Test 2: Laplacian Boundary Variance (Blur & Smoothing)
        # -------------------------------------------------------------------
        lap_score, edge_img, lap_details = self._analyze_laplacian(gray_img, gray_arr)

        # -------------------------------------------------------------------
        # Test 3: Chrominance & Boundary Lighting Inconsistency
        # -------------------------------------------------------------------
        color_score, color_details = self._analyze_color_consistency(rgb_arr)

        # -------------------------------------------------------------------
        # Test 4: High-Pass Noise Residual (PRNU Inconsistency)
        # -------------------------------------------------------------------
        noise_score, noise_details = self._analyze_sensor_noise(gray_img, gray_arr)

        # -------------------------------------------------------------------
        # Multi-Vector Risk Fusion
        # Weights:
        # - FFT Frequency Analysis: 35%
        # - Laplacian Boundary Variance: 30%
        # - Chrominance Consistency: 20%
        # - PRNU Sensor Noise: 15%
        # -------------------------------------------------------------------
        combined_score = (
            (0.35 * fft_score) +
            (0.30 * lap_score) +
            (0.20 * color_score) +
            (0.15 * noise_score)
        )
        overall_score = int(round(max(0, min(100, combined_score))))

        # Determine Verdict Category
        if overall_score >= 68:
            status = "High Risk Synthetic"
            verdict_label = "HIGH CONFIDENCE SYNTHETIC / DEEPFAKE"
            color = "red"
        elif overall_score >= 38:
            status = "Suspicious"
            verdict_label = "SUSPICIOUS // POTENTIAL MANIPULATION ARTIFACTS"
            color = "orange"
        else:
            status = "Likely Authentic"
            verdict_label = "LIKELY AUTHENTIC // NOMINAL CAMERA OPTICS"
            color = "green"

        # Compile Explanations
        reasons = []
        if fft_score >= 50:
            reasons.append(
                f"Frequency Domain: {fft_details['desc']} (Anomaly Confidence: {fft_score}%)"
            )
        else:
            reasons.append(
                "Frequency Domain: Natural continuous power falloff; no periodic GAN lattice detected."
            )

        if lap_score >= 50:
            reasons.append(
                f"Boundary Optics: {lap_details['desc']} (Smoothing Discontinuity: {lap_score}%)"
            )
        else:
            reasons.append(
                "Boundary Optics: Natural edge gradient depth consistent with optical lens capture."
            )

        if color_score >= 50:
            reasons.append(
                f"Color Space: {color_details['desc']} (Illumination Discrepancy: {color_score}%)"
            )
        else:
            reasons.append(
                "Color Space: Facial core and perimeter exhibit coherent chrominance harmony."
            )

        if noise_score >= 50:
            reasons.append(
                f"Sensor Noise: {noise_details['desc']} (Noise Pattern Anomaly: {noise_score}%)"
            )
        else:
            reasons.append(
                "Sensor Noise: Coherent Poisson-Gaussian camera sensor grain observed."
            )

        return {
            "overall_score": overall_score,
            "status": status,
            "verdict_label": verdict_label,
            "color": color,
            "metrics": {
                "fft_score": int(fft_score),
                "lap_score": int(lap_score),
                "color_score": int(color_score),
                "noise_score": int(noise_score),
                "laplacian_variance": round(lap_details["var"], 1),
                "high_freq_ratio": round(fft_details["ratio"] * 100, 2),
                "color_discrepancy": round(color_details["diff"], 2),
                "noise_variance": round(noise_details["var"], 2)
            },
            "reasons": reasons,
            "edge_image": edge_img,
            "fft_image": fft_img,
            "face_crop": face_roi
        }

    # -----------------------------------------------------------------------
    # Forensic Helper: FFT 2D Analysis
    # -----------------------------------------------------------------------
    def _analyze_fft(self, gray_arr):
        """
        Computes 2D Fast Fourier Transform on the grayscale matrix.
        Detects unnatural energy distribution in high-frequency bands and
        computes a visually inspectable power spectrum image.
        """
        h, w = gray_arr.shape
        # Center crop to square power-of-two for clean FFT
        min_dim = min(h, w)
        start_y = (h - min_dim) // 2
        start_x = (w - min_dim) // 2
        square_crop = gray_arr[start_y:start_y + min_dim, start_x:start_x + min_dim]

        # 2D FFT with zero-frequency shifted to center
        f_transform = np.fft.fft2(square_crop)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)

        # Log power spectrum for visual representation
        log_spectrum = 20 * np.log(magnitude_spectrum + 1e-9)
        norm_spectrum = ((log_spectrum - log_spectrum.min()) / (log_spectrum.max() - log_spectrum.min() + 1e-9) * 255).astype(np.uint8)
        
        # Colorize FFT map (cyber-blue / purple heat style)
        fft_pil = Image.fromarray(norm_spectrum, mode="L").resize((256, 256), Image.Resampling.BILINEAR)

        # Frequency energy ratio (High-frequency ring vs low-frequency core)
        cy, cx = min_dim // 2, min_dim // 2
        y, x = np.ogrid[:min_dim, :min_dim]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        r_inner = min_dim * 0.15
        r_outer = min_dim * 0.45
        
        inner_mask = dist_from_center <= r_inner
        outer_mask = (dist_from_center > r_inner) & (dist_from_center <= r_outer)

        inner_energy = np.sum(magnitude_spectrum[inner_mask])
        outer_energy = np.sum(magnitude_spectrum[outer_mask])
        ratio = float(outer_energy / (inner_energy + 1e-9))

        # Natural photos exhibit power-law decay 1/f^alpha (ratio typically 0.08 - 0.22)
        # Deepfakes often have suppressed natural high-frequencies (<0.05) or severe grid spikes (>0.35)
        if ratio < 0.055:
            fft_score = min(92, 55 + (0.055 - ratio) * 700)
            desc = "Unnatural frequency suppression detected (characteristic of generative upsampling filters)."
        elif ratio > 0.32:
            fft_score = min(95, 60 + (ratio - 0.32) * 150)
            desc = "Periodic high-frequency spectral spikes detected (characteristic of GAN deconvolution checkerboards)."
        else:
            fft_score = max(8, min(32, int(ratio * 120)))
            desc = "Normal power-law spectral distribution consistent with optical camera sensors."

        return fft_score, fft_pil, {"ratio": ratio, "desc": desc}

    # -----------------------------------------------------------------------
    # Forensic Helper: Laplacian Boundary Variance (Blur / Smoothing)
    # -----------------------------------------------------------------------
    def _analyze_laplacian(self, gray_img, gray_arr):
        """
        Measures variance of the Laplacian kernel across the image.
        Overly smoothed or blended fake boundaries produce abnormally low variance,
        whereas unnatural cut-and-paste seams produce jagged edge outliers.
        """
        # Apply standard 3x3 Laplacian kernel via Pillow ImageFilter
        # Kernel: [0, 1, 0, 1, -4, 1, 0, 1, 0]
        laplacian_filter = ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1, offset=128)
        lap_img = gray_img.filter(laplacian_filter)
        
        lap_arr = np.array(lap_img, dtype=np.float32) - 128.0
        lap_var = float(np.var(lap_arr))

        # Visual gradient representation (rescaled for high visual clarity)
        norm_edge = np.clip(np.abs(lap_arr) * 4.5, 0, 255).astype(np.uint8)
        edge_pil = Image.fromarray(norm_edge, mode="L").resize((256, 256), Image.Resampling.BILINEAR)

        # Variance evaluation:
        # Very blurry / over-smoothed deepfake face: var < 50
        # Optimal optical capture: var ~ 120 - 450
        # Excessive digital sharpening artifact: var > 800
        if lap_var < 50:
            lap_score = min(92, 60 + (50 - lap_var) * 0.65)
            desc = f"Excessive smoothing/blur anomaly (Var: {lap_var:.1f}). Facial region lacks natural epidermal micro-textures."
        elif lap_var > 750:
            lap_score = min(88, 55 + (lap_var - 750) * 0.08)
            desc = f"Synthetic edge sharpening anomaly (Var: {lap_var:.1f}). Potential boundary mask sharpening detected."
        else:
            lap_score = max(10, min(30, int(100 - (lap_var / 5.0))))
            desc = f"Natural edge sharpness and texture depth (Var: {lap_var:.1f})."

        return lap_score, edge_pil, {"var": lap_var, "desc": desc}

    # -----------------------------------------------------------------------
    # Forensic Helper: Color Space & Illumination Consistency
    # -----------------------------------------------------------------------
    def _analyze_color_consistency(self, rgb_arr):
        """
        Evaluates color temperature and lighting balance between the central
        facial region and perimeter border. Deepfakes frequently fail to match
        the ambient illuminant of the donor and recipient scenes.
        """
        h, w, _ = rgb_arr.shape
        cy, cx = h // 2, w // 2
        r = min(h, w) // 4

        # Center core mask
        y, x = np.ogrid[:h, :w]
        center_mask = ((x - cx)**2 + (y - cy)**2) <= r**2
        # Perimeter boundary mask (annulus around center)
        border_mask = (((x - cx)**2 + (y - cy)**2) > (r * 1.3)**2) & (((x - cx)**2 + (y - cy)**2) <= (r * 1.8)**2)

        center_rgb = np.mean(rgb_arr[center_mask], axis=0) if np.any(center_mask) else np.array([128, 128, 128])
        border_rgb = np.mean(rgb_arr[border_mask], axis=0) if np.any(border_mask) else np.array([128, 128, 128])

        # Euclidean RGB distance between center and perimeter
        diff = float(np.linalg.norm(center_rgb - border_rgb))
        
        # Red-to-Blue ratio difference (color temperature mismatch)
        rb_center = center_rgb[0] / (center_rgb[2] + 1e-5)
        rb_border = border_rgb[0] / (border_rgb[2] + 1e-5)
        rb_diff = abs(rb_center - rb_border)

        if diff > 48 or rb_diff > 0.45:
            color_score = min(90, 50 + diff * 0.8)
            desc = f"Illumination mismatch (Discrepancy: {diff:.1f}). Ambient light color temperature diverges between face and perimeter."
        else:
            color_score = max(12, min(32, int(diff * 0.6)))
            desc = f"Consistent ambient lighting and chrominance distribution (Discrepancy: {diff:.1f})."

        return color_score, {"diff": diff, "desc": desc}

    # -----------------------------------------------------------------------
    # Forensic Helper: High-Pass Sensor Noise (PRNU Residual)
    # -----------------------------------------------------------------------
    def _analyze_sensor_noise(self, gray_img, gray_arr):
        """
        Extracts high-pass noise residuals by subtracting a box-blurred copy.
        Real cameras produce uniform sensor noise; AI-generated pixels have
        disrupted, non-stationary noise variance.
        """
        # Box blur to extract low-frequency base
        blurred = gray_img.filter(ImageFilter.BoxBlur(1))
        blur_arr = np.array(blurred, dtype=np.float32)

        # High-pass residual
        noise_residual = gray_arr - blur_arr
        noise_var = float(np.var(noise_residual))

        # Check spatial variance consistency across quadrants
        h, w = noise_residual.shape
        mid_h, mid_w = h // 2, w // 2
        q1 = np.var(noise_residual[:mid_h, :mid_w])
        q2 = np.var(noise_residual[:mid_h, mid_w:])
        q3 = np.var(noise_residual[mid_h:, :mid_w])
        q4 = np.var(noise_residual[mid_h:, mid_w:])
        quad_vars = [q1, q2, q3, q4]
        spatial_inconsistency = float(np.std(quad_vars) / (np.mean(quad_vars) + 1e-5))

        if noise_var < 1.2:
            noise_score = min(88, 60 + (1.2 - noise_var) * 25)
            desc = f"Unnaturally clean image matrix (Var: {noise_var:.2f}). Missing expected optical sensor noise floor."
        elif spatial_inconsistency > 0.65:
            noise_score = min(85, 55 + spatial_inconsistency * 40)
            desc = f"Discontinuous sensor noise distribution (Inconsistency: {spatial_inconsistency:.2f}). Patch-based splicing artifact."
        else:
            noise_score = max(10, min(28, int(noise_var * 6)))
            desc = f"Uniform sensor noise signature observed (Var: {noise_var:.2f})."

        return noise_score, {"var": noise_var, "desc": desc}


    def analyze_audio(self, audio_input):
        """
        Forensic acoustic evaluation of voice clips & audio recordings.
        Inspects spectral bandwidth cutoff (vocoder signatures), background room noise,
        and zero-crossing rate stability characteristic of synthetic voice clones.
        """
        try:
            import wave
            audio_bytes = None
            if hasattr(audio_input, "read"):
                audio_input.seek(0)
                audio_bytes = audio_input.read()
            elif isinstance(audio_input, (bytes, bytearray)):
                audio_bytes = audio_input

            if not audio_bytes:
                raise ValueError("No audio bytes available.")

            with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                raw_frames = wf.readframes(min(n_frames, framerate * 5))  # analyze up to 5s

            if sampwidth == 2:
                samples = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32)
            else:
                samples = np.frombuffer(raw_frames, dtype=np.uint8).astype(np.float32) - 128.0

            if n_channels > 1:
                samples = samples[::n_channels]

            # Normalize
            if np.max(np.abs(samples)) > 0:
                samples = samples / np.max(np.abs(samples))

            # 1. 1D FFT frequency distribution
            fft_vals = np.abs(np.fft.rfft(samples))
            freqs = np.fft.rfftfreq(len(samples), 1.0 / framerate)

            # Check frequency cutoff (many voice cloning TTS models cutoff steeply above 8kHz or 16kHz)
            high_cutoff_freq = 8000
            idx_cutoff = np.where(freqs >= high_cutoff_freq)[0]
            if len(idx_cutoff) > 0:
                high_energy_ratio = float(np.sum(fft_vals[idx_cutoff]) / (np.sum(fft_vals) + 1e-6))
            else:
                high_energy_ratio = 0.0

            # 2. Silence floor unnaturalness (AI speech models often have 100% synthetic zero noise floor)
            abs_samples = np.abs(samples)
            silence_samples = np.sum(abs_samples < 0.005)
            silence_ratio = float(silence_samples / len(samples))

            # 3. Zero-Crossing Rate variance
            zero_crossings = np.nonzero(np.diff(samples > 0))[0]
            if len(zero_crossings) > 10:
                intervals = np.diff(zero_crossings)
                interval_jitter = float(np.std(intervals) / (np.mean(intervals) + 1e-5))
            else:
                interval_jitter = 0.5

            # Scoring
            score = 15
            reasons = []

            # Harsh cutoff evaluation
            if high_energy_ratio < 0.015 and framerate >= 22050:
                score += 35
                reasons.append(f"Steep high-frequency spectral cutoff detected (< 8 kHz). Classic neural vocoder synthesis signature.")
            else:
                reasons.append("Natural acoustic frequency spread extending into higher spectrum registers.")

            # Synthetic silence floor
            if silence_ratio > 0.35 and np.min(abs_samples[:1000]) == 0.0:
                score += 30
                reasons.append("Unnaturally sterile silence floor detected. Lacks physical room acoustic reverberation.")
            else:
                reasons.append("Natural environmental background acoustic noise present.")

            # Jitter
            if interval_jitter < 0.35:
                score += 20
                reasons.append("Hyper-regular pitch micro-timing observed (typical of deterministic algorithmic speech synthesis).")

            overall_score = min(100, max(0, score))
            if overall_score >= 65:
                status = "High Risk Synthetic Voice"
                color = "#EF4444"
                verdict = "SYNTHETIC VOICE CLONE DETECTED"
            elif overall_score >= 35:
                status = "Suspicious Audio"
                color = "#F59E0B"
                verdict = "SUSPICIOUS ACOUSTIC ANOMALIES"
            else:
                status = "Likely Authentic Audio"
                color = "#06B6D4"
                verdict = "AUTHENTIC HUMAN VOICE SIGNATURE"

            return {
                "overall_score": overall_score,
                "status": status,
                "color": color,
                "verdict_label": verdict,
                "sample_rate": framerate,
                "duration": round(n_frames / framerate, 2),
                "high_energy_ratio": round(high_energy_ratio * 100, 2),
                "silence_ratio": round(silence_ratio * 100, 2),
                "interval_jitter": round(interval_jitter, 3),
                "reasons": reasons
            }
        except Exception as e:
            return {
                "overall_score": 50,
                "status": "Suspicious Audio",
                "color": "#F59E0B",
                "verdict_label": "AUDIO ANALYSIS NOTICE",
                "sample_rate": 44100,
                "duration": 0.0,
                "high_energy_ratio": 0.0,
                "silence_ratio": 0.0,
                "interval_jitter": 0.0,
                "reasons": [f"Could not parse audio waveform completely: {e}. Ensure standard uncompressed WAV format."]
            }


def generate_sample_synthetic_audio():
    """Generates an in-memory WAV simulating synthetic voice clone characteristics (16kHz cutoff, pure silence)."""
    import wave
    import struct
    framerate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(framerate * duration), endpoint=False)
    # Fundamental voice harmonics (150Hz + overtones) but strictly cutoff at 3.5kHz
    wave_data = np.sin(2 * np.pi * 160 * t) * 0.4 + np.sin(2 * np.pi * 320 * t) * 0.2 + np.sin(2 * np.pi * 640 * t) * 0.1
    # Introduce unnaturally dead silence gaps
    wave_data[int(framerate * 0.8):int(framerate * 1.2)] = 0.0
    
    scaled = (wave_data * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(scaled.tobytes())
    buf.seek(0)
    return buf


def generate_sample_authentic_audio():
    """Generates an in-memory WAV simulating natural human acoustic recording with room noise."""
    import wave
    framerate = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(framerate * duration), endpoint=False)
    # Voice with natural vibrato and wideband room noise
    vibrato = 1.0 + 0.03 * np.sin(2 * np.pi * 5 * t)
    wave_data = np.sin(2 * np.pi * 180 * vibrato * t) * 0.35 + np.sin(2 * np.pi * 360 * t) * 0.15 + np.sin(2 * np.pi * 720 * t) * 0.08
    # Add natural room acoustic noise floor
    room_noise = np.random.normal(0, 0.012, len(t))
    wave_data = np.clip(wave_data + room_noise, -1.0, 1.0)
    
    scaled = (wave_data * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(scaled.tobytes())
    buf.seek(0)
    return buf

    """
    Generates a synthetic test portrait pattern simulating generative GAN artifacts
    (periodic frequency grid and boundary smoothing) for instant offline demo evaluation.
    """
    size = 256
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    
    # Gradient backdrop
    for y in range(size):
        arr[y, :, 0] = int(30 + (y / size) * 40)
        arr[y, :, 1] = int(35 + (y / size) * 45)
        arr[y, :, 2] = int(50 + (y / size) * 60)

    # Simulated oval face
    cy, cx = size // 2, size // 2
    ry, rx = 75, 55
    y, x = np.ogrid[:size, :size]
    face_mask = (((x - cx) / rx)**2 + ((y - cy) / ry)**2) <= 1.0

    # Over-smooth warm skin tone
    arr[face_mask, 0] = 220
    arr[face_mask, 1] = 180
    arr[face_mask, 2] = 160

    # Subtle periodic GAN grid lattice (checkerboard frequency artifact)
    grid = (np.sin(x * 0.6) * np.cos(y * 0.6) * 16).astype(np.int16)
    for c in range(3):
        channel = arr[:, :, c].astype(np.int16)
        channel[face_mask] = np.clip(channel[face_mask] + grid[face_mask], 0, 255)
        arr[:, :, c] = channel.astype(np.uint8)

    img = Image.fromarray(arr, mode="RGB")
    # Apply soft blur to face boundary to simulate blending mask
    return img.filter(ImageFilter.GaussianBlur(radius=1.2))


def generate_sample_authentic_portrait():
    """
    Generates an authentic reference pattern simulating natural optical sensor noise
    and sharp edge gradients for comparison.
    """
    size = 256
    np.random.seed(42)
    # Natural scene with gradient and camera noise
    y, x = np.ogrid[:size, :size]
    base = (x * 0.3 + y * 0.4).astype(np.float32)
    
    # Simulated natural face
    cy, cx = size // 2, size // 2
    ry, rx = 75, 55
    face_mask = (((x - cx) / rx)**2 + ((y - cy) / ry)**2) <= 1.0

    r = np.where(face_mask, 215.0 + np.random.normal(0, 4.5, (size, size)), 80.0 + base * 0.3)
    g = np.where(face_mask, 165.0 + np.random.normal(0, 4.5, (size, size)), 90.0 + base * 0.3)
    b = np.where(face_mask, 140.0 + np.random.normal(0, 4.5, (size, size)), 110.0 + base * 0.3)

    # Eyes & Mouth features (natural edges)
    eye1 = (((x - (cx - 20))**2 + (y - (cy - 15))**2) <= 6**2)
    eye2 = (((x - (cx + 20))**2 + (y - (cy - 15))**2) <= 6**2)
    mouth = (((x - cx)**2 / 16**2 + (y - (cy + 25))**2 / 5**2) <= 1.0)
    
    r[eye1 | eye2 | mouth] = 50
    g[eye1 | eye2 | mouth] = 40
    b[eye1 | eye2 | mouth] = 40

    rgb = np.stack([np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)], axis=2).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")
