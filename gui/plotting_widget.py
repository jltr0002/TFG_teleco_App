"""
Plotting widget for antenna synthesis visualization.
"""

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import mplcursors
from mplcursors import Selection
from matplotlib.projections.polar import PolarAxes
from matplotlib.ticker import FuncFormatter, MultipleLocator
from fractions import Fraction
from typing import Dict, Any, List, cast

import os
import sys

from translations import translations

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Dev mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def format_theta_as_pi(value, tick_number):
    """
    Formatea un valor de ángulo theta (0 a pi) como una fracción de π.
    """
    # Si el valor es muy cercano a cero
    if np.isclose(value, 0):
        return "0"
    
    # Si el valor es muy cercano a pi
    if np.isclose(value, np.pi):
        return "π"

    # Find the closest multiple of π/8
    numerator = int(np.round(8 * value / np.pi))
    
    # Simplify the fraction (numerator / 8)
    frac = Fraction(numerator, 8)
    num = frac.numerator
    den = frac.denominator

    # Formatea la cadena de salida (solo casos positivos)
    if num == 1:
        pi_str = "π"
    else:
        pi_str = f"{num}π"

    if den == 1:
        return pi_str
    else:
        return f"{pi_str}/{den}"

class PlottingWidget(QWidget):
    """
    Widget for plotting array factors and excitations.
    MPLS funcionality
    - Hover: Show a temporary datatip.
    - Left-click: Make the datatip persistent.
    - Right-click on a persistent datatip: Remove it.
    - Drag a persistent datatip to move it.
    """
    
    def __init__(self):
        super().__init__()
        
        # Store current data for interaction
        self.current_results = None 


        # self.hover_cursor: mplcursors.Cursor | None = None
        # self.click_cursor: mplcursors.Cursor | None = None
        self.hover_cursor = None
        self.click_cursor = None

        # Store the latest global params to use in callbacks
        self._global_params: Dict[str, Any] = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the plotting interface."""
        layout = QVBoxLayout(self)
        
        # Create splitter for top and bottom plots
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Top plot: Array Factor (rectangular)
        self.af_figure = Figure(figsize=(10, 4))
        self.af_canvas = FigureCanvas(self.af_figure)
        splitter.addWidget(self.af_canvas)
        
        # Bottom section: Polar plot and excitations
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # Polar plot
        self.polar_figure = Figure(figsize=(5, 4))
        self.polar_canvas = FigureCanvas(self.polar_figure)
        bottom_layout.addWidget(self.polar_canvas)
        
        # Excitations plot
        self.excitations_figure = Figure(figsize=(5, 4))
        self.excitations_canvas = FigureCanvas(self.excitations_figure)
        bottom_layout.addWidget(self.excitations_canvas)
        
        splitter.addWidget(bottom_widget)
        
        # Array elements plot (separate widget)
        self.elements_figure = Figure(figsize=(12, 6))
        self.elements_canvas = FigureCanvas(self.elements_figure)
        splitter.addWidget(self.elements_canvas)
        
        # Set splitter proportions: 33% for each section
        splitter.setSizes([400, 400, 400])
    
    def setup_interactions(self, artists_to_track: List[Any]):
        """Setup two separate mplcursors: one for hover, one for persistent clicks."""        
        # Limpiar cursores antiguos
        if self.hover_cursor: self.hover_cursor.remove()
        if self.click_cursor: self.click_cursor.remove()

        # --- 1. Cursor for Hover (temporary) ---
        self.hover_cursor = mplcursors.cursor(artists_to_track, hover=True)
        
        @self.hover_cursor.connect("add")
        def on_hover(sel: Selection):
            # Use a light style for hover
            sel.annotation.get_bbox_patch().set(facecolor='ivory', alpha=0.7)
            # Customize hover text
            self.format_annotation_text(sel)

        # --- 2. Cursor for Clicks (permanent) ---
        self.click_cursor = mplcursors.cursor(artists_to_track, hover=False, multiple=True)

        @self.click_cursor.connect("add")
        def on_add(sel: Selection):
            # Use a more prominent style for fixed annotations
            sel.annotation.get_bbox_patch().set(facecolor='lightblue', alpha=0.9, ec="black", lw=0.5)
            sel.annotation.arrow_patch.set(edgecolor="black", facecolor="lightblue", alpha=0.9, lw=0.5)
            
            # Customize text (reuse the same function)
            self.format_annotation_text(sel)

            # Logic for removal with right-click
            original_event = getattr(sel.target, 'event', None)
            if original_event and original_event.button == 3:
                if self.click_cursor:
                    self.click_cursor.remove_selection(sel)
    
    def format_annotation_text(self, sel):
        """Helper function to format the text for any annotation."""
        ax = sel.artist.axes
        x, y = sel.target
        
        if ax == self.af_figure.axes[0]:
            is_linear = self._global_params.get('rectangular_scale') == 'linear'
            unit = "rad" if self._global_params.get('angle_unit_rectangular') == 'radians' else "°"
            scale_label = "" if is_linear else " dB"
            sel.annotation.set_text(f"Angle: {x:.2f}{unit}\nLevel: {y:.2f}{scale_label}")
        
        elif ax in self.excitations_figure.axes:
            element = int(round(x))
            if ax == self.excitations_figure.axes[0]:
                sel.annotation.set_text(f"Element: {element}\nMag: {y:.3f}")
            else:
                phase_unit = self._global_params.get('element_phase_unit', 'degrees')
                unit_symbol = "°" if phase_unit == 'degrees' else " rad"
                sel.annotation.set_text(f"Element: {element}\nPhase: {y:.3f}{unit_symbol}")

        elif isinstance(ax, PolarAxes):
            angle_deg = np.rad2deg(x)
            if angle_deg > 180: angle_deg = 360 - angle_deg
            is_linear = self._global_params.get('polar_scale') == 'linear'
            scale_label = "" if is_linear else " dB"
            sel.annotation.set_text(f"Angle: {angle_deg:.1f}°\nLevel: {y:.2f}{scale_label}")
        
    def update_plots(self, results: Dict[str, Any], global_params: Dict[str, Any]):
        """Update all plots and re-initialize the interactive cursors."""
        self._global_params = global_params
        if not results:
            self.clear_plots()
            return
        
        self.current_results = results
            
        try:
            artists1 = self.plot_array_factor_rectangular(results, global_params)
            artists2 = self.plot_array_factor_polar(results, global_params)
            artists3 = self.plot_excitations(results)
            self.plot_array_elements(results, global_params)

            # FIX 3 & 4: Ensure we are summing lists, not None types
            all_artists = (artists1 or []) + (artists2 or []) + (artists3 or [])
            self.setup_interactions(all_artists)
                
            self.af_canvas.draw()
            self.polar_canvas.draw()
            self.excitations_canvas.draw()
            self.elements_canvas.draw()
            
        except Exception as e:
            print(f"Error updating plots: {e}")
            self.clear_plots()
            
    def plot_array_factor_rectangular(self, results: Dict[str, Any], params: Dict[str, Any]):
        """Plot array factor in rectangular coordinates. This function only visualizes data."""

        self.af_figure.clear()
        ax = self.af_figure.add_subplot(111)
        interactive_artists: List[Any] = []
        
        # Determine which data arrays to use based on the scale
        scale = params.get('rectangular_scale', 'dB')
        threshold_db = params.get('threshold_db', -90)
        angle_unit = params.get('angle_unit_rectangular', 'degrees')
        normalize = params.get('normalize_array_factor', True)

        if scale == 'linear':
            # Choose between normalized or original AF based on user preference
            if normalize:
                af_complex = results.get('normalized_af')
                af_desired_complex = results.get('desired_af_normalized') if 'desired_af_normalized' in results else results.get('desired_af')
            else:
                af_complex = results.get('af')
                # For non-normalized view, show the desired pattern as-is (max = 1.0)
                af_desired_complex = results.get('desired_af')
            
            af_data = np.abs(af_complex) if af_complex is not None else None
            af_desired_data = np.abs(af_desired_complex) if af_desired_complex is not None else None
            y_label = translations.tr("array_factor_linear")
            max_af = np.max(af_data) if af_data is not None else 1.0
            y_max, y_min = max_af*1.1, 0
            threshold_val = 10**(threshold_db / 20)
        else: 
            # Default to dB
            af_data = results.get('af_db')
            af_desired_data = results.get('desired_af_db')
            y_label = translations.tr("array_factor_db")
            y_label, y_max, y_min = translations.tr("array_factor_db"), 5, threshold_db - 5
            threshold_val = threshold_db
            max_af = None  # Not applicable in dB scale

        # If primary data is missing, do nothing and return
        if af_data is None: 
            ax.text(0.5, 0.5, translations.tr("no_data_to_display"), ha='center', va='center')
            return        

        # Determine which angle array to use
        if angle_unit == 'radians':
            theta = results.get('theta_radians', [])
            x_label = translations.tr("angle_theta_radians")            

            # 2. Aplica el formateador al eje X
            ax.xaxis.set_major_formatter(FuncFormatter(format_theta_as_pi))

            # 3. (Optional) Manually define where you want the ticks for better control
            ax.xaxis.set_major_locator(MultipleLocator(base=np.pi / 8))
        else:
            theta = results.get('theta_degrees', [])
            x_label = translations.tr("angle_theta_degrees")

        if len(theta) == 0: return

        # Plot reconstructed array factor (always present) using np.maximun to show the umbral
        interactive_artists.extend(ax.plot(theta, np.maximum(af_data, threshold_val), 'b-', linewidth=2, label=translations.tr("array_factor_computed")))

        # Plot desired array factor (if available)
        if af_desired_data is not None:
            interactive_artists.extend(ax.plot(theta, np.maximum(af_desired_data, threshold_val), 'r--', linewidth=1.5, label=translations.tr("desired_pattern")))

        # Plot desired sidelobe level line (if available)
        if 'sidelobe_level_desired' in results:
            sll_db = results['sidelobe_level_desired']
            sll_val = 10**(sll_db / 20) if scale == 'linear' else sll_db
            ax.axhline(y=sll_val, color='orange', linestyle='--', alpha=0.8, label=f"{translations.tr('desired_sll')} ({sll_db:.1f} dB)")

        # Plot reference lines
        if scale == 'linear':
            if normalize:
                # Only show the 1.0 reference line when normalized
                ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.6, linewidth=1, label=translations.tr("reference_1_0"))
            else:
                # Show both 1.0 and max reference lines when not normalized
                ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.6, linewidth=1, label=translations.tr("reference_1_0"))
                if max_af is not None:
                    ax.axhline(y=max_af, color='green', linestyle='--', alpha=0.6, linewidth=1, label=f"{translations.tr('reference_max')} ({max_af:.2f})")
        else:
            # In dB scale, show 0 dB reference line
            ax.axhline(y=0.0, color='black', linestyle='--', alpha=0.6, linewidth=1, label=translations.tr("reference_0db"))

        # Plot threshold line (only in dB scale where it's meaningful)
        if scale == 'dB':
            ax.axhline(y=threshold_val, color='gray', linestyle=':', alpha=0.7, label=f"{translations.tr('threshold')} ({threshold_db} dB)")

        ax.set_title(translations.tr("array_factor_vs_angle"))
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        ax.set_xlim(theta[0], theta[-1])
        ax.set_ylim(y_min, y_max)
        
        self.af_figure.tight_layout()

        return interactive_artists

    def plot_array_factor_polar(self, results: Dict[str, Any], params: Dict[str, Any]):
        """Plot array factor in polar coordinates."""
        self.polar_figure.clear()
        interactive_artists: List[Any] = []
        
        ax_generic = self.polar_figure.add_subplot(111, projection='polar')
        ax = cast(PolarAxes, ax_generic)

        scale = params.get('polar_scale', 'dB')
        threshold_db = params.get('threshold_db', -90)        
        angle_unit = params.get('angle_unit_polar', 'degrees')
        normalize = params.get('normalize_array_factor', True)

        if scale == 'linear':
            # Choose between normalized or original AF based on user preference
            if normalize:
                af_complex = results.get('normalized_af')
                af_desired_complex = results.get('desired_af_normalized') if 'desired_af_normalized' in results else results.get('desired_af')
            else:
                af_complex = results.get('af')
                # For non-normalized view, show the desired pattern as-is (max = 1.0)
                af_desired_complex = results.get('desired_af')
            
            af_data = np.abs(af_complex) if af_complex is not None else None
            af_desired_data = np.abs(af_desired_complex) if af_desired_complex is not None else None
            max_af = np.max(af_data) if af_data is not None else 1.0
            r_max, r_min = max_af*1.1 if not normalize else 1.1, 0
            zero_db_ref = 1.0
        else: # Default to dB
            af_data, af_desired_data = results.get('af_db'), results.get('desired_af_db')
            max_af = None  # Not applicable in dB scale
            r_max, r_min = 5, threshold_db
            zero_db_ref = 0.0
            
        if af_data is None or len(af_data) == 0: return

        # Apply the threshold for visualization purposes
        af_thresholded = np.maximum(af_data, r_min)
        
        # Original data for the right side (0 to 180 degrees)
        theta_rad_right = results.get('theta_radians', [])
        
        if len(theta_rad_right) == 0: return

        # Mirrored data for the left side (180 to 360 degrees)
        # This maps the 0-180 degree angle space to the 180-360 degree polar space
        theta_rad_left = np.pi + (np.pi - theta_rad_right[::-1])
        af_left = af_thresholded[::-1] # Reverse the data array to mirror it
        
        # Combine both sides for a full 360-degree plot
        theta_full = np.concatenate([theta_rad_right, theta_rad_left])
        af_full = np.concatenate([af_thresholded, af_left])
        
        # Plot the full reconstructed array factor
        interactive_artists.extend(ax.plot(theta_full, af_full, 'b-', linewidth=2, label=translations.tr("array_factor_computed")))

        ax.fill(theta_full, af_full, 'b', alpha=0.3)
        
        # Plot the full desired array factor (if available)
        if af_desired_data is not None:
            af_desired_thresholded = np.maximum(af_desired_data, r_min)
            af_desired_left = af_desired_thresholded[::-1]
            af_desired_full = np.concatenate([af_desired_thresholded, af_desired_left])
            ax.plot(theta_full, af_desired_full, 'r--', linewidth=1.5, label=translations.tr("desired"))

        # --- REFERENCE CIRCLES ---
        ref_theta = np.linspace(0, 2 * np.pi, 100)
        
        if scale == 'linear':
            # Only show the 1.0 reference line (normalized or not)
            ax.plot(ref_theta, np.full_like(ref_theta, 1.0), color='black', linestyle='--', alpha=0.6, linewidth=1, label=translations.tr("reference_1_0"))
        else:
            # In dB scale, show 0 dB reference line
            ax.plot(ref_theta, np.full_like(ref_theta, zero_db_ref), color='black', linestyle='--', alpha=0.6, linewidth=1, label=translations.tr("reference_0db"))
        
        # Add radial tick for the reference level for clarity
        current_rticks = list(ax.get_yticks())
        if zero_db_ref not in current_rticks:
            current_rticks.append(zero_db_ref)
        ax.set_yticks(sorted(current_rticks))

        # --- CONFIGURE FULL POLAR PLOT ---
        # Now Pylance knows that 'ax' is a PolarAxes and recognizes these methods
        ax.set_theta_zero_location('N')  # 0 degrees at the top
        ax.set_theta_direction(-1)       # Clockwise direction
        ax.set_ylim(r_min, r_max)
        ax.set_title(translations.tr("array_factor_polar_symmetric"))
        
        # Set symmetric angular grid labels
        if angle_unit == 'radians':
            # Define ticks and labels for radians
            radian_ticks_values = np.array([0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330])
            # Convert tick values from degrees to radians so Matplotlib places them correctly
            radian_ticks_rad = np.deg2rad(radian_ticks_values)

            # The labels we show to the user
            labels_rad = [
                '0', 'π/6', 'π/3', 'π/2', '2π/3', '5π/6', 'π', 
                '5π/6', '2π/3', 'π/2', 'π/3', 'π/6'
            ]
            ax.set_thetagrids(radian_ticks_values, labels_rad)
        else: # By default, use degrees
            degree_ticks = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
            labels_deg = ['0°', '30°', '60°', '90°', '120°', '150°', '180°', '150°', '120°', '90°', '60°', '30°']
            ax.set_thetagrids(degree_ticks, labels_deg)
        
        # Always show legend (includes reference line and optionally desired pattern)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        self.polar_figure.tight_layout()

        return interactive_artists
        
    def plot_excitations(self, results: Dict[str, Any]):
        self.excitations_figure.clear()
        excitations = results.get('element_excitations')
        if excitations is None:
            return

        n_elements = len(excitations)
        element_indices = np.arange(1, n_elements + 1)
        
        magnitudes = np.abs(excitations)
        
        # Get phase unit from global parameters
        phase_unit = self._global_params.get('element_phase_unit', 'degrees')
        if phase_unit == 'radians':
            phases = np.angle(excitations, deg=False)
            phase_label = translations.tr("phase_radians")
        else:
            phases = np.angle(excitations, deg=True)
            phase_label = translations.tr("phase_degrees")
        
        ax1 = self.excitations_figure.add_subplot(211)
        ax2 = self.excitations_figure.add_subplot(212, sharex=ax1)
        
        # Magnitude plot
        mag_stem_container = ax1.stem(element_indices, magnitudes, linefmt='b-', markerfmt='bo', basefmt=' ')
        ax1.set_ylabel(translations.tr("magnitude"))
        ax1.set_title(translations.tr("element_excitations"))
        ax1.grid(True, linestyle=':', alpha=0.6)
        
        # Phase plot
        phase_stem_container = ax2.stem(element_indices, phases, linefmt='r-', markerfmt='ro', basefmt=' ')
        ax2.set_xlabel(translations.tr("element_number"))
        ax2.set_ylabel(phase_label)
        ax2.grid(True, linestyle=':', alpha=0.6)
        
        ax1.set_xlim(0.5, n_elements + 0.5)
        ax2.set_xlim(0.5, n_elements + 0.5)
        
        # Adjust phase plot y-limits when values are near ±180°
        if phase_unit == 'degrees':
            phase_min, phase_max = np.min(phases), np.max(phases)
            # Check if any phase values are close to ±180°
            if np.any(np.abs(phases) > 150):  # Values closer to ±180°
                ax2.set_ylim(-185, 185)
            else:
                # Default auto-scaling with some padding
                phase_range = phase_max - phase_min
                padding = max(10, phase_range * 0.1)  # At least 10° padding
                ax2.set_ylim(phase_min - padding, phase_max + padding)
        else:
            # For radians, check if values are close to ±π
            phase_min, phase_max = np.min(phases), np.max(phases)
            if np.any(np.abs(phases) > 2.6):  # Close to ±π (3.14)
                ax2.set_ylim(-3.3, 3.3)
        
        if n_elements <= 20: # Show all ticks for small arrays
            ax2.set_xticks(element_indices)
        
        self.excitations_figure.tight_layout()

        return [mag_stem_container.stemlines, phase_stem_container.stemlines]

    def _select_element_canvas(self, layout_type: str, num_elements: int) -> str:
        """
        Select the appropriate element placement image based on layout type and number of elements.
        
        Parameters:
        -----------
        layout_type : str
            The layout type ('symmetric', 'unilateral', etc.)
        num_elements : int
            The number of elements in the array
            
        Returns:
        --------
        str
            The filename of the PNG image to display
        """
        if layout_type == 'unilateral':
            return 'unilateral.png'
        elif layout_type == 'symmetric':
            # For symmetric arrays, choose based on odd/even number of elements
            if num_elements % 2 == 0:
                return 'even.png'
            else:
                return 'odd.png'
        else:
            # Default fallback
            return 'unilateral.png'

    def plot_array_elements(self, results: Dict[str, Any], params: Dict[str, Any]):
        """Plot array elements placement diagram using pre-made element layout images."""
        self.elements_figure.clear()
        
        try:
            # Get actual number of elements from results, not input parameters
            num_elements = results.get('n_elements')
            if num_elements is None:
                # Fallback: try to get from element excitations
                excitations = results.get('element_excitations')
                if excitations is not None:
                    num_elements = len(excitations)
                else:
                    # Final fallback to input values
                    input_values = params.get('input_values', {})
                    num_elements = int(input_values.get('n_elements', 10))
            
            # Get layout type
            layout_type = results.get('layout_type') or params.get('layout_type', 'symmetric')
            
            # Select the appropriate element canvas image
            image_filename = self._select_element_canvas(layout_type, num_elements)
            relative_image_path = os.path.join('gui', 'plots', 'element_placement', image_filename)
            image_path = resource_path(relative_image_path)
            
            # Check if image file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Element placement image not found: {image_path}")
            
            # Load and display the image
            ax = self.elements_figure.add_subplot(111)
            
            # Read the image using matplotlib
            import matplotlib.image as mpimg
            img = mpimg.imread(image_path)
            
            # Display the image
            ax.imshow(img)
            ax.axis('off')  # Hide axes for clean image display
            
            # Add title with array information
            title = f"{layout_type.title()} Array Layout ({num_elements} elements)"
            ax.set_title(title, fontsize=12, pad=10)
            
            self.elements_canvas.draw()
            
        except Exception as e:
            # Show error message if plot generation fails
            ax = self.elements_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Cannot display array layout:\n{str(e)}", 
                   ha='center', va='center', fontsize=12, alpha=0.7)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.elements_canvas.draw()
        
    def clear_plots(self):
        """Clear all plots and display a message."""

        # if self.hover_cursor: self.hover_cursor.remove()
        # if self.click_cursor: self.click_cursor.remove()
        self.hover_cursor = None
        self.click_cursor = None

        for fig in [self.af_figure, self.polar_figure, self.excitations_figure, self.elements_figure]:
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, translations.tr("not_computed"), ha='center', va='center', fontsize=12, alpha=0.5)
            ax.set_xticks([])
            ax.set_yticks([])
        
        self.af_canvas.draw()
        self.polar_canvas.draw()
        self.excitations_canvas.draw()
        self.elements_canvas.draw()
    
    def export_plots(self, base_filename: str, file_format: str = 'png'):
        """
        Export all plots to files.
        
        Parameters:
        -----------
        base_filename : str
            Base filename without extension
        file_format : str
            File format ('png' or 'svg')
        """
        
        # Ensure the directory exists
        directory = os.path.dirname(base_filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Export array factor plot
        af_filename = f"{base_filename}_array_factor.{file_format}"
        self.af_figure.savefig(af_filename, format=file_format, dpi=300, bbox_inches='tight')
        
        # Export polar plot
        polar_filename = f"{base_filename}_polar.{file_format}"
        self.polar_figure.savefig(polar_filename, format=file_format, dpi=300, bbox_inches='tight')
        
        # Export excitations plot
        excitations_filename = f"{base_filename}_excitations.{file_format}"
        self.excitations_figure.savefig(excitations_filename, format=file_format, dpi=300, bbox_inches='tight')
        
        # Export array elements plot
        elements_filename = f"{base_filename}_elements.{file_format}"
        self.elements_figure.savefig(elements_filename, format=file_format, dpi=300, bbox_inches='tight')
        
        return [af_filename, polar_filename, excitations_filename, elements_filename]
    