import numpy as np
from enum import Enum
from .config import config
import AOT_biomaps.Settings
import matplotlib.pyplot as plt

class OpticFieldType(Enum):
    GAUSSIAN = "Gaussian"
    UNIFORM = "Uniform"
    SPHERICAL = "Spherical"

class Phantom:
    """
    Classe pour appliquer les absorbeurs à un champ laser dans le plan XZ.
    """
    class Laser:
        def __init__(self, params):
            self.x = np.arange(params.general['Xrange'][0], params.general['Xrange'][1], params.general['dx'])*1000
            self.z = np.arange(params.general['Zrange'][0], params.general['Zrange'][1], params.general['dz'])*1000
            try:
                self.shape = OpticFieldType(params.optic['laser']['shape'].capitalize())
            except ValueError:
                raise ValueError(f"Laser shape '{params.optic['laser']['shape']}' is not a valid OpticFieldType")

            self.center = params.optic['laser']['center']
            self.w0 = params.optic['laser']['w0']*1000
            self._set_intensity()
            if type(params)!= AOT_biomaps.Settings.Params:
                raise TypeError("params must be an instance of the Params class")
        
        def _set_intensity(self):
            if self.shape == OpticFieldType.GAUSSIAN:
                self.intensity = self._gaussian_beam()
            elif self.shape == OpticFieldType.UNIFORM:
                raise NotImplementedError("Uniform beam not implemented yet.")
            elif self.shape == OpticFieldType.SPHERICAL:
                raise NotImplementedError("Spherical beam not implemented yet.")
            else:
                raise ValueError("Unknown beam shape.")
        
        def _gaussian_beam(self):
            """
            Génère un faisceau laser gaussien dans le plan XZ.
            """
            if self.center == 'center':
                x0 = (self.x[0] + self.x[-1]) / 2
                z0 = (self.z[0] + self.z[-1]) / 2
            else:
                x0, z0 = self.center*1000
            X, Z = np.meshgrid(self.x, self.z, indexing='ij')
            return np.exp(-2 * ((X - x0)**2 + (Z - z0)**2) / self.w0**2)
        
    
    class Absorber:
        def __init__(self, name, type, center, radius, amplitude):
            self.name = name
            self.type = type
            self.center = center
            self.radius = radius
            self.amplitude = amplitude

        def __repr__(self):
            return f"Absorber(name={self.name}, type={self.type}, center={self.center}, radius={self.radius}, amplitude={self.amplitude})"

    def __init__(self, params):
    
        absorber_params = params.optic['absorbers']
        self.absorbers = [self.Absorber(**a) for a in absorber_params]

        self.laser = self.Laser(params)
        self.phantom = self._apply_absorbers()

    def _apply_absorbers(self):
        X, Z = np.meshgrid(self.laser.x, self.laser.z, indexing='ij')
        intensity = np.copy(self.laser.intensity)

        for absorber in self.absorbers:
            r2 = (X - absorber.center[0]*1000)**2 + (Z - absorber.center[1]*1000)**2
            absorption = -absorber.amplitude * np.exp(-r2 / (absorber.radius*1000)**2)
            intensity += absorption

        return np.clip(intensity, 0, None)
    
    def __str__(self):
        """
        Returns a string representation of the Phantom object, including its laser and absorber parameters.
        Formatted in a table-like structure.
        """
        # Attributs du laser
        laser_attrs = {
            'shape': self.laser.shape.name.capitalize(),
            'center': self.laser.center,
            'w0': self.laser.w0,
        }

        laser_attr_lines = [f"  {k}: {v}" for k, v in laser_attrs.items()]

        # Attributs des absorbeurs
        absorber_lines = []
        for absorber in self.absorbers:
            absorber_lines.append(f"  - name: \"{absorber.name}\"")
            absorber_lines.append(f"    type: \"{absorber.type}\"")
            absorber_lines.append(f"    center: {absorber.center}")
            absorber_lines.append(f"    radius: {absorber.radius}")
            absorber_lines.append(f"    amplitude: {absorber.amplitude}")

        # Définissez les bordures et titres
        border = "+" + "-" * 40 + "+"
        title = f"| Type : {self.__class__.__name__} |"
        laser_title = "| Laser Parameters |"
        absorber_title = "| Absorbers |"

        # Assemblez le résultat final
        result = f"{border}\n{title}\n{border}\n{laser_title}\n{border}\n"
        result += "\n".join(laser_attr_lines)
        result += f"\n{border}\n{absorber_title}\n{border}\n"
        result += "\n".join(absorber_lines)
        result += f"\n{border}"

        return result

    
    def plot_phantom(self):
        plt.imshow(self.phantom, extent=(self.laser.x[0], self.laser.x[-1]+1, self.laser.z[-1], self.laser.z[0]), aspect='auto',cmap='hot')
        plt.colorbar(label='Intensity')
        plt.xlabel('X (mm)',fontsize=20)
        plt.ylabel('Z (mm)',fontsize=20)
        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.title('Optical Phantom with Absorbers')
        plt.show()

    def plot_laser(self):
        plt.imshow(self.laser.intensity, extent=(self.laser.x[0], self.laser.x[-1]+1, self.laser.z[-1], self.laser.z[0]), aspect='auto',cmap='hot')
        plt.colorbar(label='Intensity')
        plt.xlabel('X (mm)',fontsize=20)
        plt.ylabel('Z (mm)',fontsize=20)
        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.title('Laser Intensity Distribution')
        plt.show()
    
