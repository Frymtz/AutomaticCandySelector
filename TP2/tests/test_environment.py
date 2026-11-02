
import torch
import torchvision
import cv2
import numpy as np
import pandas as pd
import sklearn

print("=== ACS : Vérification de l'environnement ===")

print("PyTorch :", torch.__version__)
print("Torchvision :", torchvision.__version__)
print("OpenCV :", cv2.__version__)
print("NumPy :", np.__version__)
print("Pandas :", pd.__version__)
print("Scikit-learn :", sklearn.__version__)

print("\n=== Configuration CUDA ===")

print("CUDA PyTorch :", torch.version.cuda)
print("CUDA disponible :", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU :", torch.cuda.get_device_name(0))
    print("Compute capability :",
          torch.cuda.get_device_capability(0))
    print("Architectures PyTorch :",
          torch.cuda.get_arch_list())

    try:
        a = torch.rand(256, 256, device="cuda")
        b = a @ a
        torch.cuda.synchronize()
        print("Test GPU : OK")
    except Exception as e:
        print("Test GPU : ÉCHEC")
        print(type(e).__name__, str(e))
else:
    print("GPU CUDA non disponible")

print("\n=== Test CNN sur CPU ===")

from torchvision.models import mobilenet_v3_small

model = mobilenet_v3_small(weights=None)
model.eval()

image = torch.rand(1, 3, 224, 224)

with torch.inference_mode():
    output = model(image)

print("Entrée :", tuple(image.shape))
print("Sortie :", tuple(output.shape))
print("Test CNN : OK")
