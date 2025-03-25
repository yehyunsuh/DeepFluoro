import os
import argparse
import h5py
import numpy as np
import nibabel as nib
import json
import cv2


def process_patient_group(patient_id,group, output_path):
    os.makedirs(output_path, exist_ok=True)

    # --- Volume ---
    if 'vol' in group and 'pixels' in group['vol']:
        volume = group['vol']['pixels'][()]
        dir_mat = group['vol']['dir-mat'][()]
        origin = group['vol']['origin'][()]
        spacing = group['vol']['spacing'][()]

        spacing = spacing.flatten()
        affine = dir_mat @ np.diag(spacing)
        affine = np.concatenate([affine, origin], axis=1)
        affine = np.vstack([affine, [0, 0, 0, 1]])

        volume_nifti = nib.Nifti1Image(volume, affine=affine)
        nib.save(volume_nifti, os.path.join(output_path, f"{patient_id}.nii.gz"))
        print(f"Saved {patient_id}.nii.gz with proper affine in {output_path}")

    # --- Segmentation ---
    if 'vol-seg' in group and 'image' in group['vol-seg']:
        seg = group['vol-seg']['image']['pixels'][()]
        seg_dir_mat = group['vol-seg']['image']['dir-mat'][()]
        seg_origin = group['vol-seg']['image']['origin'][()]
        seg_spacing = group['vol-seg']['image']['spacing'][()]

        seg_spacing = seg_spacing.flatten()
        seg_affine = seg_dir_mat @ np.diag(seg_spacing)
        seg_affine = np.concatenate([seg_affine, seg_origin], axis=1)
        seg_affine = np.vstack([seg_affine, [0, 0, 0, 1]])
        
        seg_nifti = nib.Nifti1Image(seg, affine=seg_affine)
        nib.save(seg_nifti, os.path.join(output_path, f"{patient_id}_seg.nii.gz"))
        print(f"Saved {patient_id}_seg.nii.gz with proper affine in {output_path}")

    # --- Landmarks ---
    if 'vol-landmarks' in group:
        landmarks = {}
        for lm_name in group['vol-landmarks']:
            coord = group['vol-landmarks'][lm_name][()]
            landmarks[lm_name] = coord.tolist()
        with open(os.path.join(output_path, "landmarks.json"), 'w') as f_json:
            json.dump(landmarks, f_json, indent=2)
        print(f"Saved landmarks.json in {output_path}")

    # --- Projection Images ---
    if 'projections' in group:
        proj_dir = os.path.join(output_path, "projections")
        os.makedirs(proj_dir, exist_ok=True)
        for proj_id in list(group['projections'].keys()):
            proj_path = group['projections'][proj_id]
            if 'image' in proj_path:
                img = proj_path['image']['pixels'][()]

                # normalize
                img = img.astype(np.float32)
                img = (img - np.min(img)) / (np.max(img) - np.min(img))
                img = (img * 255).astype(np.uint8)
                cv2.imwrite(os.path.join(proj_dir, f"{patient_id}_{proj_id}.png"), img)
        print(f"Saved projections in {proj_dir}")


def main(args):
    with h5py.File(args.input, 'r') as f:
        for patient_id in f.keys():
            if patient_id == "proj-params":
                continue  # skip global projection params
            group = f[patient_id]
            patient_output_path = os.path.join(args.output, patient_id)
            process_patient_group(patient_id, group, patient_output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert h5 files to nii.gz, JSON, and PNG format.")
    parser.add_argument('--input', type=str, help='Input h5 file path', default='1_DeepFluoro_unzipped/ipcai_2020_full_res_data.h5')
    parser.add_argument('--output', type=str, help='Output directory', default='2_DeepFluoro_nii')

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    main(args)