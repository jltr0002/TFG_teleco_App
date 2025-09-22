# In gui/plots/rectangular_plot.py
import numpy as np
from matplotlib.ticker import FuncFormatter, MultipleLocator
from typing import Dict, Any, List
from .base_plot import BasePlotWidget
from translations import translations

class RectangularAFPlotWidget(BasePlotWidget):
    """Widget for plotting the rectangular array factor."""
    def update_plot(self, results: Dict[str, Any], params: Dict[str, Any]) -> List[Any]:
        self.ax.clear()
        
        # This logic is moved directly from your old PlottingWidget
        scale = params.get('rectangular_scale', 'dB')
        threshold_db = params.get('threshold_db', -90)
        angle_unit = params.get('angle_unit_rectangular', 'degrees')

        if scale == 'linear':
            af_data = np.abs(results.get('af')) if results.get('af') is not None else None
            y_label, y_max, y_min = translations.tr("array_factor_linear"), 1.1, 0
        else:
            af_data = results.get('af_db')
            y_label, y_max, y_min = translations.tr("array_factor_db"), 5, threshold_db - 5
            
        if af_data is None: self.clear_plot(); return []
        
        theta = results.get('theta_degrees') if angle_unit == 'degrees' else results.get('theta_radians')
        x_label = translations.tr("angle_theta_degrees") if angle_unit == 'degrees' else translations.tr("angle_theta_radians")
        
        line, = self.ax.plot(theta, np.maximum(af_data, y_min), 'b-', linewidth=2)
        
        self.ax.set_title(translations.tr("array_factor_vs_angle"))
        self.ax.set_xlabel(x_label); self.ax.set_ylabel(y_label)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.set_xlim(theta[0], theta[-1]); self.ax.set_ylim(y_min, y_max)
        self.figure.tight_layout()
        self.canvas.draw()
        
        return [line] # Return the plottable artist for interaction