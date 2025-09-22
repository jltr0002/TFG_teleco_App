"""
Dolph-Chebyshev method for antenna array synthesis.
"""

import numpy as np
import warnings
from typing import List, Dict, Any, Tuple
from scipy.signal import find_peaks

from .synthesis import SynthesisMethod 

class DolphChebyshevMethod(SynthesisMethod):
    """
    Implementation of the Dolph-Chebyshev method for linear array synthesis.

    This method produces an array factor with a specified sidelobe level (SLL)
    where all sidelobes have the same magnitude. It achieves the narrowest possible
    main beam for a given SLL. The synthesis is based on mapping the array factor 
    to a Chebyshev polynomial, as detailed in "ANTENNA ARRAYS: 
    A Computational Approach" by Randy L. Haupt.
    """    

    @property
    def name(self) -> str:
        return "Dolph-Chebyshev"

    @property
    def description(self) -> str:
        return "Synthesizes arrays with uniform, specified sidelobe levels."

    @property
    def layout_type(self) -> str:
        """Dolph-Chebyshev method produces a symetric array"""
        return "symmetric"
        
        
    def _parse_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Parses input parameters from GUI keyword arguments into internal format.
        
        Returns:
            Dictionary containing parsed parameters ready for validation.
        """
        try:
            n_elements = int(kwargs["n_elements"])
            sll_db = float(kwargs["sidelobe_level_db"])
            d_lambda = float(kwargs["d_lambda"])
            theta0_angle = kwargs["theta0_angle"]  # Already parsed by GUI
        except KeyError as e:
            raise ValueError(f"missing_parameter:{e.args[0]}")
        
        # Convert theta0_angle to float if it's a string (backward compatibility)
        if isinstance(theta0_angle, str):
            theta0_angle = float(theta0_angle)

        angle_unit = kwargs.get("angle_unit", "degrees")
        resolution = int(kwargs.get("resolution", 5000))

        if angle_unit == "degrees":
            theta0_rad = np.deg2rad(theta0_angle)
        else:
            theta0_rad = theta0_angle
            
        return {
            "d_lambda": d_lambda,
            "theta0_rad": theta0_rad,
            "n_elements": n_elements,
            "sidelobe_level_db": sll_db,            
            "resolution": resolution,
        }
    
    def _validate_inputs(self, params: Dict[str, Any]) -> None:
        """
        Validates GUI input parameters for correctness and feasibility.
        
        Parameters:
            params: Dictionary of parsed GUI input parameters.
            
        Raises:
            ValueError: If any parameter is invalid.
        """
        n = int(params["n_elements"])
        if n < 2:
            raise ValueError("error_number_of_elements_min_2")

        sll_db = float(params["sidelobe_level_db"])
        if not np.isfinite(sll_db):
            raise ValueError("error_sidelobe_level_must_be_finite")

        if sll_db < 0.0:
            print(f"Negative sidelobe level provided ({sll_db} dB). Using its absolute value as magnitude.")

            # dictionaries are mutable so it would change
            params["sidelobe_level_db"] = abs(sll_db)

        d_lambda = float(params["d_lambda"])
        if not np.isfinite(d_lambda) or d_lambda <= 0.0:
            raise ValueError("error_d_lambda_must_be_positive")

        res = int(params["resolution"])
        if res < 16:
            raise ValueError("error_resolution_must_be_at_least_16")

        theta0_rad = float(params["theta0_rad"])
        if not np.isfinite(theta0_rad) or not (0.0 <= theta0_rad <= np.pi):
            raise ValueError("error_main_beam_angle_out_of_range")
                
        m = n - 1
        r_a = 10.0 ** (abs(float(params["sidelobe_level_db"])) / 20.0)  # voltage ratio > 1
        if m == 0:
            x0 = 1.0
        else:
            # x0 satisfies T_m(x0) = R -> cosh(m*acosh(x0)) = R
            x0 = float(np.cosh((1.0 / m) * np.arccosh(r_a)))
        if not np.isfinite(x0) or x0 <= 1.0:
            raise ValueError(
                "Combination of N and SLL not achievable (x0 <= 1). "
                "Increase n_elements or use a less strict SLL."
            )        
        
        d_max = (1.0 / np.pi) * np.arccos(-1.0 / x0)
        if d_lambda > d_max:
            warnings.warn(
                f"Element spacing d = {d_lambda:.3f} exceeds recommended maximum "
                f"d_max = {d_max:.3f}. The specified sidelobe level (SLL = {sll_db:.1f} dB) "
                f"may not be achievable. Consider reducing element spacing or relaxing the SLL requirement. "
                f"Synthesis will continue but results may not meet specifications.",
                UserWarning,
                stacklevel=2
            )
        
        # Chebyshev parameters
        params["n_zeros"] = m
        params["d_max"] = d_max
        params["r_a"] = r_a
        params["scaling_factor"] = x0

    def _prepare_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional hook to derive intermediate parameters after validation.
        Default implementation returns params unchanged.
        Subclasses can override to compute constants like kd, alpha, grids, etc.
        """
        # Electromagnetic fundamental constants
        k = 2.0 * np.pi  # Wave number: 2π/λ
        kd = k * float(params["d_lambda"])  # Spacing in electrical radians
        alpha_rad = -kd * np.cos(float(params["theta0_rad"]))

        # Angular grid and psi grid
        theta_rad = np.linspace(0.0, np.pi, int(params["resolution"]))
        psi_rad = kd*np.cos(theta_rad)

        psi_min_rad, psi_max_rad = self._compute_visible_margin(params["d_lambda"], alpha_rad) 

        # d_opt in terms of lambda (valid only for broadside arrays, theta0 = 90°)
        # This optimal spacing leads to the smallest possible HPBW for the given sidelobe level
        # Note: For steered arrays (theta0 ≠ 90°), this value is only approximate
        n = params["n_elements"]
        r_a = params["r_a"]

        sqrt_term = np.sqrt(r_a**2 - 1.0)
        log_arg = r_a + sqrt_term

        ln_term = np.log(log_arg)
        cosh_arg = (1.0 / (n - 1)) * ln_term

        # Calculate γ = cosh[(1/(N-1)) * ln(R + √(R² - 1))]
        gamma = np.cosh(cosh_arg)

        arg_arccos = 1.0 / gamma
        arccos_term = np.arccos(arg_arccos)
        d_opt = abs(1.0 - arccos_term / np.pi)
        
        prepared_params =  dict(params)     
        prepared_params.update({
            "k": k,
            "kd": kd,
            "alpha_rad": alpha_rad,
            "theta_rad": theta_rad,
            "d_opt": d_opt,
            "psi_rad": psi_rad,
            "psi_min_rad": psi_min_rad,
            "psi_max_rad": psi_max_rad
        })

        return prepared_params
    
    def _compute_excitations(self, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the complex excitation coefficients for the antenna elements.
        
        Parameters:
            params: Dictionary of validated input parameters.
            
        Returns:
            Array of complex excitation coefficients.
        """
        x0 = params["scaling_factor"]
        d_lambda = params["d_lambda"]
        theta0_rad = params["theta0_rad"]
        
        m = params["n_zeros"]
        i = np.arange(1, m+1)
        x_nulls = np.cos(np.pi * (i - 0.5) / m)

        psi_nulls = 2 * np.arccos(x_nulls / x0)
        
        z_nulls = np.exp(1j * psi_nulls)

        coeff = np.real(np.poly(z_nulls))
        steered_coeff = self.steer(coeff, d_lambda, theta0_rad)

        return steered_coeff
    
    def _compute_af(self, excitations: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the RAW, complex array factor.
        This method should NOT normalize or convert to dB.
        """
        # Phase variable psi over theta grid
        psi_rad = params["psi_rad"]

        N = len(excitations)
        n_indices = np.arange(N) - (N - 1) / 2.0
        # Vectorized calculation of the Array Factor
        phase_matrix = np.exp(1j * np.outer(n_indices, psi_rad))
        af = np.sum(excitations[:, np.newaxis] * phase_matrix, axis=0)

        return af
        
    def _format_output(self, results: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats the final output results for the GUI and user consumption.
        
        Parameters:
            results: Dictionary of processed intermediate results.
            params: Dictionary of input parameters.
            
        Returns:
            Dictionary of formatted final results.
        """
        theta_rad = params["theta_rad"]
        theta_deg = np.rad2deg(theta_rad)

        # invisible_nulls = params["invisible_nulls"]

        psi_min_rad = params["psi_min_rad"]
        psi_max_rad = params["psi_max_rad"]

        # Visible margin formatted in radians
        visible_margin_rad_str = self._format_visible_margin_radians(psi_min_rad, psi_max_rad)
        visible_margin_deg_str = self._format_visible_margin_degrees(np.rad2deg(psi_min_rad), np.rad2deg(psi_max_rad))

        excitations = results["excitations"]
        af = results["raw_af"]
        
        normalized_excitations = self._normalize_excitations(excitations, "center")
        polynomial_str = self._format_polynomial_string(normalized_excitations)

        max_af = np.max(np.abs(af))
        normalized_af = af / max_af if max_af > 0 else af
        normalized_af = self._zero_small_parts(normalized_af)
        af_db = 20 * np.log10(np.abs(normalized_af) + self.EPSILON)

        directivity_linear, directivity_db = self._calculate_directivity_from_af(af = normalized_af, theta_rad = theta_rad)

        theta0_rad = params['theta0_rad']
        achieved_sll_db = self._find_achieved_sll(af_db, theta_rad, theta0_rad)

        return {
            # excitations
            'dolph_chebyshev_polynomial_str': polynomial_str,
            'element_excitations': normalized_excitations, # For display
            'raw_excitations': excitations, # For potential further use

            # af representation
            'af': af,
            'normalized_af': normalized_af,
            'af_db': af_db,
            'theta_degrees': theta_deg,
            'theta_radians': theta_rad,

            # method related outputs
            'achieved_sll_db': achieved_sll_db,
            'd_opt': params['d_opt'],
            'd_max': params['d_max'],
            'x0_scaling_factor': params['scaling_factor'],

            # Visible margin
            'visible_margin_radians_str': visible_margin_rad_str,
            'visible_margin_degrees_str': visible_margin_deg_str,

            # Directivity
            'directivity_linear': directivity_linear,
            'directivity_db': directivity_db,

            # geometry plot 
            'd_lambda': params['d_lambda'],
            'layout_type': self.layout_type,
            'theta0_rad': params['theta0_rad']
        }

    def get_inputs(self, angle_unit: str = "degrees") -> List[Dict[str, Any]]:
        """Returns a list of dictionaries defining the required input parameters."""
        return [            
            {
                'name': 'd_lambda',
                'label_key': 'element_spacing',
                'type': 'float',
                'default': 0.5,
                'min': 0.001,
                'max': 2.00,
                'step': 0.001,
                'decimals': 3,
                'help_key': 'help_element_spacing'
            },
            {
                'name': 'theta0_angle',
                'label_key': 'main_beam_angle',
                'type': 'text', 
                'default': 'pi/2' if angle_unit == "radians" else '90.0',
                'min': 0.0 if angle_unit == "degrees" else 0.0,
                'max': 180.0 if angle_unit == "degrees" else 'pi',
                'help_key': 'help_main_beam_angle'
            },
            {
                'name': 'n_elements',
                'label_key': 'number_of_elements',
                'type': 'int',
                # 'default': 10,
                'min': 2,
                'max': 100,
                'step': 1,
                'help_key': 'help_n_elements_chebyshev'
            },
            {
                'name': 'sidelobe_level_db',
                'label_key': 'sidelobe_level_db',
                'type': 'float',
                # 'default': 30.0,
                'min': 10.0,
                'max': 100.0,
                'step': 1.0,
                'decimals': 1,
                'help_key': 'help_sll_db'
            }
        ]
    
    def get_outputs(self) -> List[Dict[str, Any]]:
        """Return output parameter definitions for GUI."""
        return [
            {'key': 'dolph_chebyshev_polynomial_str', 'help_key': 'help_dolph_chebyshev_polynomial_str'},
            {'key': 'achieved_sll_db', 'help_key': 'help_achieved_sll_db'},
            {'key': 'directivity_linear', 'help_key': 'help_directivity_linear'},
            {'key': 'directivity_db', 'help_key': 'help_directivity_db'},
            {'key': 'd_opt', 'help_key': 'help_d_opt'},
            {'key': 'x0_scaling_factor', 'help_key': 'help_x0_scaling_factor'},
        ]

    def _find_achieved_sll(self, af_db: np.ndarray, theta_rad: np.ndarray, main_lobe_angle_rad: float, decimals: int = 0) -> float:
        """
        Finds the highest sidelobe level from the calculated array factor.
        
        Args:
            af_db: Array factor in dB
            theta_rad: Angle array in radians
            main_lobe_angle_rad: Main lobe steering angle in radians
            decimals: Number of decimal places to round to
            
        Returns:
            Highest sidelobe level in dB (absolute value, rounded)
        """
        # Find all peaks in the pattern
        peaks_indices, _ = find_peaks(af_db)
        if len(peaks_indices) == 0:
            return -np.inf # No sidelobes found

        # Identify the main lobe index by finding the peak closest to the expected angle
        peak_angles_rad = theta_rad[peaks_indices]
        main_lobe_idx_in_peaks = np.argmin(np.abs(peak_angles_rad - main_lobe_angle_rad))
            
        # Get all sidelobe levels by excluding the main lobe
        sidelobe_levels = np.delete(af_db[peaks_indices], main_lobe_idx_in_peaks)
        if sidelobe_levels.size == 0:
            return -np.inf # No sidelobes found
        
        sll_achieved = abs(float(np.max(sidelobe_levels)))
        sll_achieved = round(sll_achieved, decimals)
        return sll_achieved