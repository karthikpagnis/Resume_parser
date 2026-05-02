import os
os.environ['OPENBLAS_CORETYPE'] = 'NEHALEM'
os.environ['MKL_THREADING_LAYER'] = 'GNU'
import torch
print(f"PyTorch version: {torch.version}")
print(f"CUDA available: {torch.cuda.is_available()}")
print("✓ PyTorch loaded successfully")
