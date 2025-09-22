"""
Schelkunoff method for antenna array synthesis.
"""

import numpy as np
from typing import List, Dict, Any
from scipy.signal import find_peaks
from .synthesis import SynthesisMethod

class SchelkunoffMethod(SynthesisMethod):
    """
    Implementation of the Schelkunoff polynomial method for antenna array synthesis.
    
    This method synthesizes an array by placing nulls at specified angular positions.
    It determines the array factor polynomial's roots and derives the element 
    excitations from its coefficients.
    """    
    DISPLAY_ZERO_THRESHOLD = 1e-4
    DEFAULT_NULL_DEPTH_DB = -40
    
    
    @property
    def name(self) -> str:
        return "Schelkunoff"
    
    @property
    def description(self) -> str:
        return "Polynomial method for null placement synthesis"
    
    @property
    def layout_type(self) -> str:
        """Schelkunoff method produces a unilateral array starting from element 0."""
        return "unilateral"
    
    def _parse_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Parses input parameters from GUI keyword arguments into internal format.
        
        Returns:
            Dictionary containing parsed parameters ready for validation.
        """
        try:
            d_lambda = float(kwargs['d_lambda'])
            null_angles_input = kwargs['null_angles']
            theta0_angle = kwargs['theta0_angle']  # Already parsed by GUI
        except KeyError as e:
            raise ValueError(f"missing_parameter:{e.args[0]}")
        
        # Convert theta0_angle to float if it's a string (backward compatibility)
        if isinstance(theta0_angle, str):
            theta0_angle = float(theta0_angle)

        angle_unit = kwargs.get('angle_unit', 'degrees')
        resolution = int(kwargs.get('resolution', 5000))

        if isinstance(null_angles_input, str):
            if null_angles_input.strip() == "":
                null_angles = []
            else:
                try:
                    null_angles = [float(s.strip()) for s in null_angles_input.split(',')]
                except ValueError:
                    raise ValueError("error_could_not_parse_null_angles")
        else:
            null_angles = list(null_angles_input)

        if angle_unit == "degrees":
            null_angles_rad = np.deg2rad(null_angles)
            theta0_rad = np.deg2rad(theta0_angle)
        else:
            null_angles_rad = np.array(null_angles)
            theta0_rad = theta0_angle     

        return {
            "d_lambda": d_lambda,
            "theta0_rad": theta0_rad,
            "null_angles_rad": null_angles_rad,
            "original_null_angles": null_angles,
            "resolution": resolution
        }
    
    def _validate_inputs(self, params: Dict[str, Any]) -> None:
        """
        Validates GUI input parameters for correctness and feasibility.
        
        Parameters:
            params: Dictionary of parsed GUI input parameters.
            
        Raises:
            ValueError: If any parameter is invalid.
        """
        nulls = np.asarray(params["null_angles_rad"], dtype=float)

        if not nulls.size:
            raise ValueError("error_null_positions_cannot_be_empty")    
        
        d_lambda = float(params["d_lambda"])
        if not np.isfinite(d_lambda) or d_lambda <= 0.0:
            raise ValueError("error_d_lambda_must_be_positive")
        
        resolution = int(params["resolution"])
        if resolution < 16:
            raise ValueError("error_resolution_must_be_at_least_16")
        
        # Validate main beam angle
        theta0_rad = float(params["theta0_rad"])
        if not np.isfinite(theta0_rad) or not (0.0 <= theta0_rad <= np.pi):
            raise ValueError("error_main_beam_angle_out_of_range")
        
        # Warn if a null coincides with main beam angle
        angle_atol = 1e-8
        for nrad in nulls:
            if np.isclose(nrad, theta0_rad, atol=angle_atol):
                print(f"Warning: null at main beam direction {np.rad2deg(nrad):.3f} deg.")

    def _prepare_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derive intermediate constants after inputs are validated.
        
        Computes k, kd, alpha, theta grid, visibility bounds and invisibility list.
        
        Parameters:
            params: Dictionary of validated input parameters.
            
        Returns:
            Dictionary of prepared parameters with computed constants.
        """
        # Derive fundamental constants
        k = 2.0 * np.pi  # Wave number: 2π/λ
        kd = k * float(params["d_lambda"])  # Spacing in electrical radians
        alpha_rad = -kd * np.cos(float(params["theta0_rad"]))

        # Angular grid and psi grid
        theta_rad = np.linspace(0.0, np.pi, int(params["resolution"]))
        psi_rad = kd*np.cos(theta_rad) + alpha_rad

        psi_min_rad, psi_max_rad = self._compute_visible_margin(params["d_lambda"], alpha_rad)
        # print(f"Psi_min {psi_min_rad:.3f} rad, psi_max {psi_max_rad:.3f}, theta0_rad {float(params["theta0_rad"]):.3f}, alpha_rad {alpha_rad:.3f}")

        # Visibility check using normalized variable t = (psi - alpha) / kd in [-1, 1]
        nulls = np.asarray(params["null_angles_rad"], dtype=float)
        psi_nulls = kd * np.cos(nulls) + alpha_rad
        t = (psi_nulls - alpha_rad) / kd

        tol = max(100.0 * float(self.EPSILON), 1e-12)
        visible_mask = np.isfinite(t) & (t >= -1.0 - tol) & (t <= 1.0 + tol)
        invisible_idx = np.where(~visible_mask)[0].tolist()
        invisible_nulls = [params["original_null_angles"][i] for i in invisible_idx]
        if invisible_nulls:
            print(f"Warning: nulls in invisible region: {invisible_nulls}")

        prepared_params =  dict(params)     
        prepared_params.update({
            "k": k,
            "kd": kd,
            "alpha_rad": alpha_rad,
            "theta_rad": theta_rad,
            "psi_rad": psi_rad,
            "psi_min_rad": psi_min_rad,
            "psi_max_rad": psi_max_rad,
            "invisible_nulls": invisible_nulls
        })

        return prepared_params

    def _compute_excitations(self, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the complex excitation coefficients for the antenna elements.

        Note: The null positions are interpreted in the steered coordinate system.
        This means a null at angle θ will appear at that angle in the final 
        steered pattern, not in the broadside pattern.
        
        Parameters:
            params: Dictionary of validated input parameters.
            
        Returns:
            Array of complex excitation coefficients.
        """
        nulls_rad = params["null_angles_rad"]
        kd = params["kd"]
        alpha_rad = params["alpha_rad"]        
        
        psi_nulls_rad = kd * np.cos(nulls_rad)  + alpha_rad
        z_nulls = np.exp(1j * psi_nulls_rad)

        # np.poly constructs a polynomial from roots. Coefficients are the excitations.
        # [::-1] reverses the order to match the standard notation (a0, a1*z, a2*z^2, ...).
        coeff = np.poly(z_nulls)
        coeff_reversed = coeff[::-1]
        # steered_coeff = self.scan(coeff_reversed, alpha_rad)

        # def print_complex_mag_phase(arr, name):
        #     print(f"{name}:")
        #     for i, c in enumerate(arr):
        #         mag = np.abs(c)
        #         phase_rad = np.angle(c)
        #         phase_deg = np.rad2deg(phase_rad)
        #         print(f"  [{i}]: |{mag:.4f}| ∠{phase_deg:.2f}° ({phase_rad:.4f} rad)")
        #     print()

        # print_complex_mag_phase(coeff, "Original coefficients")
        # print_complex_mag_phase(coeff_reversed, "Reversed coefficients")
        # # print_complex_mag_phase(steered_coeff, "Steered coefficients")
                
        return coeff_reversed

    def _compute_af(self, excitations: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the RAW, complex array factor.
        This method should NOT normalize or convert to dB.
        """
        # Phase variable psi over theta grid
        psi_rad = params["psi_rad"]

        # Vandermonde-like phase matrix for unilateral array starting at index 0   
        n_elements = len(excitations)
        element_indices = np.arange(n_elements)
        
        phase_matrix = np.exp(1j * np.outer(element_indices, psi_rad))

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

        invisible_nulls = params["invisible_nulls"]

        psi_min_rad = params["psi_min_rad"]
        psi_max_rad = params["psi_max_rad"]

        # Visible margin
        visible_margin_rad_str = self._format_visible_margin_radians(psi_min_rad, psi_max_rad)
        visible_margin_deg_str = self._format_visible_margin_degrees(np.rad2deg(psi_min_rad), np.rad2deg(psi_max_rad))

        excitations = results["excitations"]
        af = results["raw_af"]

        n_elements = len(excitations)
        
        # normalized_excitations = self._normalize_excitations(excitations, "first")
        normalized_excitations = excitations
        polynomial_str = self._format_polynomial_string(normalized_excitations)

        max_af = np.max(np.abs(af))
        normalized_af = af / max_af if max_af > 0 else af
        normalized_af = self._zero_small_parts(normalized_af)
        af_db = 20 * np.log10(np.abs(normalized_af) + self.EPSILON)

        achieved_nulls_rad = self._find_achieved_nulls(af_db=af_db, theta_rad = theta_rad)
        achieved_nulls_deg = np.rad2deg(achieved_nulls_rad)

        directivity_linear, directivity_db = self._calculate_directivity_from_af(af = normalized_af, theta_rad = theta_rad)

        return {
            # excitations
            'schelkunoff_polynomial_str': polynomial_str,
            'element_excitations': normalized_excitations, # For display
            'raw_excitations': excitations, # For potential further use
            'n_elements': n_elements,

            # af representation
            'af': af,
            'normalized_af': normalized_af,
            'af_db': af_db,
            'theta_degrees': theta_deg,
            'theta_radians': theta_rad,

            # method related outputs
            'achieved_nulls_degrees': achieved_nulls_deg,
            'achieved_nulls_radians': achieved_nulls_rad,

            # Visible margin
            'visible_margin_radians_str': visible_margin_rad_str,
            'visible_margin_degrees_str': visible_margin_deg_str,            
            'invisible_nulls': invisible_nulls,

            # Directivity
            'directivity_linear': directivity_linear,
            'directivity_db': directivity_db,

            # geometry plot 
            'd_lambda': params['d_lambda'],
            'layout_type': self.layout_type,
            'theta0_rad': params['theta0_rad']
        }
    
    def get_inputs(self, angle_unit: str = "degrees") -> List[Dict[str, Any]]:
        """Return input parameter definitions for GUI."""        
        return [
            {
                'name': 'd_lambda',
                'label_key': 'element_spacing', # Element spacing (length in wavelengths, λ)
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
                'name': 'null_angles',
                'label_key': 'null_positions',
                'type': 'list_float',
                #'default': [0, 90, 180],
                #'default': [0.9273, 1.3694, 1.7722, 2.2143, 3.1416],
                #'default': [0, 53.1301, 60.00, 78.4630, 101.5370, 120, 126.8699, 180],
                'help_key': 'help_null_positions'
            }
        ]
    
    def get_outputs(self) -> List[Dict[str, Any]]:
        """Return output parameter definitions for GUI."""
        return [
            {'key': 'schelkunoff_polynomial_str', 'help_key': 'help_schelkunoff_polynomial_str'},
            {'key': 'n_elements', 'help_key': 'help_n_elements_output'},
            {'key': 'achieved_nulls_degrees', 'help_key': 'help_achieved_nulls_degrees'},
            {'key': 'achieved_nulls_radians', 'help_key': 'help_achieved_nulls_radians'},
            {'key': 'visible_margin_radians_str', 'help_key': 'help_visible_margin_radians_str'},
            {'key': 'visible_margin_degrees_str', 'help_key': 'help_visible_margin_degrees_str'},
            {'key': 'directivity_linear', 'help_key': 'help_directivity_linear'},
            {'key': 'directivity_db', 'help_key': 'help_directivity_db'}
        ]
    
    def _find_achieved_nulls(self, af_db: np.ndarray, theta_rad: np.ndarray) -> np.ndarray:
        """
        Finds the actual null positions by finding deep valleys in the pattern.
        
        Parameters:
            af_db: Array factor in dB scale.
            theta_rad: Angle array in radians.
            
        Returns:
            Array of angles (in radians) where nulls are achieved.
        """
        peak_height_threshold = -self.DEFAULT_NULL_DEPTH_DB  # e.g., 40 dB
        internal_indices, _ = find_peaks(-af_db, height=peak_height_threshold)
        
        boundary_indices = []
        if af_db[0] <= self.DEFAULT_NULL_DEPTH_DB: boundary_indices.append(0)
        if af_db[-1] <= self.DEFAULT_NULL_DEPTH_DB: boundary_indices.append(len(af_db) - 1)
        
        all_indices = np.union1d(internal_indices, boundary_indices).astype(int)
        
        achieved_nulls_rad = theta_rad[all_indices]
        
        return achieved_nulls_rad

    
