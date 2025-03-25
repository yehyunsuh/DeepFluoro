# DeepFluoro

```
conda create -n DeepFluoro python=3.10 -y
conda activate DeepFluoro
```

## 0. Download NMDID dataset

## 1. Unzip NMDID dataset
```
python3 1_unzip.py
```

## 2. Extract nii from .h5
```
python3 2_h5_to_nii.py
```