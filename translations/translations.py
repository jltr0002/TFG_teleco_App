"""
Translation system for the antenna synthesis application.
"""

class Translations:
    """Handles translations for the application."""
    
    def __init__(self):
        self.current_language = "es"
        self.translations = {
            "en": {
                # Menu items
                "edit": "Edit",
                "export": "Export",
                "view": "View",
                "preferences": "Preferences",
                "global_parameters": "Global Parameters",
                "export_plots": "Export Plots",
                "export_as_png": "Export as PNG",
                "export_as_svg": "Export as SVG",
                "export_data_json": "Export Data as JSON",
                "export_array_factor_csv": "Export Array Factor as CSV",
                "appearance": "Appearance",
                "reset_view": "Reset View",
                "language": "Language",
                "font_size": "Font Size",
                "english": "English",
                "spanish": "Spanish",
                
                # Window titles
                "main_window_title": "Antenna Synthesis Tool",
                "global_parameters_title": "Display Settings",
                "preferences_title": "Preferences",
                
                # Method names
                "schelkunoff": "Schelkunoff",
                "fourier": "Fourier",
                "chebyshev": "Chebyshev",
                "uniform": "Uniform",
                
                # Group boxes
                "method_selection": "Method Selection",
                "inputs": "Inputs",
                "outputs": "Outputs",
                
                # Buttons
                "compute": "Compute",
                "computing": "Computing...",
                "ok": "OK",
                "cancel": "Cancel",
                "browse": "Browse",
                
                # Tab names
                "array_factor": "Array Factor",
                "array_elements": "Array Elements",
                "excitation_coefficients": "Excitation Coefficients",
                
                # Plot titles
                "array_factor_vs_angle": "Array Factor vs Angle",
                "array_factor_polar": "Array Factor (Polar)",
                "array_factor_polar_symmetric": "Array Factor (Polar) - Symmetric Pattern",
                "array_factor_semi_polar": "Array Factor (Semi-Polar)",
                "element_excitations": "Element Excitations",
                "linear_scale": "Linear Scale",
                "db_scale": "dB Scale",
                "right_side": "Right: 0°→180°, Left: 180°→0°",
                "semi_polar_range": "0° to 180°",
                
                # Input labels
                "element_spacing": "Element spacing (length in wavelengths, λ)",
                "number_of_elements": "Number of elements",
                "main_beam_angle": "Main beam angle θ₀",
                "null_positions": "Null positions",
                "sidelobe_level": "Sidelobe level (dB)",
                "main_beam_direction": "Main beam direction θ₀",
                "number_of_beams": "Number of beams",
                "beam_shape": "Beam shape",
                "beam_angles": "Beam angles (start, end)",
                "beam_angles_single": "Beam angles (start, end)",
                "beam_angles_pair_1": "First pair of beam angles",
                "beam_angles_pair_2": "Second pair of beam angles", 
                "beam_angles_pair_3": "Third pair of beam angles",
                "rectangular": "rectangular",
                "triangular": "triangular",
                
                # Output labels
                "schelkunoff_polynomial_str": "Schelkunoff polynomial",
                "array_factor_computed": "Array factor (computed)",
                "nulls_found": "Nulls found",
                "element_excitations_output": "Element excitations",
                "directivity_linear": "Directivity (linear)",
                "directivity_db": "Directivity (dB)",
                "desired_directivity_linear": "Desired directivity (linear)",
                "desired_directivity_db": "Desired directivity (dB)",
                "reconstructed_directivity_db": "Reconstructed directivity (dB)",
                "achieved_sidelobe_level": "Achieved sidelobe level (dB)",
                "theoretical_beamwidth": "Theoretical beamwidth (degrees)",
                "actual_beamwidth": "Actual beamwidth (degrees)",
                "number_of_elements_used": "Number of elements used",
                "visible_margin_rad_str": "Visible margin (radians)",
                "visible_margin_deg_str": "Visible margin (degrees)",
                "achieved_nulls_deg": "Achieved nulls (degrees)",
                "achieved_nulls_rad": "Achieved nulls (radians)",
                "n_elements": "Number of elements",
                "sidelobe_level_db": "Sidelobe level (dB)",
                "dolph_chebyshev_polynomial_str": "Dolph-Chebyshev polynomial",
                "achieved_sll_db": "Achieved sidelobe level (dB)",
                "d_opt": "d_opt for broadside (λ)",
                "x0_scaling_factor": "Scaling factor (x₀)",
                "theoretical_hpbw_deg": "Theoretical HPBW (degrees)",
                "actual_hpbw_deg": "Actual HPBW (degrees)",
                "peak_sidelobe_level_db": "Peak sidelobe level (dB)",
                "array_length_lambda": "Array length (λ)",
                
                # Schelkunoff specific outputs
                "visible_margin_radians_str": "Visible margin (radians)",
                "visible_margin_degrees_str": "Visible margin (degrees)",
                "achieved_nulls_degrees": "Achieved nulls (degrees)",
                "achieved_nulls_radians": "Achieved nulls (radians)",
                
                # Global parameters
                "precision_decimals": "Display decimals:",
                "input_angle_unit": "Input angle unit:",
                "rectangular_plot_unit": "Rectangular plot unit:",
                "polar_plot_unit": "Polar plot unit:",
                "element_phase_unit": "Element phase unit:",
                "rectangular_plot_scale": "Rectangular plot scale:",
                "polar_plot_scale": "Polar plot scale:",
                "resolution": "Resolution:",
                "threshold_db": "Threshold (dB):",
                "normalize_array_factor": "Normalize Array Factor:",
                "degrees": "degrees",
                "radians": "radians",
                "linear": "linear",
                "db": "dB",
                
                # Messages
                "no_data_to_display": "No data to display",
                "not_computed_yet": "Not computed yet",
                "not_available": "Not available",
                "not_computed": "Not computed",
                "computation_error": "Computation Error",
                "export_error": "Export Error",
                "export_successful": "Export Successful",
                "no_results_to_export": "No results available to export. Please compute first.",
                "error_during_computation": "Error during computation:",
                "data_exported_successfully": "Data exported successfully to:",
                "array_factor_exported_successfully": "Array factor data exported successfully to:",
                "plots_exported_successfully": "Plots exported successfully:",
                "error_exporting_plots": "Error exporting plots:",
                "error_exporting_data": "Error exporting data:",
                "error_exporting_array_factor": "Error exporting array factor:",
                
                # Help text
                "help_null_positions": "List of null positions in degrees/radians",
                "help_main_beam_angle": "Desired direction of the main beam. 90 is broadside.",
                "help_number_of_elements": "Use an odd number for better results",
                "help_n_elements_chebyshev": "Number of antenna elements in the array",
                "help_sidelobe_level": "Sidelobe level below main lobe",
                "help_sll_db": "Maximum allowed sidelobe level in dB below the main beam",
                "help_number_of_elements_auto": "Number of array elements (auto if not specified)",
                "help_beam_angles": "Edges in degrees/radians. E.g., \"60, 120\" or for 2 beams \"30, 60, 120, 150\"",
                "help_n_elements_uniform": "Number of antenna elements with uniform amplitude",
                "help_element_spacing": "Distance between adjacent elements in wavelengths",
                "help_number_of_beams": "Number of radiation beams to synthesize",
                "help_beam_shape": "Shape of the desired beam pattern",
                
                # Output parameter help text
                "help_schelkunoff_polynomial_str": "Schelkunoff polynomial used for null placement",
                "help_n_elements_output": "Number of array elements used in the final synthesis",
                "help_achieved_nulls_degrees": "Actual null positions found in the synthesized pattern (degrees)",
                "help_achieved_nulls_radians": "Actual null positions found in the synthesized pattern (radians)",
                "help_visible_margin_radians_str": "Angular range where the pattern is visible (radians)",
                "help_visible_margin_degrees_str": "Angular range where the pattern is visible (degrees)",
                "help_directivity_linear": "Maximum directivity of the array in linear scale",
                "help_directivity_db": "Maximum directivity of the array in decibels",
                "help_dolph_chebyshev_polynomial_str": "Dolph-Chebyshev polynomial",
                "help_achieved_sll_db": "Actual sidelobe level achieved in the synthesized pattern",
                "help_d_opt": "Optimal element spacing for broadside radiation in wavelengths",
                "help_x0_scaling_factor": "Scaling factor used in Chebyshev polynomial computation",
                "help_desired_directivity_linear": "Target directivity of the desired pattern in linear scale",
                "help_desired_directivity_db": "Target directivity of the desired pattern in decibels",
                "help_theoretical_hpbw_deg": "Theoretical half-power beamwidth in degrees",
                "help_actual_hpbw_deg": "Actual half-power beamwidth measured from synthesized pattern",
                "help_peak_sidelobe_level_db": "Highest sidelobe level in the synthesized pattern",
                "help_array_length_lambda": "Total physical length of the antenna array in wavelengths",
                
                # Error messages
                "input_error": "Input Error", 
                "error_parsing_nulls": "Error parsing nulls:",
                
                # New snake_case error message keys
                "error_could_not_parse_null_angles": "Could not parse null angle values",
                "error_null_positions_cannot_be_empty": "Null positions cannot be empty",
                "error_d_lambda_must_be_positive": "Element spacing must be positive and finite",
                "error_resolution_must_be_at_least_16": "Resolution must be at least 16",
                "error_main_beam_angle_out_of_range": "Main beam angle must be between 0 and pi radians (0 to 180 degrees)",
                "error_number_of_elements_min_2": "Number of elements must be at least 2",
                "error_number_of_elements_min_1": "Number of elements must be at least 1",
                "error_sidelobe_level_must_be_finite": "Sidelobe level must be a finite number",
                "error_theta0_rad_out_of_range": "Main beam angle must be between 0 and pi radians",
                "error_could_not_parse_beam_angles": "Could not parse beam angles for beam",
                "error_unknown_beam_shape": "Unknown beam shape",
                "error_could_not_find_or_parse": "Could not find or parse parameter",
                "error_unknown_normalization_method": "Unknown normalization method",
                "invalid_number_of_beams": "Invalid number of beams. Must be 1 or 2.",
                "could_not_parse_beam_angles": "Could not parse beam angles. Use a comma-separated list of numbers (e.g., '60, 120').",
                "at_least_2_angles_required": "At least 2 angles are required to define 1 beam (e.g., '60, 120').",
                "at_least_4_angles_required": "At least 4 angles are required to define 2 beams (e.g., '30, 60, 120, 150').",
                "number_of_elements_minimum": "Number of elements must be at least 2.",
                "array_factor_data_not_available": "Array factor data not available in results",
                "plotting_widget_not_available": "Plotting widget not available",
                "no_results_available": "No results available to export",
                
                # File dialogs
                "select_file": "Select File",
                "all_files": "All Files (*)",
                "json_files": "JSON files (*.json)",
                "csv_files": "CSV files (*.csv)",
                "png_files": "PNG files (*.png)",
                "svg_files": "SVG files (*.svg)",
                
                # Axis labels
                "angle_theta_degrees": "Angle θ (degrees)",
                "angle_theta_radians": "Angle θ (radians)",
                "array_factor_linear": "Array Factor (Linear)",
                "array_factor_db": "Array Factor (dB)",
                "magnitude": "Magnitude",
                "phase_degrees": "Phase (degrees)",
                "phase_radians": "Phase (radians)",
                "element_number": "Element Number",
                
                # Plot annotations
                "threshold": "Threshold",
                "null": "Null",
                "desired_sll": "Desired SLL",
                "reference_0db": "0 dB Reference",
                "reference_1_0": "1.0 Reference",
                "reference_max": "Max Reference",
                "desired_pattern": "Desired Pattern",
                "desired": "Desired",
                
                # Datatip information
                "element": "Element",
                "mag": "Mag",
                "phase": "Phase",
                
                # Excitation coefficients table
                "coefficient_index": "Index",
                "coefficient_magnitude": "Magnitude",
                "coefficient_phase": "Phase",
                "coefficient_real": "Real part",
                "coefficient_imaginary": "Imaginary part",

                # Errors
                "beam_angles_not_sorted": "Beam angles must be in non-decreasing order (e.g., 10, 20, 20, 30).",
                "beam_angles_max_repetition": "An angle can be repeated at most once consecutively (e.g., 20, 20 is OK, but 20, 20, 20 is not).",
                "help_beam_angles_multi": "For N beams, provide 2*N angles sorted non-decreasingly: start1, end1, start2, end2, ...",
                "multi_beam_angle_error": "Incorrect number of angles. {1} beams require exactly {0} angles.",
                "missing_parameter": "Missing parameter",
                
                # Plot detachment functionality
                "plots": "Plots",
                "detach_plot": "Detach Plot",
                "reattach_plot": "Reattach Plot",
                "reattach_all_plots": "Reattach All Plots",
                "reattach_plot_tooltip": "Reattach this plot to the main window",
                "close": "Close",
                "close_plot_window": "Close this plot window",
                "array_factor_rectangular": "Array Factor (Rectangular)",
                "array_factor_polar": "Array Factor (Polar)",
            },
            "es": {
                # Menu items
                "edit": "Editar",
                "export": "Exportar",
                "view": "Ver",
                "preferences": "Preferencias",
                "global_parameters": "Parámetros globales",
                "export_plots": "Exportar gráficos",
                "export_as_png": "Exportar como PNG",
                "export_as_svg": "Exportar como SVG",
                "export_data_json": "Exportar datos como JSON",
                "export_array_factor_csv": "Exportar factor de array como CSV",
                "appearance": "Apariencia",
                "reset_view": "Restablecer vista",
                "language": "Idioma",
                "font_size": "Tamaño de letra",
                "english": "Inglés",
                "spanish": "Español",
                
                # Window titles
                "main_window_title": "Herramienta de síntesis de antenas",
                "global_parameters_title": "Parámetros globales",
                "preferences_title": "Preferencias",
                
                # Method names
                "schelkunoff": "Schelkunoff",
                "fourier": "Fourier",
                "chebyshev": "Chebyshev",
                "uniform": "Uniforme",
                
                # Group boxes
                "method_selection": "Selección de método",
                "inputs": "Entradas",
                "outputs": "Salidas",
                
                # Buttons
                "compute": "Calcular",
                "computing": "Calculando...",
                "ok": "Aceptar",
                "cancel": "Cancelar",
                "browse": "Examinar",
                
                # Tab names
                "array_factor": "Factor de array",
                "array_elements": "Elementos del array",
                "excitation_coefficients": "Coeficientes de excitación",
                
                # Plot titles
                "array_factor_vs_angle": "Factor de array vs ángulo",
                "array_factor_polar": "Factor de array (polar)",
                "array_factor_polar_symmetric": "Factor de array (polar) - patrón simétrico",
                "array_factor_semi_polar": "Factor de array (semi-polar)",
                "element_excitations": "Excitaciones de elementos",
                "linear_scale": "Escala lineal",
                "db_scale": "Escala dB",
                "right_side": "Derecha: 0°→180°, Izquierda: 180°→0°",
                "semi_polar_range": "0° a 180°",
                
                # Input labels
                "element_spacing": "Espaciado de elementos (en longitudes de onda, λ)",
                "number_of_elements": "Número de elementos",
                "main_beam_angle": "Ángulo del haz principal θ₀",
                "null_positions": "Posiciones de nulos",
                "sidelobe_level": "Nivel de lóbulos secundarios (dB)",
                "main_beam_direction": "Dirección del haz principal θ₀",
                "number_of_beams": "Número de haces",
                "beam_shape": "Forma del haz",
                "beam_angles": "Ángulos del haz (inicio, fin)",
                "beam_angles_single": "Ángulos del haz (inicio, fin)",
                "beam_angles_pair_1": "Primer par de ángulos del haz",
                "beam_angles_pair_2": "Segundo par de ángulos del haz",
                "beam_angles_pair_3": "Tercer par de ángulos del haz",
                "rectangular": "rectangular",
                "triangular": "triangular",
                
                # Output labels
                "schelkunoff_polynomial_str": "Polinomio de Schelkunoff",
                "array_factor_computed": "Factor de array (calculado)",
                "nulls_found": "Nulos encontrados",
                "element_excitations_output": "Excitaciones de elementos",
                "directivity_linear": "Directividad (lineal)",
                "directivity_db": "Directividad (dB)",
                "desired_directivity_linear": "Directividad deseada (lineal)",
                "desired_directivity_db": "Directividad deseada (dB)",
                "reconstructed_directivity_db": "Directividad reconstruida (dB)",
                "achieved_sidelobe_level": "Nivel de lóbulos secundarios logrado (dB)",
                "theoretical_beamwidth": "Ancho de haz teórico (grados)",
                "actual_beamwidth": "Ancho de haz real (grados)",
                "number_of_elements_used": "Número de elementos utilizados",
                "visible_margin_rad_str": "Margen visible (radianes)",
                "visible_margin_deg_str": "Margen visible (grados)",
                "achieved_nulls_deg": "Nulos conseguidos (grados)",
                "achieved_nulls_rad": "Nulos conseguidos (radianes)",
                "n_elements": "Número de elementos",
                "sidelobe_level_db": "Nivel de lóbulos secundarios (dB)",
                "dolph_chebyshev_polynomial_str": "Polinomio de Dolph-Chebyshev",
                "achieved_sll_db": "Nivel de lóbulos secundarios logrado (dB)",
                "d_opt": "d_opt para broadside (λ)",
                "x0_scaling_factor": "Factor de escala (x₀)",
                "theoretical_hpbw_deg": "HPBW teórico (grados)",
                "actual_hpbw_deg": "HPBW real (grados)",
                "peak_sidelobe_level_db": "Nivel máximo de lóbulos secundarios (dB)",
                "array_length_lambda": "Longitud del array (λ)",
                
                # Schelkunoff specific outputs
                "visible_margin_radians_str": "Margen visible (radianes)",
                "visible_margin_degrees_str": "Margen visible (grados)",
                "achieved_nulls_degrees": "Nulos conseguidos (grados)",
                "achieved_nulls_radians": "Nulos conseguidos (radianes)",
                
                # Global parameters
                "precision_decimals": "Decimales en pantalla:",
                "input_angle_unit": "Unidad de ángulo de entrada:",
                "rectangular_plot_unit": "Unidad de gráfico rectangular:",
                "polar_plot_unit": "Unidad de gráfico polar:",
                "element_phase_unit": "Unidad de fase de elementos:",
                "rectangular_plot_scale": "Escala de gráfico rectangular:",
                "polar_plot_scale": "Escala de gráfico polar:",
                "resolution": "Resolución:",
                "threshold_db": "Umbral (dB):",
                "normalize_array_factor": "Normalizar factor de arreglo:",
                "degrees": "grados",
                "radians": "radianes",
                "linear": "lineal",
                "db": "dB",
                
                # Messages
                "no_data_to_display": "No hay datos para mostrar",
                "not_computed_yet": "Aún no calculado",
                "not_available": "No disponible",
                "not_computed": "No calculado",
                "computation_error": "Error de cálculo",
                "export_error": "Error de exportación",
                "export_successful": "Exportación exitosa",
                "no_results_to_export": "No hay resultados disponibles para exportar. Por favor calcule primero.",
                "error_during_computation": "Error durante el cálculo:",
                "data_exported_successfully": "Datos exportados exitosamente a:",
                "array_factor_exported_successfully": "Datos del factor de array exportados exitosamente a:",
                "plots_exported_successfully": "Gráficos exportados exitosamente:",
                "error_exporting_plots": "Error exportando gráficos:",
                "error_exporting_data": "Error exportando datos:",
                "error_exporting_array_factor": "Error exportando factor de array:",
                
                # Help text
                "help_null_positions": "Lista de posiciones de nulos en grados/radianes",
                "help_main_beam_angle": "Dirección deseada del haz principal. 90 es broadside.",
                "help_number_of_elements": "Use un número impar para mejores resultados",
                "help_n_elements_chebyshev": "Número de elementos de antena en el array",
                "help_sidelobe_level": "Nivel de lóbulos secundarios por debajo del lóbulo principal",
                "help_sll_db": "Nivel máximo permitido de lóbulos secundarios en dB por debajo del haz principal",
                "help_number_of_elements_auto": "Número de elementos del array (automático si no se especifica)",
                "help_beam_angles": "Bordes en grados/radianes. Ej., \"60, 120\" o para 2 haces \"30, 60, 120, 150\"",
                "help_n_elements_uniform": "Número de elementos de antena con amplitud uniforme",
                "help_element_spacing": "Distancia entre elementos adyacentes en longitudes de onda",
                "help_number_of_beams": "Número de haces de radiación a sintetizar",
                "help_beam_shape": "Forma del patrón de haz deseado",
                
                # Output parameter help text (Spanish)
                "help_schelkunoff_polynomial_str": "Polinomio de Schelkunoff usado para posicionar nulos",
                "help_n_elements_output": "Número de elementos del array utilizados en la síntesis final",
                "help_achieved_nulls_degrees": "Posiciones reales de nulos encontradas en el patrón sintetizado (grados)",
                "help_achieved_nulls_radians": "Posiciones reales de nulos encontradas en el patrón sintetizado (radianes)",
                "help_visible_margin_radians_str": "Rango angular donde el patrón es visible (radianes)",
                "help_visible_margin_degrees_str": "Rango angular donde el patrón es visible (grados)",
                "help_directivity_linear": "Directividad máxima del array en escala lineal",
                "help_directivity_db": "Directividad máxima del array en decibelios",
                "help_dolph_chebyshev_polynomial_str": "Polinomio de Dolph-Chebyshev",
                "help_achieved_sll_db": "Nivel real de lóbulos secundarios logrado en el patrón sintetizado",
                "help_d_opt": "Espaciado óptimo de elementos para radiación broadside en longitudes de onda",
                "help_x0_scaling_factor": "Factor de escala usado en el cálculo del polinomio de Chebyshev",
                "help_desired_directivity_linear": "Directividad objetivo del patrón deseado en escala lineal",
                "help_desired_directivity_db": "Directividad objetivo del patrón deseado en decibelios",
                "help_theoretical_hpbw_deg": "Ancho de haz teórico a media potencia en grados",
                "help_actual_hpbw_deg": "Ancho de haz real a media potencia medido del patrón sintetizado",
                "help_peak_sidelobe_level_db": "Nivel más alto de lóbulos secundarios en el patrón sintetizado",
                "help_array_length_lambda": "Longitud física total del array de antenas en longitudes de onda",
                
                # Error messages
                "input_error": "Error de entrada",
                "error_parsing_nulls": "Error analizando nulos:",
                
                # New snake_case error message keys (Spanish)
                "error_could_not_parse_null_angles": "No se pudieron analizar los valores de ángulos nulos",
                "error_null_positions_cannot_be_empty": "Las posiciones de nulos no pueden estar vacías",
                "error_d_lambda_must_be_positive": "El espaciado de elementos debe ser positivo y finito",
                "error_resolution_must_be_at_least_16": "La resolución debe ser al menos 16",
                "error_main_beam_angle_out_of_range": "El ángulo del haz principal debe estar entre 0 y pi radianes (0 a 180 grados)",
                "error_number_of_elements_min_2": "El número de elementos debe ser al menos 2",
                "error_number_of_elements_min_1": "El número de elementos debe ser al menos 1",
                "error_sidelobe_level_must_be_finite": "El nivel de lóbulos secundarios debe ser un número finito",
                "error_theta0_rad_out_of_range": "El ángulo del haz principal debe estar entre 0 y pi radianes",
                "error_could_not_parse_beam_angles": "No se pudieron analizar los ángulos del haz para el haz",
                "error_unknown_beam_shape": "Forma de haz desconocida",
                "error_could_not_find_or_parse": "No se pudo encontrar o analizar el parámetro",
                "error_unknown_normalization_method": "Método de normalización desconocido",
                "invalid_number_of_beams": "Número de haces inválido. Debe ser 1 o 2.",
                "could_not_parse_beam_angles": "No se pudieron analizar los ángulos del haz. Use una lista separada por comas (ej., '60, 120').",
                "at_least_2_angles_required": "Se requieren al menos 2 ángulos para definir 1 haz (ej., '60, 120').",
                "at_least_4_angles_required": "Se requieren al menos 4 ángulos para definir 2 haces (ej., '30, 60, 120, 150').",
                "number_of_elements_minimum": "El número de elementos debe ser al menos 2.",
                "array_factor_data_not_available": "Datos del factor de array no disponibles en resultados",
                "plotting_widget_not_available": "Widget de gráficos no disponible",
                "no_results_available": "No hay resultados disponibles para exportar",
                
                # File dialogs
                "select_file": "Seleccionar archivo",
                "all_files": "Todos los archivos (*)",
                "json_files": "Archivos JSON (*.json)",
                "csv_files": "Archivos CSV (*.csv)",
                "png_files": "Archivos PNG (*.png)",
                "svg_files": "Archivos SVG (*.svg)",
                
                # Axis labels
                "angle_theta_degrees": "Ángulo θ (grados)",
                "angle_theta_radians": "Ángulo θ (radianes)",
                "array_factor_linear": "Factor de array (lineal)",
                "array_factor_db": "Factor de array (dB)",
                "magnitude": "Magnitud",
                "phase_degrees": "Fase (grados)",
                "phase_radians": "Fase (radianes)",
                "element_number": "Número de elemento",
                
                # Plot annotations
                "threshold": "Umbral",
                "null": "Nulo",
                "desired_sll": "NSL Deseado",
                "reference_0db": "Referencia 0 dB",
                "reference_1_0": "Referencia 1.0",
                "reference_max": "Referencia máx",
                "desired_pattern": "Patrón deseado",
                "desired": "Deseado",
                
                # Datatip information
                "element": "Elemento",
                "mag": "Mag",
                "phase": "Fase",
                
                # Excitation coefficients table
                "coefficient_index": "Índice",
                "coefficient_magnitude": "Magnitud",
                "coefficient_phase": "Fase",
                "coefficient_real": "Parte real",
                "coefficient_imaginary": "Parte imaginaria",

                # Error messages in Spanish
                "beam_angles_not_sorted": "Los ángulos del haz deben estar en orden no decreciente (ej., 10, 20, 20, 30).",
                "beam_angles_max_repetition": "Un ángulo puede repetirse como máximo una vez consecutivamente (ej., 20, 20 está bien, pero 20, 20, 20 no).",
                "multi_beam_angle_error": "Número incorrecto de ángulos. {1} haces requieren exactamente {0} ángulos.",
                "missing_parameter": "Parámetro faltante",
                
                # Plot detachment functionality
                "plots": "Gráficos",
                "detach_plot": "Desacoplar gráfico",
                "reattach_plot": "Acoplar gráfico",
                "reattach_all_plots": "Acoplar todos los gráficos",
                "reattach_plot_tooltip": "Acoplar este gráfico a la ventana principal",
                "close": "Cerrar",
                "close_plot_window": "Cerrar esta ventana de gráfico",
                "array_factor_rectangular": "Factor de array (rectangular)",
                "array_factor_polar": "Factor de array (polar)",
            }
        }
    
    def set_language(self, language_code: str):
        """Set the current language."""
        if language_code in self.translations:
            self.current_language = language_code
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def tr(self, key: str) -> str:
        """Translate a key to the current language."""
        return self.translations[self.current_language].get(key, key)
    
    def get_available_languages(self) -> dict:
        """Get available languages."""
        return {
            "en": self.tr("english"),
            "es": self.tr("spanish")
        }

# Global translation instance
translations = Translations()