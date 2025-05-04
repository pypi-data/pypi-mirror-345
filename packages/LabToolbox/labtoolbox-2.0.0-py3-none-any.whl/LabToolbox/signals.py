from LabToolbox import np, plt
from scipy.integrate import quad

# def fourier(x, y, type = 'd'):

#     # type: d = discrete
#     #       f = fast

#     return

def fa(f, n, T):
    return lambda x: f(x) * np.cos(2 * np.pi * n * x / T)

def fb(f, n, T):
    return lambda x: f(x) * np.sin(2 * np.pi * n * x / T)

def period(x, y):
    """
    Verifica se i dati sono periodici e stima il periodo principale.

    Parametri
    ---------
    x : array_like
        Ascisse (devono essere equispaziate).
    y : array_like
        Ordinata (i dati da analizzare).
    plot_spectrum : bool
        Se True, mostra lo spettro di Fourier per ispezione.

    Ritorna
    -------
    period : float or None
        Il periodo stimato, se rilevato. None se non periodico.
    """

    # Controllo: x deve essere equispaziato
    dx = np.diff(x)
    if not np.allclose(dx, dx[0], rtol=1e-2):
        raise ValueError("I dati devono essere campionati su un intervallo equispaziato.")

    N = len(x)
    T = x[1] - x[0]  # intervallo di campionamento

    # FFT e spettro delle frequenze
    fft_vals = np.fft.fft(y - np.mean(y))  # rimuovi la media per migliorare la DFT
    fft_freqs = np.fft.fftfreq(N, d=T)

    # Considera solo parte positiva dello spettro
    positive_freqs = fft_freqs[:N // 2]
    amplitudes = np.abs(fft_vals[:N // 2])

    # Ignora la frequenza nulla (offset)
    amplitudes[0] = 0

    # Trova frequenza dominante
    peak_index = np.argmax(amplitudes)
    dominant_freq = positive_freqs[peak_index]

    if dominant_freq == 0:
        return None  # non periodico

    period = 1 / dominant_freq

    return period

def spectrum(x, y):

    # spettro di potenza + grafico

    return

def dfs(t, data, deg, plot = True):
    """
    """

    # serie di fourier DISCRETA

    T = period(t, data)

    if T is None:
        raise ValueError("La funzione non è periodica")

    # se la 'funzione' non è periodica, raise ValueError("La funzione non è periodica")

    # fare il plot con la funzione di partenza e la sdf con label "degree = ..."
    # deve calcolare il chi2red e pvalue e printarlo

    # return a, b, f_approx, chi2red, pvalue

def compute_fourier_series(f, interval, order, num_points=1000):
    """
    Compute the Fourier series approximation of a function f(x)
    
    Parameters
    ----------
    f : callable
        Function to approximate.
    interval : tuple of float
        The interval (a, b) over which to compute the Fourier series.
    order : int
        Number of Fourier modes (n) to use in the approximation.
    num_points : int, optional
        Number of points for plotting (default is 1000).
        
    Returns
    -------
    x : ndarray
        Array of points in the interval.
    f_original : ndarray
        Original function evaluated at x.
    f_approx : ndarray
        Fourier approximation evaluated at x.
    """

    a, b = interval
    T = b - a  # Period
    L = T / 2
    x = np.linspace(a, b, num_points)
    
    # Compute a0 separately
    a0, _ = quad(lambda x_: f(x_), a, b)
    a0 /= L

    # Compute coefficients a_n and b_n
    a_n = []
    b_n = []

    for n in range(1, order + 1):
        an, _ = quad(lambda x_: f(x_) * np.cos(n * np.pi * (x_ - a) / L), a, b)
        bn, _ = quad(lambda x_: f(x_) * np.sin(n * np.pi * (x_ - a) / L), a, b)
        a_n.append(an / L)
        b_n.append(bn / L)

    # Build the Fourier approximation
    f_approx = np.full_like(x, a0 / 2)

    for n in range(1, order + 1):
        f_approx += (
            a_n[n - 1] * np.cos(n * np.pi * (x - a) / L) +
            b_n[n - 1] * np.sin(n * np.pi * (x - a) / L)
        )

    f_original = f(x)

    # Plot
    plt.plot(x, f_original, label="Original Function", lw=0.8)
    plt.plot(x, f_approx, '--', label=f"Fourier Approximation (order = {order})", lw=0.8)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.legend()

    return x, f_original, f_approx

def spectrogram():

    return