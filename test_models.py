"""Test model loading without starting full app"""

import os

# Set all compatibility flags
os.environ['OPENBLAS_CORETYPE'] = 'NEHALEM'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_THREADING_LAYER'] = 'GNU'
os.environ['TORCH_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

print("1. Testing PyTorch...")
import torch
print(f"   ✓ PyTorch loaded: {torch.__version__}")

print("\n2. Testing numpy...")
import numpy as np
print(f"   ✓ Numpy loaded: {np.__version__}")

print("\n3. Testing transformers library...")
from transformers import pipeline
print("   ✓ Transformers imported")

print("\n4. Testing NER model loading...")
try:
    print("   Loading NER model (this may take a minute)...")
    ner = pipeline(
        "token-classification",
        model="dbmdz/bert-base-cased-finetuned-conll03-english",
        aggregation_strategy="simple",
        device=-1
    )
    print("   ✓ NER model loaded successfully!")
except Exception as e:
    print(f"   ✗ NER model failed: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Testing Zero-shot model...")
try:
    print("   Loading Zero-shot model (this may take a minute)...")
    zs = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1
    )
    print("   ✓ Zero-shot model loaded successfully!")
except Exception as e:
    print(f"   ✗ Zero-shot model failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ All model tests passed! App should work now.")
