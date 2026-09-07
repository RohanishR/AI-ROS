import os
import json
import argparse
import urllib.request

def download_taco_annotations(dest_dir):
    """
    Downloads the official TACO dataset annotations.
    """
    url = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, "annotations.json")
    
    if not os.path.exists(dest_path):
        print(f"Downloading TACO annotations from {url}...")
        try:
            urllib.request.urlretrieve(url, dest_path)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download: {e}")
            return None
    else:
        print("Annotations already exist.")
        
    return dest_path

def convert_coco_to_yolo(annotations_path, output_dir):
    """
    Converts COCO format annotations to YOLO format.
    NOTE: TACO images need to be downloaded separately via the TACO download script 
    (https://github.com/pedropro/TACO/blob/master/download.py) because they are hosted across multiple sources.
    This function assumes you have the images and just converts the bounding box formats.
    """
    if not annotations_path or not os.path.exists(annotations_path):
        print("Annotations file not found.")
        return

    with open(annotations_path, 'r') as f:
        coco = json.load(f)

    os.makedirs(os.path.join(output_dir, 'labels'), exist_ok=True)
    
    # Create class mapping mapping id -> zero-indexed yolo class id
    class_mapping = {cat['id']: i for i, cat in enumerate(coco['categories'])}
    
    # Save a classes.txt file
    with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
        for cat in coco['categories']:
            f.write(f"{cat['name']}\n")

    images_info = {img['id']: img for img in coco['images']}

    print("Converting annotations to YOLO format...")
    for ann in coco['annotations']:
        img_id = ann['image_id']
        img = images_info[img_id]
        
        # COCO bbox format is [x_min, y_min, width, height]
        x_min, y_min, w, h = ann['bbox']
        img_w, img_h = img['width'], img['height']
        
        # YOLO format is [x_center, y_center, width, height] normalized to 0-1
        x_center = (x_min + w / 2) / img_w
        y_center = (y_min + h / 2) / img_h
        norm_w = w / img_w
        norm_h = h / img_h
        
        yolo_class_id = class_mapping[ann['category_id']]
        
        # Use image file name for the label text file name
        base_name = os.path.splitext(os.path.basename(img['file_name']))[0]
        label_path = os.path.join(output_dir, 'labels', f"{base_name}.txt")
        
        with open(label_path, 'a') as f:
            f.write(f"{yolo_class_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}\n")
            
    print(f"Conversion complete. YOLO labels saved to {output_dir}/labels/")
    print("NOTE: You must download the actual images using the official TACO repo's download.py script.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Prepare TACO Dataset for YOLO")
    parser.add_argument('--dest', type=str, default='dataset', help='Destination directory')
    args = parser.parse_args()
    
    ann_path = download_taco_annotations(args.dest)
    convert_coco_to_yolo(ann_path, args.dest)
