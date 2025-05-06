
from .Settings import *
from .AOT_Optic import *
from .AOT_Acoustic import *
import os
import ast

class Experiment:
    def __init__(self,AcousticFieldPath,fieldParamPath, params):
        self.params = params
        self.systemMatrix = self._generate_system_matrix(AcousticFieldPath, fieldParamPath, params)
        self.OpticImage = AOT_biomaps.AOT_Optic.Phantom(params=params)
        self.AOsignal = None

        if type(params)!= AOT_biomaps.Settings.Params:
            raise TypeError("params must be an instance of the Params class")
        
    def _generate_system_matrix(self, fieldDataPath, fieldParamPath, params):
        if not os.path.exists(fieldParamPath):
            raise FileNotFoundError(f"Field parameter file {fieldParamPath} not found.")
        os.makedirs(fieldDataPath, exist_ok=True)
        sytemMatrix = []
        patternList = []
        with open(fieldParamPath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue  # skip empty lines
                try:
                    parts = line.split('),')
                    coords = ast.literal_eval(parts[0] + ')')  # (0, 192, 0, 0)
                    angles = ast.literal_eval(parts[1])        # [0] ou [2, -20]
                    for angle in angles:
                        patternList.append([*coords, angle])
                except Exception as e:
                    print(f"Erreur de parsing sur la ligne: {line}\n{e}")

        for pattern in patternList:
            if len(pattern) != 5:
                raise ValueError(f"Invalid pattern format: {pattern}. Expected 5 values.")
            AcousticField = AOT_biomaps.AOT_Acoustic.StructuredWave(
                angle_deg=patternList[0][4],
                space_0=patternList[0][0],
                space_1=patternList[0][1],
                move_head_0_2tail=patternList[0][2],
                move_tail_1_2head=patternList[0][3],
                params=params  # Pass params as a keyword argument
            )

            pathField = os.path.join(fieldDataPath, os.path.basename(AcousticField.get_path()))
            if os.path.exists(pathField):
                print(f"Loading system matrix from {fieldDataPath}")
                sytemMatrix.append(AcousticField.load_field(pathField, params.acoustic['typeSim']))
            else:
                AcousticField.generate_field()
                AcousticField.calculate_envelope_squared()
                sytemMatrix.append(AcousticField)

        


            
                
    

            
        
        
        
    

def plot_animations_A_matrix(self, A_matrix, z, x, angles_to_plot, wave_name=None, step=10, save_dir=None):
        """
        Plot synchronized animations of A_matrix slices for selected angles.

        Args:
            A_matrix: 4D numpy array (time, z, x, angles)
            z: array of z-axis positions
            x: array of x-axis positions
            angles_to_plot: list of angles to visualize
            wave_name: optional name for labeling the subplots (e.g., "wave1")
            step: time step between frames (default every 10 frames)
            save_dir: directory to save the animation gif; if None, animation will not be saved

        Returns:
            ani: Matplotlib FuncAnimation object
        """
        import os
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import numpy as np
        import matplotlib as mpl

        # Set the maximum embedded animation size to 100 MB
        mpl.rcParams['animation.embed_limit'] = 100

        # Check if all angles are valid
        missing_angles = [angle for angle in angles_to_plot if angle not in self.angles]
        if missing_angles:
            raise ValueError(f"The following angles are not available in the wave: {missing_angles}")

        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)

        num_plots = len(angles_to_plot)

        # Automatically adjust layout
        if num_plots <= 3:
            nrows, ncols = 1, num_plots
        else:
            ncols = 3
            nrows = (num_plots + ncols - 1) // ncols

        # Create figure and subplots 
        fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5.3 * nrows))
        if isinstance(axes, plt.Axes):
            axes = np.array([axes])
        axes = axes.flatten()

        ims = []
        pattern_str = self.pattern_params.to_string()

        # Set wave_name if not provided 
        if wave_name is None:
            wave_name = f"Pattern structure {pattern_str}"  # default fallback

        # Set main title 
        fig.suptitle(f"[System Matrix Animation] Pattern structure: {pattern_str} | Angles {angles_to_plot}",
                    fontsize=12, y=0.98)

        # Create a mapping from angle to local index
        angle_idx_map = {angle: idx for idx, angle in enumerate(self.angles)}

        # Ensure start_idx_in_A_matrix exists
        if not hasattr(self, 'start_idx_in_A_matrix'):
            raise AttributeError("StructuredWave must have attribute 'start_idx_in_A_matrix' to locate A_matrix slices.")

        for idx, angle in enumerate(angles_to_plot):
            ax = axes[idx]
            local_index = angle_idx_map[angle]
            global_index = self.start_idx_in_A_matrix + local_index  # <-- Key: from A_matrix global index

            im = ax.imshow(A_matrix[0, :, :, global_index],
                        # extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000), vmax =  0.2*np.max(A_matrix[:,:,:,global_index]),
                        extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000), vmax =  1,
                        aspect='equal', cmap='jet', animated=True)
            ax.set_title(f"{wave_name} | Angle {angle}°", fontsize=10)
            ax.set_xlabel("x (mm)", fontsize=8)
            ax.set_ylabel("z (mm)", fontsize=8)
            ims.append((im, ax, angle, global_index))

        # Remove unused axes if any
        for j in range(num_plots, len(axes)):
            fig.delaxes(axes[j])

        # Adjust layout to leave space for main title
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Unified update function for all subplots
        def update(frame):
            artists = []
            for im, ax, angle, global_index in ims:
                im.set_array(A_matrix[frame, :, :, global_index])
                ax.set_title(f"{wave_name} | Angle {angle}° | t = {frame * 25e-6 * 1000:.2f} ms", fontsize=10)
                artists.append(im)
            return artists

        # Create animation
        ani = animation.FuncAnimation(
            fig, update,
            frames=range(0, A_matrix.shape[0], step),
            interval=50, blit=True
        )

        # Save animation if needed
        if save_dir is not None:
            angles_str = '_'.join(str(a) for a in angles_to_plot)
            save_filename = f"A | Pattern structure {pattern_str} | Angles {angles_str}.gif"
            save_path = os.path.join(save_dir, save_filename)
            ani.save(save_path, writer='pillow', fps=20)
            print(f"Saved: {save_path}")

        plt.close(fig)

        return ani

def plot_animated_y_A_LAMBDA(self, A_matrix, y, LAMBDA, x, z, angle, save_dir=None, step=10, wave_name=None):
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import matplotlib as mpl

    mpl.rcParams['animation.embed_limit'] = 100

    if angle not in self.angles:
        raise ValueError(f"Angle {angle} not found in this wave's angles.")
    local_idx = self.angles.index(angle)

    if self.start_idx_in_A_matrix is None:
        raise AttributeError("StructuredWave must have 'start_idx_in_A_matrix' assigned.")
    global_idx = self.start_idx_in_A_matrix + local_idx

    pattern_str = self.pattern_params.to_string()
    if wave_name is None:
        wave_name = f"Pattern structure {pattern_str}"

    fig, axs = plt.subplots(1, 3, figsize=(6 * 3, 5.3 * 1))
    if isinstance(axs, plt.Axes):
        axs = np.array([axs])

    fig.suptitle(f"[AO Signal Animation] {wave_name} | Angle {angle}°", fontsize=12, y=0.98)

    # Left: LAMBDA at bottom
    im_lambda_bottom = axs[0].imshow(LAMBDA.T, cmap='hot', alpha=1, origin='upper',
                                    extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000),
                                    aspect='equal')

    # Acoustic field drawn on top of LAMBDA
    im_field = axs[0].imshow(A_matrix[0, :, :, global_idx], cmap='jet', origin='upper',
                            extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000), vmax =  1, vmin = 0.01, alpha=0.8,
                            aspect='equal')

    axs[0].set_title(f"{wave_name} | Angle {angle}° | t = 0.00 ms", fontsize=10)
    axs[0].set_xlabel("x (mm)", fontsize=8)
    axs[0].set_ylabel("z (mm)", fontsize=8)

    # Center: AO signal y
    time_axis = np.arange(y.shape[0]) * 25e-6 * 1000  # in ms
    line_y, = axs[1].plot(time_axis, y[:, global_idx])
    # vertical_line = axs[1].axvline(x=time_axis[0], color='r', linestyle='--')
    vertical_line, = axs[1].plot([time_axis[0], time_axis[0]], [0, y[0, global_idx]], 'r--')
    axs[1].set_xlabel("Time (ms)", fontsize=8)
    axs[1].set_ylabel("Value", fontsize=8)
    axs[1].set_title(f"{wave_name} | Angle {angle}° | t = 0.00 ms", fontsize=10)

    # Right: Static Ground Truth LAMBDA
    im_lambda = axs[2].imshow(LAMBDA.T, extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000),
                            cmap='hot', aspect='equal')
    axs[2].set_title("Ground Truth LAMBDA", fontsize=10)
    axs[2].set_xlabel("x (mm)", fontsize=8)
    axs[2].set_ylabel("z (mm)", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    def update(frame):
        current_time_ms = frame * 25e-6 * 1000

        # Apply masking to suppress background
        frame_data = A_matrix[frame, :, :, global_idx]
        masked_data = np.where(frame_data > 0.02, frame_data, np.nan)
        im_field.set_data(masked_data)

        axs[0].set_title(f"{wave_name} | Angle {angle}° | t = {current_time_ms:.2f} ms", fontsize=10)

        # Copy partial y signal
        y_vals = y[:, global_idx]
        y_copy = np.full_like(y_vals, np.nan)
        y_copy[:frame + 1] = y_vals[:frame + 1]
        line_y.set_data(time_axis, y_copy)

        # Red vertical line
        vertical_line.set_data([time_axis[frame], time_axis[frame]], [0, y_vals[frame]])

        axs[1].set_title(f"{wave_name} | Angle {angle}° | t = {current_time_ms:.2f} ms", fontsize=10)

        return [im_field, vertical_line, line_y]


    # Create the animation
    ani = animation.FuncAnimation(
        fig, update,
        frames=range(0, A_matrix.shape[0], step),
        interval=50, blit=True
    )
    
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)
        save_filename = f"A_y_LAMBDA_overlay | Pattern {pattern_str} | Angle {angle}.gif"
        save_path = os.path.join(save_dir, save_filename)
        ani.save(save_path, writer='pillow', fps=20)
        print(f"Saved: {save_path}")

    plt.close(fig)

    return ani

def plot_animated_y_A_LAMBDA_orignal(self, A_matrix, y, LAMBDA, x, z, angle, save_dir=None, step=10, wave_name=None):
    """
    Plot and optionally save an animation showing A_matrix, y signal, and LAMBDA.

    Args:
        A_matrix: 4D array (time, z, x, angles)
        y: 2D array (time, angles)
        LAMBDA: 2D array (z, x)
        x: x-axis positions
        z: z-axis positions
        angle: angle to visualize
        save_dir: if not None, save the animation gif to this folder
        step: frame step size for the animation
        wave_name: optional name for labeling (default uses pattern structure)

    Returns:
        ani: Matplotlib FuncAnimation object
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import matplotlib as mpl

    # Set the maximum embedded animation size to 100 MB
    mpl.rcParams['animation.embed_limit'] = 100

    # Find the local index of the requested angle 
    if angle not in self.angles:
        raise ValueError(f"Angle {angle} not found in this wave's angles.")
    local_idx = self.angles.index(angle)

    # Calculate global index in A_matrix and y
    if self.start_idx_in_A_matrix is None:
        raise AttributeError("StructuredWave must have 'start_idx_in_A_matrix' assigned.")
    global_idx = self.start_idx_in_A_matrix + local_idx

    # Get pattern string
    pattern_str = self.pattern_params.to_string()

    # Set wave_name if not provided
    if wave_name is None:
        wave_name = f"Pattern structure {pattern_str}"

    # Create figure and subplots 
    fig, axs = plt.subplots(1, 3, figsize=(6 * 3, 5.3 * 1))  # 1 row, 3 columns
    if isinstance(axs, plt.Axes):
        axs = np.array([axs])

    # Global Title 
    fig.suptitle(f"[AO Signal Animation] {wave_name} | Angle {angle}°", fontsize=12, y=0.98)

    # Left: Acoustic field (A matrix)
    im_field = axs[0].imshow(A_matrix[0, :, :, global_idx], cmap='jet', origin='upper',
                            extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000),
                            aspect='equal')
    axs[0].set_title(f"{wave_name} | Angle {angle}° | t = 0.00 ms", fontsize=10)
    axs[0].set_xlabel("x (mm)", fontsize=8)
    axs[0].set_ylabel("z (mm)", fontsize=8)

    # Center: AO signal y
    time_axis = np.arange(y.shape[0]) * 25e-6 * 1000  # Convert index to ms
    line_y, = axs[1].plot(time_axis, y[:, global_idx])
    vertical_line = axs[1].axvline(x=time_axis[0], color='r', linestyle='--')  # initial position
    axs[1].set_xlabel("Time (ms)", fontsize=8)
    axs[1].set_ylabel("Value", fontsize=8)
    axs[1].set_title(f"{wave_name} | Angle {angle}° | t = 0.00 ms", fontsize=10)

    # Right: Ground truth LAMBDA
    im_lambda = axs[2].imshow(LAMBDA.T, extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000),
                            cmap='hot', aspect='equal')
    axs[2].set_title("Ground Truth LAMBDA", fontsize=10)
    axs[2].set_xlabel("x (mm)", fontsize=8)
    axs[2].set_ylabel("z (mm)", fontsize=8)

    # Adjust layout 
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Update function for animation
    def update(frame):
        current_time_ms = frame * 25e-6 * 1000
        im_field.set_data(A_matrix[frame, :, :, global_idx])
        axs[0].set_title(f"{wave_name} | Angle {angle}° | t = {current_time_ms:.2f} ms", fontsize=10)
        vertical_line.set_xdata([current_time_ms, current_time_ms])
        axs[1].set_title(f"{wave_name} | Angle {angle}° | t = {current_time_ms:.2f} ms", fontsize=10)
        return [im_field, vertical_line]

    # Create the animation
    ani = animation.FuncAnimation(
        fig, update,
        frames=range(0, A_matrix.shape[0], step),
        interval=50, blit=True
    )

    # Save animation if needed
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)
        save_filename = f"A_y_LAMBDA | Pattern {pattern_str} | Angle {angle}.gif"
        save_path = os.path.join(save_dir, save_filename)
        ani.save(save_path, writer='pillow', fps=20)
        print(f"Saved: {save_path}")

    plt.close(fig)

    return ani

def plot_AO_signal_y(self, y, angles_to_plot, save_dir=None, wave_name=None):
    """
    Plot AO signals y(t) for selected angles.

    Args:
        y: 2D numpy array (time, angles)
        angles_to_plot: list of angles to visualize
        save_dir: directory to save the figure; if None, only display
        wave_name: optional name for labeling; default uses pattern structure
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt

    # Validate input angles
    missing_angles = [angle for angle in angles_to_plot if angle not in self.angles]
    if missing_angles:
        raise ValueError(f"The following angles are not available in the wave: {missing_angles}")

    # Time axis in milliseconds
    time_axis = np.arange(y.shape[0]) * 25e-6 * 1000

    # Prepare wave_name if not provided
    pattern_str = self.pattern_params.to_string()
    if wave_name is None:
        wave_name = f"Pattern structure {pattern_str}"

    # Set up layout
    num_plots = len(angles_to_plot)
    if num_plots == 1:
        nrows, ncols = 1, 1
    elif num_plots == 2:
        nrows, ncols = 1, 2
    else:
        ncols = 3
        nrows = (num_plots + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 4.5 * nrows))
    if isinstance(axes, plt.Axes):
        axes = np.array([axes])
    axes = axes.flatten()

    # Set main title
    fig.suptitle(f"[AO Signal Plot] {wave_name} | Angles {angles_to_plot}", fontsize=12, y=0.98)

    # Mapping from angle to local index
    angle_idx_map = {angle: idx for idx, angle in enumerate(self.angles)}

    for idx, angle in enumerate(angles_to_plot):
        ax = axes[idx]
        local_idx = angle_idx_map[angle]
        ax.plot(time_axis, y[:, self.start_idx_in_A_matrix + local_idx])
        ax.set_xlabel("Time (ms)", fontsize=8)
        ax.set_ylabel("Value", fontsize=8)
        ax.set_title(f"{wave_name} | Angle {angle}°", fontsize=10)

    # Remove unused axes
    for j in range(num_plots, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save if needed
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)
        angles_str = '_'.join(str(a) for a in angles_to_plot)
        save_filename = f"Static_y_Plot | Pattern {pattern_str} | Angles {angles_str}.png"
        save_path = os.path.join(save_dir, save_filename)
        plt.savefig(save_path, dpi=200)
        print(f"Saved: {save_path}")

    plt.show()
    plt.close(fig)

