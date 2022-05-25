import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import util.approximate_sinusoid_int as u_asi
import util.spectrogram

PLOT_DFT = False

"""Parameters"""
samples: int = 512
sample_frequency: int = 48e3 / 2
k: int = 193
bits: int = 16

"""Test Signal (int16)"""
x = np.arange(samples)
test_signal = np.zeros(x.shape)

# [Hz, magnitude]
test_signal_components = [[4.2e3, 23210], [450, 1200]]

for (f, m) in test_signal_components:
    test_signal += m * np.sin(2 * np.pi * (f / sample_frequency) * x)
test_signal_int = np.array(test_signal).astype(int)
np.savetxt(os.getcwd() + f"/generated/int{bits}_signal.txt", test_signal_int, fmt="%d")


"""Generate Sinusoid Approximations"""
(df, x, ys, (cos_w, sin_nw)) = u_asi.approximate_sinusoid_int(
    samples, sample_frequency, k, bits, debug=True
)
np.savetxt(
    os.getcwd() + f"/generated/int{bits}_cos.txt", df["y_cos_est"].values, fmt="%d"
)
np.savetxt(
    os.getcwd() + f"/generated/int{bits}_sin.txt", df["y_sin_est"].values, fmt="%d"
)

"""Save Parameter Configuration"""
msg = [
    f"samples: {samples}, sample_frequency: {sample_frequency}",
    f"k: {k}, sinusoid bits: {bits}",
    "",
    f"cos(wk)= {cos_w}",
    f"-sin(wk)= {sin_nw}",
]
with open(os.getcwd() + "/generated/parameters.txt", "w") as f:
    f.writelines("\n".join(msg))

"""Generate DFT"""
(dft_re, dft_im, dft_magnitude, k_frequencies) = util.spectrogram.dft_int16(
    test_signal_int, sample_frequency
)
np.savetxt(os.getcwd() + f"/generated/int{bits}_dft_re.txt", dft_re, fmt="%d")
np.savetxt(os.getcwd() + f"/generated/int{bits}_dft_im.txt", dft_im, fmt="%d")
np.savetxt(os.getcwd() + f"/generated/int{bits}_dft_mag.txt", dft_magnitude, fmt="%d")


"""Visualise"""
if PLOT_DFT:
    df = pd.DataFrame(
        {
            "fk": k_frequencies,
            "dft_re": dft_re,
            "dft_im": dft_im,
            "dft_magnitude": dft_magnitude,
        }
    )

    # Subplot DFT (for report)
    subplot = make_subplots(rows=2, cols=1)
    subplot.add_trace(
        go.Scatter(name="Signal", x=k_frequencies, y=test_signal), row=1, col=1
    )
    subplot.add_trace(
        go.Scatter(name="DFT Re", x=k_frequencies, y=dft_re), row=2, col=1
    )
    subplot.add_trace(
        go.Scatter(name="DFT Im", x=k_frequencies, y=dft_im), row=2, col=1
    )
    subplot.add_trace(
        go.Scatter(name="DFT", x=k_frequencies, y=dft_magnitude), row=2, col=1
    )
    subplot.update_layout(
        title="DFT", xaxis_title="Frequency (Hz)", yaxis_title="Magnitude (linear)"
    )
    subplot.show()
