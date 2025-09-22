import numpy as np
from numpy.typing import NDArray, ArrayLike
from typing import List, Dict, Tuple, Any, cast, final
from abc import ABC, abstractmethod

class SynthesisMethod(ABC):
    """
    Abstract Base Class for all antenna array synthesis methods.
    
    This class defines the common interface (contract) that all synthesis
    methods must implement. It also provides common utility functions.
    """
    # Threshold for setting small numerical values to zero
    NUMERICAL_ZERO_THRESHOLD = 1e-10

    # Threshold for division and logarithmic operations
    EPSILON = 1e-12 
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the synthesis method."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of the synthesis method."""
        pass

    @property
    @abstractmethod
    def layout_type(self) -> str:
        """
        Defines the layout type for visualization ('unilateral' or 'symmetric').
        """
        pass    
    
    @final
    def compute(self, **kwargs) -> Dict[str, Any]:
        """
        The main computation method (Template Method).
        Orchestrates the synthesis process. DO NOT override in subclasses.
        """
        parsed_params = self._parse_inputs(**kwargs)

        self._validate_inputs(params = parsed_params)

        prepared_params = self._prepare_params(params=parsed_params)

        raw_excitations = self._compute_excitations(params = prepared_params)
        excitations = self._zero_small_parts(data = raw_excitations)

        raw_af = self._compute_af(excitations=excitations, params = prepared_params)
        raw_af = self._zero_small_parts(raw_af)

        intermediate_results = {
            'excitations': excitations,
            'raw_af': raw_af
        }

        processed_results = self._post_process_hook(intermediate_results = intermediate_results, params=prepared_params)

        final_results = self._format_output(results=processed_results, params=prepared_params)       
        
        return final_results   

    @abstractmethod
    def _parse_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Parses input parameters from GUI keyword arguments into internal format.
        
        Returns:
            Dictionary containing parsed parameters ready for validation.
        """
        pass

    @abstractmethod
    def _validate_inputs(self, params: Dict[str, Any]) -> None:
        """
        Validates GUI input parameters for correctness and feasibility.
        
        Parameters:
            params: Dictionary of parsed GUI input parameters.
            
        Raises:
            ValueError: If any parameter is invalid.
        """
        pass

    def _prepare_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional hook to derive intermediate parameters after validation.
        Default implementation returns params unchanged.
        Subclasses can override to compute constants like kd, alpha, grids, etc.
        """
        return params

    @abstractmethod
    def _compute_excitations(self, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the complex excitation coefficients for the antenna elements.
        
        Parameters:
            params: Dictionary of validated input parameters.
            
        Returns:
            Array of complex excitation coefficients.
        """
        pass

    @abstractmethod
    def _compute_af(self, excitations: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the RAW, complex array factor.
        This method should NOT normalize or convert to dB.
        """
        pass

    def _post_process_hook(self, intermediate_results: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional hook for post-processing intermediate results.
        
        Subclasses can override this method to add additional processing steps.
        By default, it returns the results unchanged.
        
        Parameters:
            intermediate_results: Dictionary containing excitations and raw array factor.
            params: Dictionary of input parameters.
            
        Returns:
            Processed intermediate results dictionary.
        """
        return intermediate_results

    @abstractmethod
    def _format_output(self, results: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats the final output results for the GUI and user consumption.
        
        Parameters:
            results: Dictionary of processed intermediate results.
            params: Dictionary of input parameters.
            
        Returns:
            Dictionary of formatted final results.
        """
        pass

    @abstractmethod
    def get_inputs(self, angle_unit: str = "degrees") -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries defining the required input parameters
        for the GUI. Uses 'label_key' and 'help_key' for translation.
        
        Args:
            angle_unit: The current angle unit setting ("degrees" or "radians")
                       to adjust min/max/default values appropriately.
        """
        pass

    @abstractmethod
    def get_outputs(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries defining output parameters for GUI display.
        Each dictionary should contain:
        - 'key': The key to retrieve the value from results
        - 'help_key': Optional key for help text translation
        """
        pass
    
    @staticmethod
    def steer(excitations: np.ndarray, d_lambda: float, theta0_rad: float) -> np.ndarray:
        """
        Steers the antenna array beam to a specified angle.
        
        Converts the steering angle to a progressive phase shift and applies
        it to the excitation coefficients.
        
        Parameters:
            excitations: Array weights to be steered.
            d_lambda: Element spacing (length in wavelengths, λ)
            theta0_rad: Steering angle in radians (broadside = pi/2 rad).
            
        Returns:
            Steered excitation coefficients.
        """        
        kd = 2 * np.pi * d_lambda
        alpha_rad = -kd * np.cos(theta0_rad)  # Scanning phase in psi-space

        return SynthesisMethod.scan(excitations, alpha_rad)

    @staticmethod
    def scan(excitations: np.ndarray, alpha_rad: float) -> np.ndarray:
        """
        Applies progressive phase shift across array elements.
        
        The phase shift is applied with elements indexed around the center,
        creating a linear phase progression for beam steering.
        
        Parameters:
            excitations: Array weights to be phase-shifted.
            alpha_rad: Progressive phase shift in radians.
            
        Returns:
            Phase-shifted excitation coefficients.
        """
        M = len(excitations)
        # Element indices in range [-(M-1)/2, (M-1)/2]
        n = np.arange(M) - (M - 1) / 2
        excitations = excitations * np.exp(1j * n * alpha_rad)

        return excitations 

    @staticmethod
    def _compute_visible_margin(d_lambda:float, alpha_rad: float) -> Tuple[float, float]:
        """
        Computes the visible margin [psi_min, psi_max] for a linear antenna array.
        
        The visible margin is the range of the phase variable (psi) that
        corresponds to the full range of real-world angles (theta from 0 to 180 degrees,
        or equivalently, cos(theta) from -1 to 1).

        The relationship is defined by the formula:
        psi = k*d*cos(theta) + alpha
        
        Therefore, the margin is given by the interval [alpha - k*d, alpha + k*d].

        Parameters:
        -----------
        d_lambda (float): Element spacing (length in wavelengths, λ)
        alpha_rad (float): The progressive phase shift between elements, in radians.

        Returns:
        --------
        Tuple[float, float]
            Tuple[float, float]: A tuple containing the lower and upper bounds
                                 of the visible margin (psi_min, psi_max).       
        """
        kd = 2 * np.pi * d_lambda
        psi_min_rad = alpha_rad - kd
        psi_max_rad = alpha_rad + kd

        return psi_min_rad , psi_max_rad 

    @staticmethod
    def _format_visible_margin_radians(psi_min_rad: float, psi_max_rad: float) -> str:
        """
        Formats the visible margin range in radians as a readable string.
        
        The visible margin represents the range of the phase variable (psi) that
        corresponds to the full range of real-world angles (theta from 0 to 180 degrees).
        
        Parameters:
        -----------
        psi_min_rad : float
            The minimum value of the visible margin in radians.
        psi_max_rad : float
            The maximum value of the visible margin in radians.
            
        Returns:
        --------
        str
            A formatted string in the format "[min rad, max rad]" with 2 decimal places.
        """
        return f"[{psi_min_rad:.2f} rad, {psi_max_rad:.2f} rad]"

    @staticmethod
    def _format_visible_margin_degrees(psi_min_deg: float, psi_max_deg: float) -> str:
        """
        Formats the visible margin range in degrees as a readable string.
        
        The visible margin represents the range of the phase variable (psi) that
        corresponds to the full range of real-world angles (theta from 0 to 180 degrees).
        This method formats the range when expressed in degrees.
        
        Parameters:
        -----------
        psi_min_deg : float
            The minimum value of the visible margin in degrees.
        psi_max_deg : float
            The maximum value of the visible margin in degrees.
            
        Returns:
        --------
        str
            A formatted string in the format "[min°, max°]" with 2 decimal places.
        """
        return f"[{psi_min_deg:.2f}°, {psi_max_deg:.2f}°]"  
    
    @staticmethod
    def _calculate_directivity_from_af(af: np.ndarray, theta_rad: np.ndarray) -> Tuple[float, float]:
        """
        Calculates directivity from a given array factor.
        This method assumes isotropic array elements.
        It is bases on: 
        .. math::
            D = \\frac{4\\pi |AF_{max}|^2}{\\int_{0}^{2\\pi} \\int_{0}^{\\pi} |AF(\\theta, \\phi)|^2 \\sin(\\theta) d\\theta d\\phi}
              = \\frac{2 |AF_{max}|^2}{\\int_{0}^{\\pi} |AF(\\theta)|^2 \\sin(\\theta) d\\theta}

        Parameters:
        -----------
        af : np.ndarray
            The (normalized or unnormalized) array factor.
        theta_rad : np.ndarray
            The angles in radians over which the AF is defined (0, \\pi).

        Returns:
        --------
        Tuple[float, float]
            A tuple containing (directivity_linear, directivity_db).
        """
        epsilon = float(SynthesisMethod.EPSILON)

        # |AF|^2 and integral over theta with sin(theta)
        af_squared_abs = np.abs(af)**2
        integrand = af_squared_abs * np.sin(theta_rad)
        integral = np.trapezoid(integrand, theta_rad)        
       
        # Isotropic element pattern over phi
        p_rad = integral * 2.0 * np.pi

        # Adding robustness
        p_rad = float(np.fmax(p_rad, epsilon))
        
        # Peak radiation intensity
        u_max = np.max(af_squared_abs)
        
        # D = 4 np.pi * U_max / P_rad
        directivity_linear = float(4 * np.pi * u_max / p_rad)
        directivity_db =  float(10.0 * np.log10(np.fmax(directivity_linear, epsilon)))
        
        return directivity_linear, directivity_db
    
    @staticmethod
    def _zero_small_parts(data: ArrayLike, tol: float | None = None) -> Any:
        """
        Set to zero real/imag parts whose absolute value is below the threshold.
        Works on a copy and preserves dtype and scalar-ness.
        """
        # Pick threshold: explicit value wins, otherwise use the class constant
        threshold = float(SynthesisMethod.NUMERICAL_ZERO_THRESHOLD) if tol is None else float(tol)

        arr = np.array(data, copy=True)

        if np.iscomplexobj(arr):
            carr = cast(NDArray[np.complexfloating[Any, Any]], arr)

            # Boolean masks for small components
            real_mask = np.abs(carr.real) < threshold
            imag_mask = np.abs(carr.imag) < threshold

            # Write into the complex view to preserve dtype and shape
            carr.real[real_mask] = 0.0
            carr.imag[imag_mask] = 0.0

            out: NDArray[np.complexfloating[Any, Any]] = carr
        else:
            # Real or integer input
            arr[np.abs(arr) < threshold] = 0
            out = arr

        # Preserve scalar output type
        if isinstance(data, np.generic):
            return data.dtype.type(out.item())  # keep NumPy scalar dtype
        if np.isscalar(data):
            return out.item()  # Python scalar
        
        return out
    
    @staticmethod
    def _normalize_excitations(excitations: np.ndarray, method: str = 'first') -> np.ndarray:
        """
        Normalizes an array of excitation coefficients using a specified method.

        Parameters:
            excitations: The array of complex excitation coefficients.
            method: The normalization method.
                'first': Normalizes by the first element (a_0 = 1).
                        Ideal for unilateral arrays (e.g., Schelkunoff).
                'center': Normalizes by the central element.
                        Ideal for symmetric arrays (e.g., Taylor, Chebyshev).
                'max': Normalizes by the element with the largest magnitude.
                    A general-purpose choice.

        Returns:
            A new array with the normalized excitations.
        """
        if excitations.size == 0:
            return excitations.copy()

        coeffs = np.array(excitations, dtype=np.complex128)
        
        scaling_factor = 1.0
        if method == 'first':
            scaling_factor = coeffs[0]
        elif method == 'center':
            center_index = (coeffs.size - 1) // 2
            scaling_factor = coeffs[center_index]
        elif method == 'max':
            scaling_factor = coeffs[np.argmax(np.abs(coeffs))]
        else:
            raise ValueError(f"error_unknown_normalization_method:{method}")

        if np.isclose(scaling_factor, 0):
            # Avoid division by zero, return a copy of the original
            return coeffs
        
        normalized_coeffs = coeffs/scaling_factor
        normalized_coeffs = SynthesisMethod._zero_small_parts(normalized_coeffs)

        return normalized_coeffs 
    
    @staticmethod
    def _format_polynomial_string(coeffs: np.ndarray, decimals: int = 2) -> str:
        """
        Builds a readable polynomial string from pre-normalized complex coefficients.
        
        Assumes the input coefficients are ready for display (e.g., normalized).
        Coefficient is normalized with a_0 = 1.
        
        Formatting rules:
        - Skips terms with magnitude below a display threshold
        - Formats complex numbers intelligently based on the specified number of decimals
        - For purely real coefficients equal to ±1 (for n > 0), omits the number
        - Does not print a leading '+' sign
        - Uses '·' for multiplication and '^' for powers
        
        Parameters:
            coeffs: Array of complex coefficients.
            decimals: Number of decimal places for formatting.
            
        Returns:
            Formatted polynomial string.
        """
        if coeffs.size == 0:
            return "0"
        
        poly_parts = []
        decimal_threshold = 10**(-decimals)

        # Iterate directly over the input coefficients
        for i, c in enumerate(coeffs):
            # Skip terms that are numerically insignificant
            # Using class constant for display threshold
            if np.abs(c) < SynthesisMethod.NUMERICAL_ZERO_THRESHOLD:  # Threshold to avoid displaying very small terms
                continue

            # --- Coefficient Formatting Logic (exactly as before) ---
            c_real = c.real
            c_imag = c.imag
            
            show_real = np.abs(c_real) >= decimal_threshold
            show_imag = np.abs(c_imag) >= decimal_threshold

            if not show_real and not show_imag:
                if i == 0 and np.isclose(c_real, 1.0):
                    coeff_str = f"1.0"
                else:
                    continue
            elif show_real and not show_imag:
                coeff_str = f"{c_real:.{decimals}f}"
            elif not show_real and show_imag:
                coeff_str = f"{c_imag:+.{decimals}f}j".replace("+-", "-")
            else:
                coeff_str = f"({c_real:.{decimals}f}{c_imag:+.{decimals}f}j)".replace("+-", "-")
            
            # --- Sign Logic (exactly as before) ---
            first_visible_part = c_real if show_real else c_imag
            sign = " - " if first_visible_part < 0 else " + "
            
            if not poly_parts:  # If this is the first term to be added
                sign = "-" if first_visible_part < 0 else ""
            
            coeff_str = coeff_str.lstrip('+-')

            # --- Special rules for coefficients ±1 (exactly as before) ---
            if i > 0 and np.isclose(np.abs(c), 1.0) and np.isclose(c.imag, 0):
                coeff_str = ""
            
            # --- Variable Logic (exactly as before) ---
            if i == 0:
                var_part = ""
            elif i == 1:
                var_part = "z"
            else:
                var_part = f"z^{i}"

            # --- Term Assembly (exactly as before) ---
            if coeff_str and var_part:
                term = f"{coeff_str}·{var_part}"
            else:
                term = f"{coeff_str}{var_part}"
                
            if i == 0 and not term:
                term = "1.0"

            poly_parts.append(f"{sign}{term}")

        final_str = "".join(poly_parts).strip()
        
        if not final_str:
            return "0.0"

        # Small improvement for the case where the first term is '1.0'
        # and there are no more terms. Looks better than "1.0".
        if final_str == "1.0" and len(coeffs) > 1:
            pass # Keep it as 1.0 if it's part of a larger polynomial
        elif final_str == "1.0":
            return "1"

        return final_str
    
    @staticmethod
    def _calculate_hpbw(af_db: np.ndarray, theta_deg: np.ndarray) -> float:
        """
        Calculates the Half-Power Beamwidth (HPBW) in degrees.

        Args:
            af_db: Array factor in dB, normalized to 0 dB at the peak.
            theta_deg: The angles in degrees corresponding to the af_db values.

        Returns:
            The HPBW in degrees, or np.nan if it cannot be determined.
        """
        # The main lobe peak is at 0 dB
        peak_level_db = 0
        half_power_level_db = peak_level_db - 3.0

        # Find the indices where the pattern crosses -3 dB
        # np.diff finds the sign change, and np.where locates it
        indices_3db = np.where(np.diff(np.sign(af_db - half_power_level_db)))[0]

        if len(indices_3db) < 2:
            return np.nan  # No se pudo encontrar el ancho de haz

        # Localizar el pico principal
        main_lobe_idx = np.argmax(af_db)
        
        # Find the closest -3 dB crossing on each side of the peak
        left_indices = indices_3db[indices_3db < main_lobe_idx]
        right_indices = indices_3db[indices_3db > main_lobe_idx]

        if not left_indices.size or not right_indices.size:
            return np.nan # Main lobe at edge, cannot calculate

        # Use the closest one to the peak on each side
        left_idx = left_indices[-1]
        right_idx = right_indices[0]

        # Can interpolate for higher precision, but this is a good approximation
        hpbw_deg = float(abs(theta_deg[right_idx] - theta_deg[left_idx]))
        
        return hpbw_deg