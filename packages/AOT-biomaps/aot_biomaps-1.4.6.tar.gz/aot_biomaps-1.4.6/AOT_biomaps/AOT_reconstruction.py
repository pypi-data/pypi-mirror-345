import subprocess
import os
import numpy as np

class Recon:
    def __init__(self, AO_path, sMatrixDir, imageDir, reconExe):
        self.AO_path = AO_path
        self.sMatrixDir = sMatrixDir
        self.imageDir = imageDir
        self.reconExe = reconExe

    def run(self):
        makeRecon(self.AO_path, self.sMatrixDir, self.imageDir, self.reconExe)

def makeRecon(AO_path, sMatrixDir,imageDir,reconExe):

    # Check if the input file exists
    if not os.path.exists(AO_path):
        print(f"Error: no input file {AO_path}")
        exit(1)

    # Check if the system matrix directory exists
    if not os.path.exists(sMatrixDir):
        print(f"Error: no system matrix directory {sMatrixDir}")
        exit(2)

    # Create the output directory if it does not exist
    os.makedirs(imageDir, exist_ok=True)

    opti = "MLEM"
    penalty = ""
    iteration = "100:10"

    cmd = (
        f"{reconExe} -df {AO_path} -opti {opti} {penalty} "
        f"-it {iteration} -proj matrix -dout {imageDir} -th 24 -vb 5 -proj-comp 1 -ignore-scanner "
        f"-data-type AOT -ignore-corr cali,fdur -system-matrix {sMatrixDir}"
    )
    result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
    print(result.stdout)

def read_recon(hdr_path):
    """
    Lit un fichier Interfile (.hdr) et son fichier binaire (.img) pour reconstruire une image comme le fait Vinci.
    
    Paramètres :
    ------------
    - hdr_path : chemin complet du fichier .hdr
    
    Retour :
    --------
    - image : tableau NumPy contenant l'image
    - header : dictionnaire contenant les métadonnées du fichier .hdr
    """
    header = {}
    with open(hdr_path, 'r') as f:
        for line in f:
            if ':=' in line:
                key, value = line.split(':=', 1)  # s'assurer qu'on ne coupe que la première occurrence de ':='
                key = key.strip().lower().replace('!', '')  # Nettoyage des caractères
                value = value.strip()
                header[key] = value
    
    # 📘 Obtenez le nom du fichier de données associé (le .img)
    data_file = header.get('name of data file')
    if data_file is None:
        raise ValueError(f"Impossible de trouver le fichier de données associé au fichier header {hdr_path}")
    
    img_path = os.path.join(os.path.dirname(hdr_path), data_file)
    
    # 📘 Récupérer la taille de l'image à partir des métadonnées
    shape = [int(header[f'matrix size [{i}]']) for i in range(1, 4) if f'matrix size [{i}]' in header]
    if shape and shape[-1] == 1:  # Si la 3e dimension est 1, on la supprime
        shape = shape[:-1]  # On garde (192, 240) par exemple
    
    if not shape:
        raise ValueError("Impossible de déterminer la forme de l'image à partir des métadonnées.")
    
    # 📘 Déterminez le type de données à utiliser
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
    
    # 📘 Ordre des octets (endianness)
    byte_order = header.get('imagedata byte order', 'LITTLEENDIAN').lower()
    endianess = '<' if 'little' in byte_order else '>'
    
    # 📘 Vérifie la taille réelle du fichier .img
    img_size = os.path.getsize(img_path)
    expected_size = np.prod(shape) * np.dtype(dtype).itemsize
    
    if img_size != expected_size:
        raise ValueError(f"La taille du fichier img ({img_size} octets) ne correspond pas à la taille attendue ({expected_size} octets).")
    
    # 📘 Lire les données binaires et les reformater
    with open(img_path, 'rb') as f:
        data = np.fromfile(f, dtype=endianess + np.dtype(dtype).char)
    
    image =  data.reshape(shape[::-1]) 
    
    # 📘 Rescale l'image si nécessaire
    rescale_slope = float(header.get('data rescale slope', 1))
    rescale_offset = float(header.get('data rescale offset', 0))
    image = image * rescale_slope + rescale_offset
    
    return image.T


@staticmethod
def plot_reconstruction_from_files(file_template, num_frames, x, z, waves, waves_define_str, save_dir=None):
    """
    Static method to read reconstruction frames from files and create animations.
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import matplotlib as mpl
    import re

    # Read reconstruction result frames
    frames = []
    for i in range(1, num_frames + 1):
        path = file_template.format(i)
        if os.path.exists(path):
            frames.append(AOT_reconstruction.read_recon(path))
        else:
            print(f"WARNING: {path} not found.")

    if len(frames) == 0:
        raise ValueError("No frames were loaded. Please check file paths.")

    frames = np.array(frames)  # (iterations, z, x)

    mpl.rcParams['animation.embed_limit'] = 100

    ###### 1. Plot with wave definition text (1x2)
    fig1, axs1 = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [1.5, 1]})

    # Left plot: the reconstruction image
    im1 = axs1[0].imshow(frames[0].T,
                        extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000),
                        vmin=0, vmax=1,
                        aspect='equal', cmap='hot', animated=True)
    axs1[0].set_xlabel("x (mm)")
    axs1[0].set_ylabel("z (mm)")
    axs1[0].set_title("Reconstruction | Iteration 1", fontsize=12)

    # Right plot: text info
    axs1[1].axis('off')
    axs1[1].set_title("[Reconstruction Animation]", fontsize=12, loc='left')

    # Evaluate any arithmetic expressions (e.g. 4*4 → 16) in the text
    waves_define_str_cal = re.sub(r'\d+\s*\*\s*\d+', lambda m: str(eval(m.group(0))), waves_define_str)

    axs1[1].text(0.0, 1.0, waves_define_str_cal, fontsize=10, ha='left', va='top', wrap=True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    def update_with_text(i):
        im1.set_array(frames[i].T)
        axs1[0].set_title(f"Reconstruction | Iteration {i + 1}")
        return [im1]

    ani_with_text = animation.FuncAnimation(
        fig1, update_with_text, frames=len(frames), interval=30, blit=True
    )

    ###### 2. Plot without any text (clean display only)
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    im2 = ax2.imshow(frames[0].T,
                    extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000),
                    vmin=0, vmax=1,
                    aspect='equal', cmap='hot', animated=True)
    ax2.set_xlabel("x (mm)")
    ax2.set_ylabel("z (mm)")
    ax2.set_title("Reconstruction")

    plt.tight_layout()

    def update_no_text(i):
        im2.set_array(frames[i].T)
        ax2.set_title(f"Reconstruction | Iteration {i + 1}")
        return [im2]

    ani_no_text = animation.FuncAnimation(
        fig2, update_no_text, frames=len(frames), interval=30, blit=True
    )

    ###### Save animations (optional)
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)

        # Build suffix string based on wave patterns and number of angles
        pattern_angle_strs = []
        for wave in waves:
            pattern_str = wave.pattern_params.to_string()
            num_angles = len(wave.angles)
            pattern_angle_strs.append(f"{pattern_str}&({num_angles})")
        suffix = '+'.join(pattern_angle_strs)

        # Limit filename length
        save_path_with_text = os.path.join(save_dir, f"ReconstructionAnimation_with_text__{suffix[:200]}.gif")
        save_path_no_text = os.path.join(save_dir, f"ReconstructionAnimation_no_text__{suffix[:200]}.gif")

        ani_with_text.save(save_path_with_text, writer='pillow', fps=50)
        ani_no_text.save(save_path_no_text, writer='pillow', fps=50)

        print(f"Saved with text: {save_path_with_text}")
        print(f"Saved without text: {save_path_no_text}")

    plt.close(fig2)
    plt.close(fig1)

    return ani_with_text

@staticmethod
def plot_reconstruction_from_files_v0(file_template, num_frames, x, z, waves, waves_define_str, save_dir=None):
        """
        Static method to read reconstruction frames from files and create animations.
        """
        import os
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import matplotlib as mpl

        # Read frames
        frames = []
        for i in range(1, num_frames + 1):
            path = file_template.format(i)
            if os.path.exists(path):
                frames.append(AOT_reconstruction.read_recon(path))
            else:
                print(f"WARNING: {path} not found.")

        if len(frames) == 0:
            raise ValueError("No frames were loaded. Please check file paths.")

        frames = np.array(frames)  # (iterations, z, x)

        mpl.rcParams['animation.embed_limit'] = 100

        ###### 1. Plot with text (1x2)
        fig1, axs1 = plt.subplots(1, 2, figsize=(10, 5))
        im1 = axs1[0].imshow(frames[0].T, extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000), vmin=0, vmax=1,
                            aspect='equal', cmap='hot', animated=True)
        axs1[0].set_xlabel("x (mm)")
        axs1[0].set_ylabel("z (mm)")
        axs1[0].set_title("Reconstruction")

        axs1[1].axis('off')
        axs1[1].text(0.0, 1.0, "[Reconstruction Animation]", fontsize=12, ha='left', va='top')
        #axs1[1].text(0.0, 0.9, waves_define_str, fontsize=10, ha='left', va='top', wrap=True)
        import re
        waves_define_str_cal = re.sub(r'\d+\s*\*\s*\d+', lambda m: str(eval(m.group(0))), waves_define_str)
        axs1[1].text(0.0, 0.9, waves_define_str_cal, fontsize=10, ha='left', va='top', wrap=True)


        plt.tight_layout(rect=[0, 0, 1, 0.93])

        def update_with_text(i):
            im1.set_array(frames[i].T)
            axs1[0].set_title(f"Reconstruction | Iteration {i + 1}")
            return [im1]

        ani_with_text = animation.FuncAnimation(fig1, update_with_text, frames=len(frames), interval=30, blit=True)

        ###### 2. Plot without text (1x1)
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        im2 = ax2.imshow(frames[0].T, extent=(x[0]*1000, x[-1]*1000, z[-1]*1000, z[0]*1000), vmin=0, vmax=1,
                        aspect='equal', cmap='hot', animated=True)
        ax2.set_xlabel("x (mm)")
        ax2.set_ylabel("z (mm)")
        ax2.set_title("Reconstruction")

        plt.tight_layout()

        def update_no_text(i):
            im2.set_array(frames[i].T)
            ax2.set_title(f"Reconstruction | Iteration {i + 1}")
            return [im2]

        ani_no_text = animation.FuncAnimation(fig2, update_no_text, frames=len(frames), interval=30, blit=True)

        ###### Save if needed
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)

            # --- Build suffix from waves ---
            pattern_angle_strs = []
            '''
            for wave in waves:
                pattern_str = wave.pattern_params.to_string()
                angles_str = '_'.join(str(a) for a in wave.angles)
                pattern_angle_strs.append(f"{pattern_str}&{angles_str}")
            suffix = '+'.join(pattern_angle_strs)
            '''
            for wave in waves:
                pattern_str = wave.pattern_params.to_string()
                num_angles = len(wave.angles)  # ! replace specific angles with the number of angles
                pattern_angle_strs.append(f"{pattern_str}&({num_angles})")
            suffix = '+'.join(pattern_angle_strs)
            
            save_path_with_text = os.path.join(save_dir, f"ReconstructionAnimation_with_text__{suffix[:200]}.gif")
            save_path_no_text = os.path.join(save_dir, f"ReconstructionAnimation_no_text__{suffix[:200]}.gif")
            
            ani_with_text.save(save_path_with_text, writer='pillow', fps=20)
            ani_no_text.save(save_path_no_text, writer='pillow', fps=20)

            print(f"Saved with text: {save_path_with_text}")
            print(f"Saved without text: {save_path_no_text}")

        plt.close(fig2)
        plt.close(fig1)

        return ani_with_text