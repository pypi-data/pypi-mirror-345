import GPUtil

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, process='cpu'):
        if not hasattr(self, 'initialized'):
            self.process = process
            self.bestGPU = None
            self.initialized = True

    def set_process(self, process):
        if process not in ['cpu', 'gpu']:
            raise ValueError("process must be 'cpu' or 'gpu'")
        self.process = process

    def get_process(self):
        return self.process
    
    def select_best_gpu(self):
        gpus = GPUtil.getGPUs()
        if not gpus:
            print("No GPUs found.")
            self.bestGPU = None

        best_gpu = 0
        max_memory = 0

        for i, gpu in enumerate(gpus):
            # Obtenez la mémoire totale et utilisée pour chaque GPU
            total_memory = gpu.memoryTotal
            used_memory = gpu.memoryUsed
            available_memory = total_memory - used_memory

            # Sélectionnez le GPU avec le plus de mémoire disponible
            if available_memory > max_memory:
                max_memory = available_memory
                best_gpu = i
        print(f"Best GPU is GPU {best_gpu} with {max_memory:.2f} MB available.")
        self.bestGPU = best_gpu

config = Config()