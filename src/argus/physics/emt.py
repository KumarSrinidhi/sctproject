"""Effective-medium models for particle-filled composites.

Conventions (enforced everywhere in this package):

* ``phi``  filler VOLUME FRACTION in [0, 1], not percent.
* ``k*``   thermal conductivities in W/(m K); ``km`` matrix, ``kf`` filler.
* ``p``    spheroid aspect ratio a3/a1 = t/D, where a3 is the semi-axis along the
           symmetry axis. p < 1 platelet, p = 1 sphere, p > 1 needle. Papers that
           quote "aspect ratio" D/t must be inverted first.
* ``r_k``  interfacial (Kapitza) resistance in m^2 K/W, referenced to the particle
           SEMI-axes as in Nan et al. (1997). Yuan et al. (2016) reference the full
           platelet thickness, so their R_b equals 2 * r_k here.
* ``cos2`` <cos^2 theta>, theta = angle between the measurement axis x3 and the
           particle symmetry axis (the platelet normal). 1/3 random; 1 = platelets
           lying flat (heat flows through their thickness); 0 = platelets standing
           up (heat flows along their basal planes).

Sources: equations as compiled in docs/reports/BN epoxy thermal conductivity
research.md (Nan 1997 via Yuan et al. 2016 and Danayat et al. 2022; Hasselman &
Johnson 1987, Lewis & Nielsen 1970, Every et al. 1992, Foygel et al. 2005).
Hashin-Shtrikman, symmetric Bruggeman and Agari-Uno are standard textbook forms,
checked here only by their limits (tests/test_physics.py).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq

ArrayLike = float | np.ndarray


def _a(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


def _check_phi(phi: np.ndarray) -> None:
    if np.any((phi < 0) | (phi > 1)):
        raise ValueError("phi is a volume FRACTION in [0, 1] (did you pass percent?)")


# --------------------------------------------------------------------------- bounds

def parallel(phi: ArrayLike, km: float, kf: float) -> np.ndarray:
    """Wiener upper bound (rule of mixtures): rigorous for any two-phase geometry."""
    phi = _a(phi)
    _check_phi(phi)
    return (1 - phi) * km + phi * kf


def series(phi: ArrayLike, km: float, kf: float) -> np.ndarray:
    """Wiener lower bound (inverse rule of mixtures), assuming perfect interfaces."""
    phi = _a(phi)
    _check_phi(phi)
    return 1.0 / ((1 - phi) / km + phi / kf)


def hashin_shtrikman(phi: ArrayLike, km: float, kf: float) -> tuple[np.ndarray, np.ndarray]:
    """Hashin-Shtrikman (1962) bounds for an ISOTROPIC two-phase composite.
    Returns (lower, upper). For kf > km the lower bound equals Maxwell-Garnett."""
    phi = _a(phi)
    _check_phi(phi)
    lo_k, hi_k = min(km, kf), max(km, kf)
    phi_hi = phi if kf >= km else 1 - phi  # volume fraction of the more conductive phase
    lower = lo_k + phi_hi / (1.0 / (hi_k - lo_k) + (1 - phi_hi) / (3 * lo_k)) if hi_k > lo_k else np.full_like(phi, lo_k)
    upper = hi_k + (1 - phi_hi) / (1.0 / (lo_k - hi_k) + phi_hi / (3 * hi_k)) if hi_k > lo_k else np.full_like(phi, hi_k)
    return _a(lower), _a(upper)


# --------------------------------------------------------------------------- dilute / Maxwell family

def maxwell_garnett(phi: ArrayLike, km: float, kf: float) -> np.ndarray:
    """Maxwell / Maxwell-Garnett: non-interacting spheres, perfect interfaces (dilute)."""
    phi = _a(phi)
    _check_phi(phi)
    d = kf - km
    return km * (kf + 2 * km + 2 * phi * d) / (kf + 2 * km - phi * d)


def maxwell_limit_ratio(phi: ArrayLike) -> np.ndarray:
    """k/km of Maxwell-Garnett as kf -> infinity: (1 + 2 phi) / (1 - phi).
    No isolated-sphere model can exceed this; data above it need contacts,
    percolation, anisotropic particles or alignment to explain."""
    phi = _a(phi)
    _check_phi(phi)
    with np.errstate(divide="ignore"):
        return (1 + 2 * phi) / (1 - phi)


def hasselman_johnson(phi: ArrayLike, km: float, kf: float, radius_m: float, r_k: float) -> np.ndarray:
    """Hasselman & Johnson (1987): Maxwell spheres of radius a with interfacial
    resistance r_k (m^2 K/W). r_k = 0 gives Maxwell-Garnett."""
    phi = _a(phi)
    _check_phi(phi)
    x = kf / km
    y = kf * r_k / radius_m  # = kf / (a h_c)
    num = 2 * phi * (x - y - 1) + x + 2 * y + 2
    den = phi * (1 - x + y) + x + 2 * y + 2
    return km * num / den


# --------------------------------------------------------------------------- Bruggeman family

def bruggeman_symmetric(phi: ArrayLike, km: float, kf: float) -> np.ndarray:
    """Symmetric Bruggeman (spheres). Built-in percolation threshold at phi = 1/3:
    above it k climbs towards kf, so it overshoots for polymer composites."""
    phi = _a(phi)
    _check_phi(phi)
    b = (3 * phi - 1) * kf + (2 - 3 * phi) * km
    return 0.25 * (b + np.sqrt(b * b + 8 * kf * km))


def bruggeman_dem(phi: ArrayLike, km: float, kf: float, r_k: float = 0.0, radius_m: float | None = None) -> np.ndarray:
    """Asymmetric Bruggeman / differential effective medium (spheres).

    r_k = 0:  (1 - phi) = (kf - k)/(kf - km) * (km/k)^(1/3)
    r_k > 0:  Every et al. (1992) with alpha = r_k km / a:
              (1 - phi)^3 = (km/k)^((1+2a)/(1-a)) * ((k - kf(1-a)) / (km - kf(1-a)))^(3/(1-a))
    Solved numerically for each phi.
    """
    phi = _a(phi)
    _check_phi(phi)
    alpha = 0.0 if r_k == 0 else r_k * km / float(radius_m)  # type: ignore[arg-type]

    def solve(f: float) -> float:
        if f == 0:
            return km
        if alpha == 0:
            if f == 1:
                return kf
            g = lambda k: (kf - k) / (kf - km) * (km / k) ** (1 / 3) - (1 - f)  # noqa: E731
            lo, hi = sorted((km, kf))
            return brentq(g, lo, hi, xtol=1e-14, rtol=1e-12)
        if abs(1 - alpha) < 1e-9:
            raise ValueError("alpha = 1 (r_k km / a) is singular in the Every form")
        kfe = kf * (1 - alpha)
        if f == 1:
            return kfe if alpha < 1 else float("nan")

        def g(k: float) -> float:
            arg = (k - kfe) / (km - kfe)
            if k <= 0 or arg <= 0:
                return float("nan")
            return 3 * math.log(1 - f) - ((1 + 2 * alpha) / (1 - alpha) * math.log(km / k)
                                          + 3 / (1 - alpha) * math.log(arg))

        # g(km) = 3 ln(1 - f) < 0; scan a log grid for the sign change, then refine.
        grid = np.geomspace(km * 1e-6, max(kf, km) * 1.000001, 4000)
        vals = np.array([g(k) for k in grid])
        start = int(np.searchsorted(grid, km))
        for i in list(range(start, len(grid) - 1)) + list(range(start - 1, -1, -1)):
            a, b = vals[i], vals[i + 1]
            if np.isfinite(a) and np.isfinite(b) and a * b <= 0:
                return brentq(g, grid[i], grid[i + 1], xtol=1e-14, rtol=1e-12)
        return float("nan")

    return np.vectorize(solve, otypes=[float])(phi)


# --------------------------------------------------------------------------- semi-empirical

def lewis_nielsen(phi: ArrayLike, km: float, kf: float, A: float, phi_m: float) -> np.ndarray:
    """Lewis-Nielsen (1970): k/km = (1 + A B phi) / (1 - B psi phi),
    B = (kf/km - 1)/(kf/km + A), psi = 1 + phi (1 - phi_m)/phi_m^2.
    A = (generalized Einstein coefficient) - 1 (1.5 for spheres); phi_m = maximum
    packing fraction (0.637 random close-packed spheres, 0.52 3D-random rods).
    Diverges as B psi phi -> 1 (unstable above ~40 vol%)."""
    phi = _a(phi)
    _check_phi(phi)
    r = kf / km
    B = (r - 1) / (r + A)
    psi = 1 + phi * (1 - phi_m) / phi_m ** 2
    den = 1 - B * psi * phi
    with np.errstate(divide="ignore", invalid="ignore"):
        out = km * (1 + A * B * phi) / den
    return np.where(den > 0, out, np.inf)


def agari_uno(phi: ArrayLike, km: float, kf: float, C1: float, C2: float) -> np.ndarray:
    """Agari-Uno (1986): log k = phi C2 log kf + (1 - phi) log(C1 km).
    C1 ~ 1 (effect on matrix), 0 <= C2 <= 1 (ease of forming conductive chains)."""
    phi = _a(phi)
    _check_phi(phi)
    return 10 ** (phi * C2 * np.log10(kf) + (1 - phi) * np.log10(C1 * km))


def geometric_mean(phi: ArrayLike, km: float, kf: float) -> np.ndarray:
    """Lichtenecker: k = kf^phi km^(1 - phi)."""
    phi = _a(phi)
    _check_phi(phi)
    return kf ** phi * km ** (1 - phi)


def foygel(phi: ArrayLike, km: float, K0: float, phi_c: float, beta: float) -> np.ndarray:
    """Foygel et al. (2005) percolation form used for h-BN/epoxy:
    k = km + K0 ((phi - phi_c)/(1 - phi_c))^beta above phi_c, km below."""
    phi = _a(phi)
    _check_phi(phi)
    x = np.clip((phi - phi_c) / (1 - phi_c), 0, None)
    return km + K0 * x ** beta


# --------------------------------------------------------------------------- Nan 1997

def depolarization(p: float) -> tuple[float, float]:
    """Geometric (depolarization) factors (L11 = L22, L33) of a spheroid with
    aspect ratio p = a3/a1. L11 + L22 + L33 = 1."""
    if p <= 0:
        raise ValueError("p must be > 0")
    if abs(p - 1) < 1e-4:
        # second-order expansion about the sphere avoids 0/0 in the closed forms
        e = p - 1
        L33 = 1 / 3 - 4 / 15 * e + 4 / 35 * e * e
        return (1 - L33) / 2, L33
    if p < 1:
        L11 = p * p / (2 * (p * p - 1)) + p * math.acos(p) / (2 * (1 - p * p) ** 1.5)
    else:
        L11 = p * p / (2 * (p * p - 1)) - p * math.acosh(p) / (2 * (p * p - 1) ** 1.5)
    return L11, 1 - 2 * L11


def coated_conductivities(km: float, kp_par: float, kp_perp: float, p: float,
                          r_k: float = 0.0, a1_m: float | None = None) -> tuple[float, float]:
    """Nan's equivalent particle conductivities (K11c, K33c) including the
    interface: Kii_c = kp_ii / (1 + gamma Lii kp_ii / km),
    gamma = (1 + 2p) r_k km / a3 = (2 + 1/p) r_k km / a1.

    This single expression has the right limit for spheres (Hasselman-Johnson),
    thin slabs (K33c -> kp/(1 + r_k kp / a3): series resistance through the
    thickness) and long needles (K11c -> kp/(1 + r_k kp / a1))."""
    L11, L33 = depolarization(p)
    if r_k == 0:
        return kp_par, kp_perp
    if not a1_m:
        raise ValueError("r_k > 0 needs the lateral semi-axis a1_m (= D/2)")
    a3 = p * a1_m
    gamma = (1 + 2 * p) * r_k * km / a3
    return kp_par / (1 + gamma * L11 * kp_par / km), kp_perp / (1 + gamma * L33 * kp_perp / km)


def nan1997(phi: ArrayLike, km: float, kp_par: float, kp_perp: float | None = None, *, p: float = 1.0,
            r_k: float = 0.0, a1_m: float | None = None, cos2: float = 1 / 3, axis: str = "33") -> np.ndarray:
    """Nan, Birringer, Clarke & Gleiter (1997): spheroidal, possibly anisotropic
    particles with interfacial resistance and an orientation distribution.

    kp_par   particle k along its long axes (h-BN basal plane, ~400)
    kp_perp  particle k along its symmetry axis (h-BN c-axis, ~5); default kp_par
    axis     "33" = along the measurement axis x3 (through-plane for a film when
             cos2 refers to the film normal); "11" = transverse to it.
    Limits: p = 1, r_k = 0 -> Maxwell-Garnett; p = 1, r_k > 0 -> Hasselman-Johnson.
    Known flaw (Berne 2015): up to ~100% error for non-spherical particles WITH r_k.
    """
    phi = _a(phi)
    _check_phi(phi)
    if not 0 <= cos2 <= 1:
        raise ValueError("cos2 must be in [0, 1]")
    kperp = kp_par if kp_perp is None else kp_perp
    L11, L33 = depolarization(p)
    K11, K33 = coated_conductivities(km, kp_par, kperp, p, r_k, a1_m)
    b11 = (K11 - km) / (km + L11 * (K11 - km))
    b33 = (K33 - km) / (km + L33 * (K33 - km))
    c = cos2
    if axis == "33":
        num = 1 + phi * (b11 * (1 - L11) * (1 - c) + b33 * (1 - L33) * c)
        den = 1 - phi * (b11 * L11 * (1 - c) + b33 * L33 * c)
    elif axis == "11":
        num = 2 + phi * (b11 * (1 - L11) * (1 + c) + b33 * (1 - L33) * (1 - c))
        den = 2 - phi * (b11 * L11 * (1 + c) + b33 * L33 * (1 - c))
    else:
        raise ValueError("axis must be '33' or '11'")
    return km * num / den
