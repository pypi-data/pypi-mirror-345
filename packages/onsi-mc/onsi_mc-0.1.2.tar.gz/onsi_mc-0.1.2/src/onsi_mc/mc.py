# SPDX-FileCopyrightText: 2025 Ali Onsi
# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2025 Ali Onsi Email: aonsi@alexu.edu.eg
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Callable, Optional, Union, List
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm  # For progress bars

# Conditional Numba import
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# JIT-compiled static method for point generation (Numba version)
if NUMBA_AVAILABLE:
    @jit(nopython=True)
    def _generate_points_numba(lower_limits, upper_limits, n, dim):
        points = np.empty((n, dim))
        for d in range(dim):
            points[:, d] = np.random.uniform(lower_limits[d], upper_limits[d], n)
        return points
else:
    def _generate_points_numba(lower_limits, upper_limits, n, dim):
        return np.column_stack([
            np.random.uniform(low, high, n)
            for low, high in zip(lower_limits, upper_limits)
        ])

class ND:
    def __init__(
        self,
        func: Callable[..., Union[float, np.ndarray]],
        *args: float,
        n: int=50000,
        N: int=1000,
        convergence_threshold: float = 0.5,
        use_numba: bool = True
    ) -> None:
        """
        Initialize the integrator with optional JIT compilation.
        
        Args:
            use_numba: If True, attempts to use Numba for acceleration (if installed).
        """
        self.n = n
        self.N = N
        self.convergence_threshold = convergence_threshold
        self.relative_stds = []
        self.use_numba = use_numba and NUMBA_AVAILABLE

        if use_numba and not NUMBA_AVAILABLE:
            print("Numba not installed. Running without JIT acceleration.")

        # JIT-compile the function if requested and available
        if self.use_numba:
            self.func = jit(nopython=True)(func)
        else:
            self.func = func

        # Validate integration limits
        if len(args) % 2 != 0:
            raise ValueError("Number of limits must be even (a1, b1, a2, b2, ...)")
        self.lower_limits = np.array(args[0::2])
        self.upper_limits = np.array(args[1::2])
        self.dimensions = len(self.lower_limits)

        # Test vectorization support
        self._validate_function()

    def _validate_function(self):
        """Check if the function handles vectorized inputs."""
        test_input = np.column_stack([np.array([1.0, 1.0]) for _ in range(self.dimensions)])
        try:
            self.func(*test_input.T)
        except Exception as e:
            raise ValueError(
                "Function must support vectorized inputs. "
                "Ensure it can handle numpy arrays."
            ) from e

    def _generate_points(self) -> np.ndarray:
        """Generate random points with optional Numba acceleration."""
        if self.use_numba:
            return _generate_points_numba(self.lower_limits, self.upper_limits, self.n, self.dimensions)
        return np.column_stack([
            np.random.uniform(low, high, self.n)
            for low, high in zip(self.lower_limits, self.upper_limits)
        ])

    def run(self, verbose: bool = True, progress_bar: bool = True) -> Optional[float]:
        """Execute integration with optional progress tracking."""
        int_list = []
        self.relative_stds = []
        iterator = tqdm(range(self.N), desc="Integrating") if progress_bar else range(self.N)

        for i in iterator:
            points = self._generate_points()
            values = self.func(*points.T)
            volume = np.prod(self.upper_limits - self.lower_limits)
            int_list.append(np.mean(values) * volume)

            # Check convergence after minimum samples
            min_samples = max(10, int(0.05 * self.N))
            if i >= min_samples:
                mean_val = np.mean(int_list)
                relative_std = np.std(int_list) / (abs(mean_val) if mean_val != 0 else np.inf)
                self.relative_stds.append(relative_std)

        return self._check_convergence(int_list)

    def _check_convergence(self, int_list: List[float]) -> Optional[float]:
        """Validate convergence and return result or None."""
        result = np.mean(int_list)
        if not self.relative_stds:
            print(f"Estimated integral: {result:.8f}")  # 8 decimal places
            return result

        self.min_std = min(self.relative_stds)
        self.max_std = max(self.relative_stds)
        self.std_diff = self.max_std - self.min_std

        if self.std_diff > self.convergence_threshold:
            print(
                f"Warning: Possible non-convergence (Δstd = {self.std_diff:.4f} > "
                f"threshold = {self.convergence_threshold}"
            )
            print(f"Estimated integral: {result:.8f}")  # Still show result with warning
            return None

        print(f"Estimated integral: {result:.8f}")
        return result

    def plot(self, show: bool = True, save: bool = False, filename: str = None):
        """Visualize convergence with matplotlib."""
        if not self.relative_stds:
            raise RuntimeError("Run integration first with .run()")

        plt.figure(figsize=(10, 6))
        min_samples = max(10, int(0.05 * self.N))
        x_vals = range(min_samples, min_samples + len(self.relative_stds))
        plt.plot(x_vals, self.relative_stds, label="Relative Std Dev")
        plt.axhline(
            self.convergence_threshold, 
            color='r', 
            linestyle='--', 
            label="Threshold"
        )
        plt.xlabel("Ensemble Count")
        plt.ylabel("Relative Standard Deviation")
        plt.legend()
        plt.grid(True)

        if save:
            fname = filename or f"mc_convergence_n{self.n}_N{self.N}.png"
            plt.savefig(fname)
        if show:
            plt.show()

    # Aliases for backward compatibility
    integrate = run
    plot_convergence = plot