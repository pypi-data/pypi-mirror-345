import scipy.io
import numpy as np
import h5py
from scipy.signal import hilbert
from math import ceil, floor
import os
from kwave.kgrid import kWaveGrid
from kwave.kmedium import kWaveMedium
from kwave.ksource import kSource
from kwave.ksensor import kSensor
from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
from kwave.kspaceFirstOrder2D import kspaceFirstOrder2D
from kwave.utils.signals import tone_burst
from kwave.options.simulation_options import SimulationOptions
from kwave.options.simulation_execution_options import SimulationExecutionOptions
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
from tempfile import gettempdir
from .config import config
import AOT_biomaps.Settings

if config.get_process()  == 'gpu':
    import cupy as cp
    from cupyx.scipy.signal import hilbert as cp_hilbert
else:
    import numpy as cp
    from scipy.signal import hilbert as cp_hilbert

from abc import ABC, abstractmethod
from enum import Enum

class TypeSim(Enum):
    """
    Enum for the type of simulation to be performed.
    - KWAVE: k-Wave simulation
    - FIELD2: Field2 simulation
    - HYDRO: Hydrophone acquisition
    """
    KWAVE = 'k-wave'
    HYDRO = 'Hydrophone'
    FIELD2 = 'Field2'

class Dim(Enum):
    """
    Enum for the dimension of the acoustic field.
    - D2: 2D field
    - D3: 3D field
    """
    D2 = '2D'
    D3 = '3D'

class FormatSave(Enum):
    """
    Enum for different file formats to save the acoustic field.
    selection of file formats:
    - HDR_IMG: Interfile format (.hdr and .img)
    - H5: HDF5 format (.h5)
    - NPY: NumPy format (.npy)
    """
    HDR_IMG = 'hdr_img'
    H5 = 'h5'
    NPY = 'npy'

class WaveType(Enum):
    FocusedWave = 'focus'
    StructuredWave = 'structured'   
    PlaneWave = 'plane'

####### ABSTRACT CLASS #######

class AcousticField(ABC):
    """
    Abstract class to generate and manipulate acoustic fields for ultrasound imaging.
    Provides methods to initialize parameters, generate fields, save and load data, and calculate envelopes.\n
    Principal paramaters :
    - field: Acoustic field data.
    - enveloppe: Analytic envelope squared of the acoustic field.
    - burst: Burst signal used for generating the field for each piezo elements.
    - delayedSignal: Delayed burst signal for each piezo element.
    - medium: Medium properties for k-Wave simulation. Because field2 and Hydrophone simulation are not implemented yet, this attribute is set to None for these types of simulation.
    """
    def __init__(self, params):
        """
        Initialize global properties of the AcousticField object.

        Parameters:
        - typeSim (TypeSim): Type of simulation to be performed. Options include KWAVE, FIELD2, and HYDRO. Default is TypeSim.KWAVE.
        - dim (Dim): Dimension of the acoustic field. Can be 2D or 3D. Default is Dim.D2.
        - c0 (float): Speed of sound in the medium, specified in meters per second (m/s). Default is 1540 m/s.
        - f_US (float): Frequency of the ultrasound signal, specified in Hertz (Hz). Default is 6 MHz.
        - f_AQ (float): Frequency of data acquisition, specified in Hertz (Hz). Default is 180 MHz.
        - f_saving (float): Frequency at which the acoustic field data is saved, specified in Hertz (Hz). Default is 10 MHz.
        - num_cycles (int): Number of cycles in the burst signal. Default is 4 cycles.
        - num_elements (int): Number of elements in the transducer array. Default is 192 elements.
        - element_width (float): Width of each transducer element, specified in meters (m). Default is 0.2 mm.
        - element_height (float): Height of each transducer element, specified in meters (m). Default is 6 mm.
        - Xrange (list of float): Range of X coordinates for the acoustic field, specified in meters (m). Default is from -20 mm to 20 mm.
        - Yrange (list of float, optional): Range of Y coordinates for the acoustic field, specified in meters (m). Default is None, indicating no specific Y range.
        - Zrange (list of float): Range of Z coordinates for the acoustic field, specified in meters (m). Default is from 0 m to 37 mm.
        """
        required_keys = [
            'c0', 'f_US', 'f_AQ', 'f_saving', 'num_cycles', 'num_elements',
            'element_width', 'element_height', 'Xrange', 'Zrange', 'dim',
            'typeSim', 'dx', 'dz'
        ]

        # Vérification des clés requises
        for key in required_keys:
            if key not in params.acoustic and key not in params.general:
                raise ValueError(f"{key} must be provided in the parameters.")
            
        self.params = {
            'c0': params.acoustic['c0'],
            'f_US': int(float(params.acoustic['f_US'])),
            'f_AQ': int(float(params.acoustic['f_AQ'])),
            'f_saving': int(float(params.acoustic['f_saving'])),
            'num_cycles': params.acoustic['num_cycles'],
            'num_elements': params.acoustic['num_elements'],
            'element_width': params.acoustic['element_width'],
            'element_height': params.acoustic['element_height'],
            'Xrange': params.general['Xrange'],
            'Yrange': params.general['Yrange'],
            'Zrange': params.general['Zrange'],
            'dim': params.acoustic['dim'],
            'typeSim': params.acoustic['typeSim'],
            'dx': params.general['dx'],
            'dy': params.general['dy'] if params.general['Yrange'] is not None else None,
            'dz': params.general['dz'],
            'Nx': int(np.round((params.general['Xrange'][1] - params.general['Xrange'][0])/params.general['dx'])),
            'Ny': int(np.round((params.general['Yrange'][1] - params.general['Yrange'][0])/params.general['dy']))  if params.general['Yrange'] is not None else 1,
            'Nz': int(np.round((params.general['Zrange'][1] - params.general['Zrange'][0])/params.general['dz'])),
            'probeWidth': params.acoustic['num_elements'] * params.acoustic['element_width'],
        }


        self.field = None
        self.enveloppe = None
        self.burst = self.__generate_burst_signal()
        if self.params["typeSim"] == TypeSim.FIELD2.value or self.params["typeSim"] == TypeSim.HYDRO.value:
            self.medium = None
        elif self.params["typeSim"] == TypeSim.KWAVE.value:
            self.medium = kWaveMedium(sound_speed=self.params['c0'])
        
        if self.params["dim"] == Dim.D3 and self.params["Yrange"] is None:
            raise ValueError("Yrange must be provided for 3D fields.")
        
        if type(params)!= AOT_biomaps.Settings.Params:
            raise TypeError("params must be an instance of the Params class")

    def __str__(self):
        """
        Returns a string representation of the AcousticField object, including its parameters and attributes.
        The string is formatted in a table-like structure for better readability.
        """
        # Obtenez tous les attributs de l'instance
        attrs = {**self.params, **{k: v for k, v in vars(self).items() if k not in self.params}}

        # Attributs de base de AcousticField
        base_attrs_keys = ['c0', 'f_US', 'f_AQ', 'f_saving', 'num_cycles', 'num_elements',
                        'element_width', 'element_height',
                        'Xrange', 'Yrange', 'Zrange', 'dim', 'typeSim', 'Nx', 'Ny', 'Nz',
                        'dx', 'dy', 'dz', 'probeWidth']
        base_attrs = {key: value for key, value in attrs.items() if key in base_attrs_keys}

        # Attributs spécifiques à la classe dérivée
        derived_attrs = {key: value for key, value in attrs.items() if key not in base_attrs_keys}

        # Créez des lignes pour les attributs de base et dérivés
        base_attr_lines = [f"  {key}: {value}" for key, value in base_attrs.items()]


        derived_attr_lines = []
        for key, value in derived_attrs.items():
            if key in {'burst', 'delayedSignal'}:
                continue
            elif key == 'pattern':
                # Inspecte l'objet pattern
                try:
                    pattern_attrs = vars(value)
                    pattern_str = ", ".join([f"{k}={v}" for k, v in pattern_attrs.items()])
                    derived_attr_lines.append(f"  pattern: {{{pattern_str}}}")
                except Exception as e:
                    derived_attr_lines.append(f"  pattern: <unreadable: {e}>")
            else:
                try:
                    derived_attr_lines.append(f"  {key}: {value}")
                except Exception as e:
                    derived_attr_lines.append(f"  {key}: <unprintable: {e}>")

        # Ajoutez les shapes pour burst et delayedSignal
        if 'burst' in derived_attrs:
            derived_attr_lines.append(f"  burst: shape={self.burst.shape}")
        if 'delayedSignal' in derived_attrs:
            derived_attr_lines.append(f"  delayedSignal: shape={self.delayedSignal.shape}")

        # Définissez les bordures et titres
        border = "+" + "-" * 40 + "+"
        title = f"|Type : {self.__class__.__name__} wave |"
        base_title = "| AcousticField Attributes |"
        derived_title = f"| {self.__class__.__name__} Specific Attributes |" if derived_attrs else ""

        # Convertissez les attributs en chaînes de caractères
        base_attr_str = "\n".join(base_attr_lines)
        derived_attr_str = "\n".join(derived_attr_lines)

        # Assemblez le résultat final
        result = f"{border}\n{title}\n{border}\n{base_title}\n{border}\n{base_attr_str}\n"
        if derived_attrs:
            result += f"\n{border}\n{derived_title}\n{border}\n{derived_attr_str}\n"
        result += border

        return result

    def __del__(self):
        """
        Destructor for the AcousticField class. Cleans up the field and envelope attributes.
        """
        self.field = None
        self.enveloppe = None
        self.burst = None
        self.delayedSignal = None
        if config.get_process() == 'gpu':
            cp.cuda.Device(config.bestGPU).synchronize()

    ## TOOLS METHODS ##

    def generate_field(self):
        """
        Generate the acoustic field based on the specified simulation type and parameters.
        """
   
        if self.params["typeSim"] == TypeSim.FIELD2.value:
            raise NotImplementedError("FIELD2 simulation is not implemented yet.")
        elif self.params["typeSim"] == TypeSim.KWAVE.value:
            if self.params["dim"] == Dim.D2.value:
                self.field = self._generate_2Dacoustic_field_KWAVE()
            elif self.params["dim"] == Dim.D3.value:
                self.field = self._generate_3Dacoustic_field_KWAVE()
        elif self.params["typeSim"] == TypeSim.HYDRO.value:
            raise ValueError("Cannot generate field for Hydrophone simulation, load exciting acquisitions.")
        else:
            raise ValueError("Invalid simulation type. Supported types are: FIELD2, KWAVE, HYDRO.")  

    def calculate_envelope_squared(self):
        """
        Calculate the analytic envelope of the acoustic field.

        Parameters:
        - acoustic_field (numpy.ndarray or cupy.ndarray): Input acoustic field data. This should be a time-domain signal.

        Returns:
        - envelope (numpy.ndarray or cupy.ndarray): The squared analytic envelope of the acoustic field.
        """
        if self.field is None:
            raise ValueError("Acoustic field is not generated. Please generate the field first.")
        acoustic_field_gpu = cp.asarray(self.field)

        if len(acoustic_field_gpu.shape) not in [3, 4]:
            raise ValueError("Input acoustic field must be a 3D or 4D array.")

        if len(acoustic_field_gpu.shape) == 3:
            envelope_gpu = cp.abs(cp_hilbert(acoustic_field_gpu, axis=0))**2
        elif len(acoustic_field_gpu.shape) == 4:
            EnveloppeField = cp.zeros_like(acoustic_field_gpu)
            for y in range(acoustic_field_gpu.shape[2]):
                for z in range(acoustic_field_gpu.shape[1]):
                    EnveloppeField[:, z, y, :] = cp.abs(cp_hilbert(acoustic_field_gpu[:, z, y, :], axis=1))**2
            envelope_gpu = EnveloppeField

        # Convert the result back to a NumPy array
        if config.get_process() == 'gpu':
            self.enveloppe = cp.asnumpy(envelope_gpu)
        else:
            self.enveloppe = envelope_gpu

    def save_field(self, filePath,formatSave):
        if formatSave == FormatSave.HDR_IMG:
            self.__save2D_HDR_IMG(self, filePath)
        elif formatSave == FormatSave.H5:
            self.__save2D_H5(self, filePath)
        elif formatSave == FormatSave.NPY:
            self.__save2D_NPY(self, filePath)
        else:   
            raise ValueError("Unsupported format. Supported formats are: HDR_IMG, H5, NPY.")
    
    def load_field(self, filePath, formatSave):
        if self.typeSim == TypeSim.FIELD2:
            raise NotImplementedError("FIELD2 simulation is not implemented yet.")
        elif self.typeSim == TypeSim.KWAVE:
            if formatSave == FormatSave.HDR_IMG:
                if self.dim == Dim.D2:
                    self.field = self._load_fieldKWAVE_XZ(filePath)
                elif self.dim == Dim.D3:
                    raise NotImplementedError("3D KWAVE field loading is not implemented yet.")
            elif formatSave == FormatSave.H5:
                if self.dim == Dim.D2:
                    raise NotImplementedError("H5 KWAVE field loading is not implemented yet.")
                elif self.dim == Dim.D3:
                    raise NotImplementedError("H5 KWAVE field loading is not implemented yet.")
            elif formatSave == FormatSave.NPY:
                if self.dim == Dim.D2:
                    self.field = np.load(filePath)
                elif self.dim == Dim.D3:
                    raise NotImplementedError("3D NPY KWAVE field loading is not implemented yet.")
        elif self.typeSim == TypeSim.HYDRO:
            if formatSave == FormatSave.HDR_IMG:
                raise ValueError("HDR_IMG format is not supported for Hydrophone acquisition.")
            if formatSave == FormatSave.H5:
                if self.dim == Dim.D2:
                    self.field, self.params['Yrange'], self.params['Zrange'] = self._load_fieldHYDRO_YZ(filePath, filePath.replace('.h5', '.mat'))
                elif self.dim == Dim.D3:
                    self.field, self.params['Xrange'], self.params['Yrange'], self.params['Zrange'] = self._load_fieldHYDRO_XYZ(filePath, filePath.replace('.h5', '.mat'))
            elif formatSave == FormatSave.NPY:
                if self.dim == Dim.D2:
                    self.field = np.load(filePath)
                elif self.dim == Dim.D3:
                    raise NotImplementedError("3D NPY Hydrophone field loading is not implemented yet.")
        else:
            raise ValueError("Invalid simulation type. Supported types are: FIELD2, KWAVE, HYDRO.")

    ## DISPAY METHODS ##

    def plot_burst_signal(self):
        time2plot = np.arange(0, len(self.burst)) / self.params['f_AQ']*1000000  # Convert to microseconds
        plt.figure(figsize=(8, 8))
        plt.plot(time2plot,self.burst)
        plt.title('Excitation burst signal')
        plt.xlabel('Time (µs)')
        plt.ylabel('Amplitude')
        plt.grid()
        plt.show()

    @abstractmethod
    def animated_plot_AcousticField(self, filePath=None, **kwargs):
        """
        Plot the A matrix as an animation.
        Parameters:
        - filePath (str): Path to save the animation. If None, display the animation.
        - **kwargs: Additional arguments for customization.
        Returns:
            ani: Matplotlib FuncAnimation object
            """
        pass

    ## PRIVATE METHODS ##

    def __generate_burst_signal(self):
        """
        Private method to generate a burst signal based on the specified parameters.
        """
        return tone_burst(self.params["f_AQ"], self.params["f_US"], self.params["num_cycles"]).squeeze()
    
    @abstractmethod
    def _generate_2Dacoustic_field_KWAVE(self):
        """
        Generate a 2D acoustic field using k-Wave simulation.\n
        Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _generate_3Dacoustic_field_KWAVE(self):
        """
        Generate a 3D acoustic field using k-Wave simulation.\n
        Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _save2D_HDR_IMG(self, filePath):
        pass

    def _save2D_H5(self, filePath):
        with h5py.File(filePath, 'w') as f:
            for key, value in self.__dict__.items():
                if key != 'field':
                    f.create_dataset(key, data=value)
            f.create_dataset('data', data=self.field, compression='gzip')

    def _save2D_NPY(self, filePath):
        np.save(filePath, self.field)

    def _load_fieldHYDRO_XZ(file_path_h5, param_path_mat):    

        # Charger les fichiers .mat
        param = scipy.io.loadmat(param_path_mat)

        # Charger les paramètres
        x_test = param['x'].flatten()
        z_test = param['z'].flatten()

        x_range = np.arange(-23,21.2,0.2)
        z_range = np.arange(0,37.2,0.2)
        X, Z = np.meshgrid(x_range, z_range)

        # Charger le fichier .h5
        with h5py.File(file_path_h5, 'r') as file:
            data = file['data'][:]

        # Initialiser une matrice pour stocker les données acoustiques
        acoustic_field = np.zeros((len(z_range), len(x_range), data.shape[1]))

        # Remplir la grille avec les données acoustiques
        index = 0
        for i in range(len(z_range)):
            if i % 2 == 0:
                # Parcours de gauche à droite
                for j in range(len(x_range)):
                    acoustic_field[i, j, :] = data[index]
                    index += 1
            else:
                # Parcours de droite à gauche
                for j in range(len(x_range) - 1, -1, -1):
                    acoustic_field[i, j, :] = data[index]
                    index += 1

        # Calculer l'enveloppe analytique
        envelope = np.abs(hilbert(acoustic_field, axis=2))
        # Réorganiser le tableau pour avoir la forme (Times, Z, X)
        envelope_transposed = np.transpose(envelope, (2, 0, 1))
        return envelope_transposed

    def _load_fieldKWAVE_XZ(hdr_path):
        """
        Lit un fichier Interfile (.hdr) et son fichier binaire (.img) pour reconstruire un champ acoustique.

        Paramètres :
        ------------
        - folderPathBase : dossier de base contenant les fichiers
        - hdr_path : chemin relatif du fichier .hdr depuis folderPathBase

        Retour :
        --------
        - field : tableau NumPy contenant le champ acoustique avec les dimensions réordonnées en (X, Z, time)
        - header : dictionnaire contenant les métadonnées du fichier .hdr
        """
        header = {}
        # Lecture du fichier .hdr
        with open(hdr_path, 'r') as f:
            for line in f:
                if ':=' in line:
                    key, value = line.split(':=', 1)
                    key = key.strip().lower().replace('!', '')
                    value = value.strip()
                    header[key] = value


        # Récupère le nom du fichier .img associé
        data_file = header.get('name of data file') or header.get('name of date file')
        if data_file is None:
            raise ValueError(f"Impossible de trouver le fichier de données associé au fichier header {hdr_path}")
        img_path = os.path.join(os.path.dirname(hdr_path),os.path.basename(data_file))

        # Détermine la taille du champ à partir des métadonnées
        shape = [int(header[f'matrix size [{i}]']) for i in range(1, 3) if f'matrix size [{i}]' in header]
        if not shape:
            raise ValueError("Impossible de déterminer la forme du champ acoustique à partir des métadonnées.")

        # Type de données
        data_type = header.get('number format', 'short float').lower()
        dtype_map = {
            'short float': np.float32,
            'float': np.float32,
            'int16': np.int16,
            'int32': np.int32,
            'uint16': np.uint16,
            'uint8': np.uint8
        }
        dtype = dtype_map.get(data_type)
        if dtype is None:
            raise ValueError(f"Type de données non pris en charge : {data_type}")

        # Ordre des octets (endianness)
        byte_order = header.get('imagedata byte order', 'LITTLEENDIAN').lower()
        endianess = '<' if 'little' in byte_order else '>'

        # Vérifie la taille réelle du fichier .img
        fileSize = os.path.getsize(img_path)
        timeDim = int(fileSize / (np.dtype(dtype).itemsize *np.prod(shape)))
            # if img_size != expected_size:
        #     raise ValueError(f"La taille du fichier img ({img_size} octets) ne correspond pas à la taille attendue ({expected_size} octets).")
        shape = shape + [timeDim]
        # Lecture des données binaires
        with open(img_path, 'rb') as f:
            data = np.fromfile(f, dtype=endianess + np.dtype(dtype).char)

        # Reshape les données en (time, Z, X)
        field = data.reshape(shape[::-1])  # NumPy interprète dans l'ordre C (inverse de MATLAB)



        # Applique les facteurs d'échelle si disponibles
        rescale_slope = float(header.get('data rescale slope', 1))
        rescale_offset = float(header.get('data rescale offset', 0))
        field = field * rescale_slope + rescale_offset

        return field
    
    def _load_fieldHYDRO_YZ(file_path_h5, param_path_mat):
        # Load parameters from the .mat file
        param = scipy.io.loadmat(param_path_mat)

        # Extract the ranges for y and z
        y_range = param['y'].flatten()
        z_range = param['z'].flatten()

        # Load the data from the .h5 file
        with h5py.File(file_path_h5, 'r') as file:
            data = file['data'][:]

        # Calculate the number of scans
        Ny = len(y_range)
        Nz = len(z_range)
        Nscans = Ny * Nz

        # Create the scan positions
        positions_y = []
        positions_z = []

        for i in range(Nz):
            if i % 2 == 0:
                # Traverse top to bottom for even rows
                positions_y.extend(y_range)
            else:
                # Traverse bottom to top for odd rows
                positions_y.extend(y_range[::-1])
            positions_z.extend([z_range[i]] * Ny)

        Positions = np.column_stack((positions_y, positions_z))

        # Initialize a matrix to store the reorganized data
        reorganized_data = np.zeros((Ny, Nz, data.shape[1]))

        # Reorganize the data according to the scan positions
        for index, (j, k) in enumerate(Positions):
            y_idx = np.where(y_range == j)[0][0]
            z_idx = np.where(z_range == k)[0][0]
            reorganized_data[y_idx, z_idx, :] = data[index, :]

        # Calculer l'enveloppe analytique
        envelope = np.abs(hilbert(reorganized_data, axis=2))
        # Réorganiser le tableau pour avoir la forme (Times, Z, Y)
        envelope_transposed = np.transpose(envelope, (2, 0, 1))
        return envelope_transposed, y_range, z_range

    def _load_fieldHYDRO_XYZ(file_path_h5, param_path_mat):
        # Load parameters from the .mat file
        param = scipy.io.loadmat(param_path_mat)

        # Extract the ranges for x, y, and z
        x_range = param['x'].flatten()
        y_range = param['y'].flatten()
        z_range = param['z'].flatten()

        # Create a meshgrid for x, y, and z
        X, Y, Z = np.meshgrid(x_range, y_range, z_range, indexing='ij')

        # Load the data from the .h5 file
        with h5py.File(file_path_h5, 'r') as file:
            data = file['data'][:]

        # Calculate the number of scans
        Nx = len(x_range)
        Ny = len(y_range)
        Nz = len(z_range)
        Nscans = Nx * Ny * Nz

        # Create the scan positions
        if Ny % 2 == 0:
            X = np.tile(np.concatenate([x_range[:, np.newaxis], x_range[::-1, np.newaxis]]), (Ny // 2, 1))
            Y = np.repeat(y_range, Nx)
        else:
            X = np.concatenate([x_range[:, np.newaxis], np.tile(np.concatenate([x_range[::-1, np.newaxis], x_range[:, np.newaxis]]), ((Ny - 1) // 2, 1))])
            Y = np.repeat(y_range, Nx)

        XY = np.column_stack((X.flatten(), Y))

        if Nz % 2 == 0:
            XYZ = np.tile(np.concatenate([XY, np.flipud(XY)]), (Nz // 2, 1))
            Z = np.repeat(z_range, Nx * Ny)
        else:
            XYZ = np.concatenate([XY, np.tile(np.concatenate([np.flipud(XY), XY]), ((Nz - 1) // 2, 1))])
            Z = np.repeat(z_range, Nx * Ny)

        Positions = np.column_stack((XYZ, Z))

        # Initialize a matrix to store the reorganized data
        reorganized_data = np.zeros((Nx, Ny, Nz, data.shape[1]))

        # Reorganize the data according to the scan positions
        for index, (i, j, k) in enumerate(Positions):
            x_idx = np.where(x_range == i)[0][0]
            y_idx = np.where(y_range == j)[0][0]
            z_idx = np.where(z_range == k)[0][0]
            reorganized_data[x_idx, y_idx, z_idx, :] = data[index, :]
        
        EnveloppeField = np.zeros_like(reorganized_data)

        for y in range(reorganized_data.shape[1]):
            for z in range(reorganized_data.shape[2]):
                EnveloppeField[:, y, z, :] = np.abs(hilbert(reorganized_data[:, y, z, :], axis=1))

        return EnveloppeField.T, x_range, y_range, z_range

####### SUBCLASS #######

class StructuredWave(AcousticField):

    class PatternParams:
        def __init__(self,space_0, space_1, move_head_0_2tail, move_tail_1_2head):
            self.space_0 = space_0
            self.space_1 = space_1
            self.move_head_0_2tail = move_head_0_2tail
            self.move_tail_1_2head = move_tail_1_2head
            self.activeList = None
            self.len_hex = None

        def __str__(self):
            pass

        def generate_pattern(self):
                """Generate binary pattern and return hex string."""
                total_bits = self.len_hex * 4
                unit = "0" * self.space_0 + "1" * self.space_1
                repeat_time = (total_bits + len(unit) - 1) // len(unit)
                pattern = (unit * repeat_time)[:total_bits]

                # Move 0s from head to tail
                if self.move_head_0_2tail > 0:
                    head_zeros = '0' * self.move_head_0_2tail
                    pattern = pattern[self.move_head_0_2tail:] + head_zeros

                # Move 1s from tail to head
                if self.move_tail_1_2head > 0:
                    tail_ones = '1' * self.move_tail_1_2head
                    pattern = tail_ones + pattern[:-self.move_tail_1_2head]

                # Convert to hex
                hex_output = hex(int(pattern, 2))[2:]
                hex_output = hex_output.zfill(self.len_hex)

                return hex_output

        def to_string(self):
            """Format the pattern parameters into a string like '0_48_0_0'."""
            return f"{self.space_0}_{self.space_1}_{self.move_head_0_2tail}_{self.move_tail_1_2head}"

        def describe(self):
            """Return a readable description."""
            return f"Pattern structure: {self.to_string()}"
               
    def __init__(self,angle_deg, space_0, space_1, move_head_0_2tail, move_tail_1_2head, **kwargs):
        """
        Initialize the StructuredWave object.
        angle _deg: Angle in degrees.
        active_list: Active list string in hexadecimal format. MUST BE THE LENGTH OF NUMBER OF ELEMENTS / 4.
        """
        super().__init__(**kwargs)
        self.waveType = WaveType.StructuredWave
        self.pattern = self.PatternParams(space_0, space_1, move_head_0_2tail, move_tail_1_2head)
        self.pattern.len_hex = self.params['num_elements'] // 4
        self.pattern.activeList = self.pattern.generate_pattern()
        self.params['angle'] = angle_deg
        self.params['t0'] = floor(self.params["Zrange"][0] / self.params["f_AQ"])
        self.params['tmax'] = ceil((self.params["Zrange"][1] - self.params["Zrange"][0] + self.params["probeWidth"] * np.tan(np.radians(abs(angle_deg)))) * self.params["f_AQ"] / self.params["c0"])
        self.params['Nt'] = round(1.20 * (self.params['tmax'] - self.params['t0']))
        
        self.params['t0'] = int(self.params['t0'] * self.params['f_AQ'])

        if self.params["angle"] < -20 or self.params["angle"] > 20:
            raise ValueError("Angle must be between -20 and 20 degrees.")
       

        print(len(self.pattern.activeList))
        print(self.params["num_elements"]//4)
        if len(self.pattern.activeList) != self.params["num_elements"]//4:
            raise ValueError(f"Active list string must be {self.params["num_elements"]//4} characters long.")

        self.delayedSignal = self._apply_delay()
    
    def get_path(self):
        """Generate the list of system matrix .hdr file paths for this wave."""
        pattern_str = self.pattern.activeList
        angle_str = self._format_angle(self.params['angle'])
        return f"field_{pattern_str}_{angle_str}.hdr"
        
    ## PRIVATE METHODS ##
        
    def _format_angle(self, angle):
        """Format an angle into 3-digit code like '120' for -20°, '020' for +20°."""
        return f"{'1' if angle < 0 else '0'}{abs(angle):02d}"
    
    def _apply_delay(self):
        """
        Applique un retard temporel au signal pour chaque élément du transducteur.

        Args:
            signal (ndarray): Le signal acoustique initial.
            num_elements (int): Nombre total d'éléments.
            element_width (float): Largeur de chaque élément du transducteur.
            c0 (float): Vitesse du son dans le milieu (m/s).
            angle_rad (float): Angle d'inclinaison en radians.
            kgrid_dt (float): Pas de temps du kgrid.
            is_positive (bool): Indique si l'angle est positif ou négatif.

        Returns:
            ndarray: Tableau des signaux retardés.
        """
        is_positive = self.params['angle'] >= 0
        delays = np.zeros(self.params['num_elements'])

        for i in range(self.params['num_elements']):
            delays[i] = (i * self.params['element_width'] * np.tan(np.deg2rad(abs(self.params['angle'] )))) / self.params['c0']  # Retard en secondes


        delay_samples = np.round(delays *self.params['f_AQ']).astype(int)
        max_delay = np.max(np.abs(delay_samples))
        
        delayed_signals = np.zeros((self.params['num_elements'], len(self.burst) + max_delay))
        for i in range(self.params['num_elements']):
            shift = delay_samples[i]

            if is_positive:
                delayed_signals[i, shift:shift + len(self.burst)] = self.burst  # Décalage à droite
            else:
                delayed_signals[i, max_delay - shift:max_delay - shift + len(self.burst)] =self.burst  # Décalage à gauche

        return delayed_signals
    
    def _save2D_HDR_IMG(self, pathFolder):

        t_ex = 1/self.params['f_US']
        angle_sign = '1' if self.params['angle'] < 0 else '0'
        formatted_angle = f"{angle_sign}{abs(self.params['angle']):02d}"

        # 4. Définir les noms de fichiers (img et hdr)
        file_name = f"field_{self.pattern.activeList}_{formatted_angle}"

        img_path = os.path.join(pathFolder , file_name + ".img")
        hdr_path = os.path.join(pathFolder , file_name + ".hdr")
        

        # === 3. Sauvegarder le champ acoustique dans le fichier .img ===
        with open(img_path, "wb") as f_img:
            self.field.astype('float32').tofile(f_img)  # Sauvegarde au format float32 (équivalent à "single" en MATLAB)

        # **Génération du headerFieldGlob**
        headerFieldGlob = (
            f"!INTERFILE :=\n"
            f"modality : AOT\n"
            f"voxels number transaxial: {self.field.shape[2]}\n"
            f"voxels number transaxial 2: {self.field.shape[1]}\n"
            f"voxels number axial: {1}\n"
            f"field of view transaxial: {(self.params['Xrange'][1] - self.params['Xrange'][0]) * 1000}\n"
            f"field of view transaxial 2: {(self.params['Zrange'][1] - self.params['Zrange'][0]) * 1000}\n"
            f"field of view axial: {1}\n"
        )

        # **Génération du header**
        header = (
            f"!INTERFILE :=\n"
            f"!imaging modality := AOT\n\n"
            f"!GENERAL DATA :=\n"
            f"!data offset in bytes := 0\n"
            f"!name of data file := system_matrix/{file_name}.img\n\n"
            f"!GENERAL IMAGE DATA\n"
            f"!total number of images := {self.field.shape[0]}\n"
            f"imagedata byte order := LITTLEENDIAN\n"
            f"!number of frame groups := 1\n\n"
            f"!STATIC STUDY (General) :=\n"
            f"number of dimensions := 3\n"
            f"!matrix size [1] := {self.field.shape[2]}\n"
            f"!matrix size [2] := {self.field.shape[1]}\n"
            f"!matrix size [3] := {self.field.shape[0]}\n"
            f"!number format := short float\n"
            f"!number of bytes per pixel := 4\n"
            f"scaling factor (mm/pixel) [1] := {self.params['dx'] * 1000}\n"
            f"scaling factor (mm/pixel) [2] := {self.params['dx'] * 1000}\n"
            f"scaling factor (s/pixel) [3] := {1/self.params['f_AQ']}\n"
            f"first pixel offset (mm) [1] := {self.params['Xrange'][0] * 1e3}\n"
            f"first pixel offset (mm) [2] := {self.params['Zrange'][0] * 1e3}\n"
            f"first pixel offset (s) [3] := 0\n"
            f"data rescale offset := 0\n"
            f"data rescale slope := 1\n"
            f"quantification units := 1\n\n"
            f"!SPECIFIC PARAMETERS :=\n"
            f"angle (degree) := {self.params['angle']}\n"
            f"activation list := {''.join(f"{int(self.pattern.activeList[i:i+2], 16):08b}" for i in range(0, len(self.pattern.activeList), 2))}\n"
            f"number of US transducers := {self.params['num_elements']}\n"
            f"delay (s) := 0\n"
            f"us frequency (Hz) := {self.params['f_US']}\n"
            f"excitation duration (s) := {t_ex}\n"
            f"!END OF INTERFILE :=\n"
        )
        # === 5. Sauvegarder le fichier .hdr ===
        with open(hdr_path, "w") as f_hdr:
            f_hdr.write(header)

        with open(os.path.join(pathFolder,"field.hdr"), "w") as f_hdr2:
            f_hdr2.write(headerFieldGlob)
        
    def _generate_2Dacoustic_field_KWAVE(self):
    
        active_list = np.array([int(char) for char in ''.join(f"{int(self.pattern.activeList[i:i+2], 16):08b}" for i in range(0, len(self.pattern.activeList), 2))])

        kgrid = kWaveGrid([self.params["Nx"], self.params["Nz"]], [self.params["dx"], self.params["dz"]])
        kgrid.setTime(Nt = self.params['Nt'], dt = 1/self.params['f_AQ'])
        
        # Masque de la sonde : alignée dans le plan XZ
        source = kSource()
        source.p_mask = np.zeros((self.params['Nx'], self.params['Nz']))  # Crée une grille vide pour le masque de la source
        print(source.p_mask.shape)
        # Placement des transducteurs actifs dans le masque
        for i in range(self.params['num_elements']):
            if active_list[i] == 1:  # Vérifiez si l'élément est actif
                x_pos = i  # Position des éléments sur l'axe X
                source.p_mask[x_pos, 0] = 1  # Position dans le plan XZ

        source.p_mask = source.p_mask.astype(int)  
        source.p = self.delayedSignal[active_list == 1, :]

        # === Définir les capteurs pour observer les champs acoustiques ===
        sensor = kSensor()
        sensor.mask = np.ones((self.params['Nx'], self.params['Nz']))  # Capteur couvrant tout le domaine
        
        # === Options de simulation ===
        simulation_options = SimulationOptions(
            pml_inside=False,  # Empêche le PML d'être ajouté à l'intérieur de la grille
            pml_x_size=20,      # Taille de la PML sur l'axe X
            pml_z_size=20,       # Taille de la PML sur l'axe Z    
            use_sg= False,
            save_to_disk = True,
            input_filename=os.path.join(gettempdir(),"KwaveIN.h5"),
            output_filename= os.path.join(gettempdir(),"KwaveOUT.h5"))

       
        execution_options = SimulationExecutionOptions(
            is_gpu_simulation = config.get_process() == 'gpu',
            device_num = config.bestGPU() if config.get_process() == 'gpu' else None)
        
        # === Lancer la simulation ===
        print("Lancement de la simulation...")
        sensor_data = kspaceFirstOrder2D(
            kgrid=kgrid,
            medium=self.medium,
            source=source,
            sensor=sensor,
            simulation_options=simulation_options,
            execution_options=execution_options,
        )
        print("Simulation terminée avec succès.")

        return sensor_data['p'].reshape(kgrid.Nt,self.params['Nz'], self.params['Nx'])
    
    def _generate_3Dacoustic_field_KWAVE(self):

        active_list = np.array([int(char) for char in ''.join(f"{int(self.pattern.activeList[i:i+2], 16):08b}" for i in range(0, len(self.pattern.activeList), 2))])
        
        # Initialisation de la grille et du milieu
        kgrid = kWaveGrid([self.params['Nx'], self.params['Ny'], self.params['Nz']], [self.params['dx'], self.params['dy'], self.params['dz']])
        kgrid.setTime(Nt=self.params['Nt'], dt=1/self.params['f_AQ'])

        # Masque de la sonde : alignée dans le plan XZ
        source = kSource()
        source.p_mask = np.zeros((self.params['Nx'], self.params['Ny'], self.params['Nz']))  # Crée une grille vide pour le masque de la source

        stringList = ''.join(map(str, active_list))
        print(stringList)
    
        # Placement des transducteurs actifs dans le masque
        for i in range(self.params['num_elements']):
            if active_list[i] == 1:  # Vérifiez si l'élément est actif
                x_pos = i+self.params['Nx']//2 - self.params['num_elements']//2 # Position des éléments sur l'axe X
                source.p_mask[x_pos, self.params['Ny'] // 2, 0] = 1  # Position dans le plan XZ

        source.p_mask = source.p_mask.astype(int)  
        source.p = self.delayedSignal[active_list == 1, :]

        # === Définir les capteurs pour observer les champs acoustiques ===
        sensor = kSensor()
        sensor.mask = np.ones((self.params['Nx'], self.params['Ny'], self.params['Nz']))  # Capteur couvrant tout le domaine

        # === Options de simulation ===
        simulation_options = SimulationOptions(
            pml_inside=False,  # Empêche le PML d'être ajouté à l'intérieur de la grille
            pml_auto = True, 
            use_sg= False, 
            save_to_disk = True,
            input_filename=os.path.join(gettempdir(),"KwaveIN.h5"),
            output_filename= os.path.join(gettempdir(),"KwaveOUT.h5"))
        
        execution_options = SimulationExecutionOptions(
            is_gpu_simulation = config.get_process() == 'gpu',
            device_num = config.bestGPU() if config.get_process() == 'gpu' else None)

        # === Lancer la simulation ===
        print("Lancement de la simulation...")
        sensor_data = kspaceFirstOrder3D(
            kgrid=kgrid,
            medium=self.medium,
            source=source,
            sensor=sensor,
            simulation_options=simulation_options,
            execution_options=execution_options,
        )
        print("Simulation terminée avec succès.")
        return sensor_data['p'].reshape(kgrid.Nt,(self.params['Nz'], self.params['Ny'], self.params['Nx']))

    def animated_plot_AcousticField(self, step=10, save_dir=None):
        """
        Plot synchronized animations of A_matrix slices for selected angles.

        Args:
            step: time step between frames (default every 10 frames)
            save_dir: directory to save the animation gif; if None, animation will not be saved

        Returns:
            ani: Matplotlib FuncAnimation object
        """

        # Set the maximum embedded animation size to 100 MB
        plt.rcParams['animation.embed_limit'] = 100

        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)

        ims = []

        # Create a figure and axis
        fig, ax = plt.subplots()

        # Set main title
        fig.suptitle(f"[System Matrix Animation] Pattern structure: {self.pattern.activeList} | Angles {self.params['angle']}°", fontsize=12, y=0.98)

        # Ensure start_idx_in_A_matrix exists
        if not hasattr(self, 'start_idx_in_A_matrix'):
            raise AttributeError("StructuredWave must have attribute 'start_idx_in_A_matrix' to locate A_matrix slices.")

        # Initial plot
        im = ax.imshow(
            self.field[0, :, :],
            extent=(self.params['Xrange'][0]*1000, self.params['Xrange'][-1]*1000, self.params['Zrange'][-1]*1000, self.params['Zrange'][0]*1000),
            vmax=1,
            aspect='equal',
            cmap='jet',
            animated=True
        )
        ax.set_title(f"{self.waveType} | Angle {self.params['angle']}°", fontsize=10)
        ax.set_xlabel("x (mm)", fontsize=8)
        ax.set_ylabel("z (mm)", fontsize=8)
        ims.append((im, ax, self.params['angle']))

        # Adjust layout to leave space for main title
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Unified update function for all subplots
        def update(frame):
            artists = []
            for im, ax, angle in ims:
                im.set_array(self.field[frame, :, :])
                ax.set_title(f"{self.waveType} | Angle {angle}° | t = {frame * self.params['f_saving'] * 1000:.2f} ms", fontsize=10)
                artists.append(im)
            return artists

        # Create animation
        ani = animation.FuncAnimation(
            fig, update,
            frames=range(0, self.field.shape[0], step),
            interval=50, blit=True
        )

        # Save animation if needed
        if save_dir is not None:
            save_filename = f"A | Pattern structure {self.pattern.activeList} | Angles {self._format_angle()}.gif"
            save_path = os.path.join(save_dir, save_filename)
            ani.save(save_path, writer='pillow', fps=20)
            print(f"Saved: {save_path}")

        plt.close(fig)

        return ani


class PlaneWave(StructuredWave):
    def __init__(self, angle_deg, **kwargs):
        super().__init__(**kwargs)
        self.waveType = WaveType.PlaneWave
        self.angle_deg = angle_deg
        self.activeListHex = '1' * (self.num_elements // 4)  # All elements are active
        self.__check_angle(self)

    @staticmethod
    def __check_angle(self):
        if self.angle_deg < -20 or self.angle_deg > 20:
            raise ValueError("Angle must be between -20 and 20 degrees.")
    
class FocusedWave(AcousticField):
    pass



