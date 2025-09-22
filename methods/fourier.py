import numpy as np
import warnings
from typing import List, Dict, Any, Optional
from .synthesis import SynthesisMethod


class FourierMethod(SynthesisMethod):
    """
    Implementation of Fourier synthesis for linear antenna arrays.
    
    This class synthesizes an array by defining a desired pattern in the physical
    theta-domain, transforming it to the psi-domain, and then applying the
    Fourier series formula to compute the required element excitations.
    """

    @property
    def name(self) -> str:
        return "Fourier"

    @property
    def description(self) -> str:    
        return "Fourier synthesis supporting N beams defined in theta-space"
    
    @property
    def layout_type(self) -> str:
        """Fourier method produces a symetric array"""
        return "symmetric"
    
    def _parse_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Parses input parameters from GUI keyword arguments into internal format.
        
        Returns:
            Dictionary containing parsed parameters ready for validation.
        """
        try:
            d_lambda = float(kwargs['d_lambda'])
            n_elements = int(kwargs['n_elements'])
            theta0_angle = kwargs['theta0_angle']  # Already parsed by GUI
            number_of_beams = int(kwargs['number_of_beams'])
            beam_shape = kwargs['beam_shape']
        except KeyError as e:
            raise ValueError(f"missing_parameter:{e.args[0]}")
        
        # Convert theta0_angle to float if it's a string (backward compatibility)
        if isinstance(theta0_angle, str):
            theta0_angle = float(theta0_angle)
        
        angle_unit = kwargs.get('angle_unit', 'degrees')
        resolution = int(kwargs.get('resolution', 5000))

        # Collect beam angles from dynamic input fields
        beam_angles = []
        for i in range(1, number_of_beams + 1):
            beam_angles_key = f'beam_angles_{i}'
            if beam_angles_key in kwargs:
                beam_angles_value = kwargs[beam_angles_key]
                if isinstance(beam_angles_value, list):
                    # Already parsed by GUI (list of floats)
                    beam_angles.extend(beam_angles_value)
                elif isinstance(beam_angles_value, str):
                    # Backward compatibility - parse string manually
                    if beam_angles_value.strip() == "":
                        continue
                    else:
                        try:
                            angles_pair = [float(s.strip()) for s in beam_angles_value.split(',')]
                            beam_angles.extend(angles_pair)
                        except ValueError:
                            raise ValueError(f"error_could_not_parse_beam_angles:{i}")
                else:
                    # Direct list/array input
                    beam_angles.extend(list(beam_angles_value))

        if angle_unit == "degrees":
            theta0_rad = np.deg2rad(theta0_angle)
            beam_angles = np.deg2rad(beam_angles)
        else:
            beam_angles = np.array(beam_angles)
            theta0_rad = theta0_angle

        return {
            "d_lambda": d_lambda,
            "n_elements": n_elements,
            "theta0_rad": theta0_rad,
            "number_of_beams": number_of_beams,
            "beam_shape": beam_shape,
            "beam_angles": beam_angles,
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
        n = int(params["n_elements"])
        if n < 2:
            raise ValueError("error_number_of_elements_min_2")
        
        d_lambda = float(params["d_lambda"])
        if not np.isfinite(d_lambda) or d_lambda <= 0.0:
            raise ValueError("error_d_lambda_must_be_positive")
        
        res = int(params["resolution"])
        if res < 16:
            raise ValueError("error_resolution_must_be_at_least_16")
        
        theta0_rad = float(params["theta0_rad"])
        if not np.isfinite(theta0_rad) or not (0.0 <= theta0_rad <= np.pi):
            raise ValueError("error_main_beam_angle_out_of_range")

        supported_shapes = ['rectangular', 'triangular'] 
        beam_shape = params.get("beam_shape")
        if beam_shape not in supported_shapes:
            raise ValueError(
                f"Unsupported beam shape: '{beam_shape}'. "
                f"Supported shapes are: {', '.join(supported_shapes)}."
            )
        
        num_beams_choice = int(params["number_of_beams"])
        beam_angles_rad = params.get("beam_angles", np.array([]))

        expected_angles = 2 * num_beams_choice
        if len(beam_angles_rad) != expected_angles:
            raise ValueError(
                f"For the selected {num_beams_choice} beam(s), exactly {expected_angles} angles are required "
                f"(a start and an end angle for each beam). You provided {len(beam_angles_rad)}."
            )
        
        if beam_angles_rad.size > 0:
            # Iterate in pairs of 2 to process each pair (start, end)
            for i in range(0, len(beam_angles_rad), 2):
                start_angle_rad = beam_angles_rad[i]
                end_angle_rad = beam_angles_rad[i+1]
                
                # First, validate that both angles of the pair are in the range [0, 180]
                if not (0 <= start_angle_rad <= np.pi and 0 <= end_angle_rad <= np.pi):
                    start_deg = np.rad2deg(start_angle_rad)
                    end_deg = np.rad2deg(end_angle_rad)
                    raise ValueError(
                        f"Invalid angle found in pair ({start_deg:.2f}, {end_deg:.2f}). "
                        "All angles must be between 0 and 180 degrees."
                    )
                
                # Second, validate that the start angle is LESS than the end angle.
                if start_angle_rad >= end_angle_rad:
                    start_deg = np.rad2deg(start_angle_rad)
                    end_deg = np.rad2deg(end_angle_rad)
                    beam_num = (i // 2) + 1 # Para saber si es el par #1, #2, etc.
                    raise ValueError(
                        f"For beam #{beam_num}, the start angle ({start_deg:.2f}°) must be "
                        f"strictly less than the end angle ({end_deg:.2f}°)."
                    )

    def _prepare_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional hook to derive intermediate parameters after validation.
        Default implementation returns params unchanged.
        Subclasses can override to compute constants like kd, alpha, grids, etc.
        """
        # Derive fundamental constants
        k = 2.0 * np.pi  # Wave number: 2π/λ
        kd = k * float(params["d_lambda"])  # Spacing in electrical radians
        theta0_rad = float(params["theta0_rad"])
        alpha_rad = -kd * np.cos(theta0_rad)

        # Angular grid and psi grid
        theta_rad = np.linspace(0.0, np.pi, int(params["resolution"]))
        psi_rad = kd*np.cos(theta_rad)

        psi_min_rad, psi_max_rad = -kd, kd
        
        beam_angles =params["beam_angles"]
        beam_shape = params["beam_shape"]        
        desired_af = self.compute_desired_pattern(theta_rad, beam_angles, beam_shape)

        prepared_params =  dict(params)     
        prepared_params.update({
            "k": k,
            "kd": kd,
            "alpha_rad": alpha_rad,
            "theta_rad": theta_rad,
            "psi_rad": psi_rad,
            "psi_min_rad": psi_min_rad,
            "psi_max_rad": psi_max_rad,
            "desired_af": desired_af
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
        """
        Computes excitations using the Fourier series integral of the desired pattern.
        """
        # 1. Get the necessary parameters
        n_elements = params['n_elements']
        desired_af_theta = params['desired_af'] # Pattern in theta domain
        
        # Original grids of theta and psi
        psi_rad_grid = params['psi_rad'] # kd*cos(theta)

        # Real limits of integration (the visible space)
        psi_min, psi_max = -np.pi, np.pi

        # Length of the integration interval
        L_psi = psi_max - psi_min
        
        # Map the desired pattern F(theta) to F(psi) using interpolation.
        # It's crucial that the psi grid is sorted for interpolation to work.
        sort_indices = np.argsort(psi_rad_grid)
        psi_sorted = psi_rad_grid[sort_indices]
        desired_af_sorted = desired_af_theta[sort_indices]
        
        # The interpolation function gives us F(psi)
        # Create it once for reuse
        F_psi = lambda psi: np.interp(psi, psi_sorted, desired_af_sorted, left=0, right=0)

        # Calculate the coefficients (excitations)
        excitations = []
        element_indices = np.arange(n_elements) - (n_elements - 1) / 2.0

        # Create a high-resolution grid ONLY for integration
        psi_integration_grid = np.linspace(psi_min, psi_max, params['resolution'])
        for n in element_indices:
            # The integrand is F(psi) * exp(j*n*psi)
            # Create a high-resolution grid ONLY for integration
            integrand = F_psi(psi_integration_grid) * np.exp(-1j * n * psi_integration_grid)
            
            # Perform numerical integration over the visible space
            integral_result = np.trapezoid(integrand, psi_integration_grid)
            
            # The scaling factor is 1 / Interval_Length
            a_n = integral_result / L_psi if L_psi > 0 else 0
            excitations.append(a_n)
        
        excitations = np.array(excitations)
        
        theta0_rad = params['theta0_rad']
        d_lambda = params['d_lambda']
        steered_excitations = self.steer(excitations, d_lambda, theta0_rad)

        return steered_excitations  
    
    def _compute_af(self, excitations: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Computes the RAW, complex array factor.
        This method should NOT normalize or convert to dB.
        """
        psi_rad = params["psi_rad"]
        N = len(excitations)
        
        # Symmetric indices around the center
        n_indices = np.arange(N) - (N - 1) / 2.0
        
        # Matriz de fase (Vandermonde)
        phase_matrix = np.exp(1j * np.outer(n_indices, psi_rad))
        
        # El factor de array es la suma ponderada
        af = np.sum(excitations[:, np.newaxis] * phase_matrix, axis=0)
        
        return af

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

    def _format_output(self, results: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats the final output results for the GUI and user consumption.
        
        Parameters:
            results: Dictionary of processed intermediate results.
            params: Dictionary of input parameters.
            
        Returns:
            Dictionary of formatted final results.
        """
        theta_rad = params['theta_rad']
        theta_deg = np.rad2deg(theta_rad)

        psi_min_rad_steered, psi_max_rad_steered = params['psi_min_rad'] + params["alpha_rad"], params['psi_max_rad'] + params["alpha_rad"]
        
        # Visible margin
        visible_margin_rad_str = self._format_visible_margin_radians(psi_min_rad_steered, psi_max_rad_steered)
        visible_margin_deg_str = self._format_visible_margin_degrees(np.rad2deg(psi_min_rad_steered), np.rad2deg(psi_max_rad_steered))

        excitations = results['excitations']
        af = results['raw_af']
        desired_af = params['desired_af']
        desired_max_af = np.max(np.abs(desired_af))
        desired_normalized_af = desired_af / desired_max_af if desired_max_af > 0 else desired_af
        desired_normalized_af = self._zero_small_parts(desired_normalized_af)
        desired_af_db = 20 * np.log10(np.abs(desired_normalized_af) + self.EPSILON)

        # Normalizar excitaciones y el AF sintetizado
        normalized_excitations = self._normalize_excitations(excitations, method='center')
        
        max_af = np.max(np.abs(af))
        normalized_af = af / max_af if max_af > 0 else af
        normalized_af = self._zero_small_parts(normalized_af)
        af_db = 20 * np.log10(np.abs(normalized_af) + self.EPSILON)

        # Calcular directividades
        directivity_linear, directivity_db = self._calculate_directivity_from_af(af, theta_rad)
        desired_directivity_linear, desired_directivity_db = self._calculate_directivity_from_af(desired_af, theta_rad)

        return {
            # excitations
            'element_excitations': normalized_excitations,
            'raw_excitations': excitations,

            # af representation
            'af': af,
            'normalized_af': normalized_af,
            'af_db': af_db,
            'desired_af': desired_af,
            'desired_af_normalized': desired_normalized_af,
            'desired_af_db': desired_af_db,
            'theta_degrees': theta_deg,
            'theta_radians': theta_rad,

            # Visible margin
            'visible_margin_rad_str': visible_margin_rad_str,
            'visible_margin_deg_str': visible_margin_deg_str,

            # Directivity
            'directivity_linear': directivity_linear,
            'directivity_db': directivity_db,            
            'desired_directivity_linear': desired_directivity_linear,
            'desired_directivity_db': desired_directivity_db,

            # geometry plot
            'd_lambda': params['d_lambda'],
            'layout_type': self.layout_type,
            'theta0_rad': params['theta0_rad']
        }
    
    def get_inputs(self, angle_unit: str = "degrees") -> List[Dict[str, Any]]:
        """Return input parameter definitions for GUI."""
        base_inputs = [
            {
                'name': 'd_lambda', 
                'label_key': 'element_spacing', 
                'type': 'float', 
                'default': 0.5, 
                'min': 0.001, 
                'max': 0.5, 
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
                #'default': 21, 
                'min': 2, 
                'max': 100, 
                'step': 1, 
                'help_key': 'help_number_of_elements'
            },            
            {
                'name': 'number_of_beams', 
                'label_key': 'number_of_beams', 
                'type': 'choice', 
                'choices': ['1', '2', '3'], 
                'default': '1',
                'help_key': 'help_number_of_beams'
            },
            {
                'name': 'beam_shape', 
                'label_key': 'beam_shape', 
                'type': 'choice', 
                'choices': ['rectangular', 
                            'triangular'], 
                'default': 'rectangular',
                'help_key': 'help_beam_shape'
            }
        ]
        
        # Return base inputs - the dynamic beam angle inputs will be handled 
        # by get_dynamic_inputs() method
        return base_inputs
        
    def get_dynamic_inputs(self, current_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Return dynamic input parameters based on current form values."""
        dynamic_inputs = []
        
        # Get number of beams from current values or default to 1
        number_of_beams = 1
        if current_values and 'number_of_beams' in current_values:
            try:
                number_of_beams = int(current_values['number_of_beams'])
            except (ValueError, TypeError):
                number_of_beams = 1
        
        # Generate beam angle inputs based on number of beams
        for i in range(1, number_of_beams + 1):
            beam_input = {
                'name': f'beam_angles_{i}',
                'label_key': f'beam_angles_pair_{i}' if number_of_beams > 1 else 'beam_angles_single',
                'type': 'text',
                # 'default': '60, 120' if i == 1 else f'{60 + (i-1)*20}, {120 + (i-1)*20}',
                'help_key': 'help_beam_angles'
            }
            dynamic_inputs.append(beam_input)
        
        return dynamic_inputs
    
    def get_outputs(self) -> List[Dict[str, Any]]:
        """Return output parameter definitions for GUI."""
        return [
            {'key': 'desired_directivity_linear', 'help_key': 'help_desired_directivity_linear'},
            {'key': 'desired_directivity_db', 'help_key': 'help_desired_directivity_db'},
            {'key': 'visible_margin_rad_str', 'help_key': 'help_visible_margin_radians_str'},
            {'key': 'visible_margin_deg_str', 'help_key': 'help_visible_margin_degrees_str'},
            {'key': 'directivity_linear', 'help_key': 'help_directivity_linear'},
            {'key': 'directivity_db', 'help_key': 'help_directivity_db'}
        ]
    
    def compute_desired_pattern(self, theta_rad: np.ndarray, beam_angles: np.ndarray, beam_shape: str) -> np.ndarray:
        """Creates the desired pattern on the theta-grid using sum-and-clip."""
        final_pattern = np.zeros_like(theta_rad, dtype=float)
        for i in range(0, len(beam_angles), 2):
            theta_min, theta_max = min(beam_angles[i], beam_angles[i+1]), max(beam_angles[i], beam_angles[i+1])
            if beam_shape.lower() == 'rectangular':
                beam_pattern = self._rectangular_pattern_theta(theta_rad, theta_min, theta_max)
            elif beam_shape.lower() == 'triangular':
                beam_pattern = self._triangular_pattern_theta(theta_rad, theta_min, theta_max)
            else:
                raise ValueError(f"error_unknown_beam_shape:{beam_shape}")
            final_pattern += beam_pattern
        return np.clip(final_pattern, 0, 1) 
    
    def _rectangular_pattern_theta(self, theta_rad_grid: np.ndarray, theta_min: float, theta_max: float) -> np.ndarray:
        return ((theta_rad_grid >= theta_min) & (theta_rad_grid <= theta_max)).astype(float)

    def _triangular_pattern_theta(self, theta_rad_grid: np.ndarray, theta_min: float, theta_max: float) -> np.ndarray:
        center_theta = (theta_min + theta_max) / 2.0
        half_width_theta = (theta_max - theta_min) / 2.0

        pattern = np.zeros_like(theta_rad_grid)
        if half_width_theta > 0:
            mask = np.abs(theta_rad_grid - center_theta) <= half_width_theta
            pattern[mask] = 1 - np.abs(theta_rad_grid[mask] - center_theta) / half_width_theta
        return pattern