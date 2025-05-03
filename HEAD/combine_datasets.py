import os
import xml.etree.ElementTree as ET
import random
from tqdm import tqdm

# Define dataset paths
SCUT_HEAD_PATH = './SCUT_HEAD'
HOLLYWOOD_PATH = './HollywoodHeads'
COMBINED_PATH = './COMBINED_HEAD'

# Create directories for COMBINED_HEAD
os.makedirs(os.path.join(COMBINED_PATH, 'Annotations'), exist_ok=True)
os.makedirs(os.path.join(COMBINED_PATH, 'JPEGImages'), exist_ok=True)
os.makedirs(os.path.join(COMBINED_PATH, 'Splits'), exist_ok=True)

# Function to check if an XML file is valid and has objects
def is_valid_xml_with_objects(xml_path):
    try:
        with open(xml_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return False, "Empty file"
        tree = ET.parse(xml_path)
        root = tree.getroot()
        objects = root.findall('object')
        if not objects:
            return False, "No objects found"
        return True, "Valid with objects"
    except ET.ParseError:
        return False, "Invalid XML"

# Process SCUT_HEAD: modify annotations and create symlinks for images
scut_ano_dir = os.path.join(SCUT_HEAD_PATH, 'Annotations')
scut_img_dir = os.path.join(SCUT_HEAD_PATH, 'JPEGImages')
combined_ano_dir = os.path.join(COMBINED_PATH, 'Annotations')
combined_img_dir = os.path.join(COMBINED_PATH, 'JPEGImages')

valid_scut_files = []
for ano_file in tqdm(os.listdir(scut_ano_dir), desc="Processing SCUT_HEAD annotations"):
    if ano_file.endswith('.xml'):
        src_ano = os.path.join(scut_ano_dir, ano_file)
        is_valid, reason = is_valid_xml_with_objects(src_ano)
        if not is_valid:
            print(f"Skipping {src_ano}: {reason}")
            continue
        
        base_name = os.path.splitext(ano_file)[0]
        valid_scut_files.append(base_name)
        
        # Modify annotation: change "person" to "head"
        dst_ano = os.path.join(combined_ano_dir, ano_file)
        tree = ET.parse(src_ano)
        root = tree.getroot()
        for obj in root.findall('object'):
            name = obj.find('name')
            if name.text == 'person':
                name.text = 'head'
        tree.write(dst_ano)
        
        # Create symlink for image with .jpg extension
        img_file = f"{base_name}.jpg"
        src_img = os.path.join(scut_img_dir, img_file)
        dst_img = os.path.join(combined_img_dir, img_file)
        if os.path.exists(src_img):
            if not os.path.exists(dst_img):
                os.symlink(os.path.relpath(src_img, combined_img_dir), dst_img)
            else:
                print(f"Symlink already exists: {dst_img}")
        else:
            print(f"Image not found: {src_img}")

# Read SCUT_HEAD split files and filter by valid files
scut_splits = {}
for split in ['train', 'val', 'test']:
    split_file = os.path.join(SCUT_HEAD_PATH, 'ImageSets', 'Main', f'{split}.txt')
    with open(split_file, 'r') as f:
        # Only include base names that have valid XMLs with objects
        scut_splits[split] = [
            line.strip() for line in f.readlines()
            if line.strip() in valid_scut_files
        ]

# Process HollywoodHeads: select every 15th valid annotation, split into train/val/test, and rename to .jpg
holly_ano_dir = os.path.join(HOLLYWOOD_PATH, 'Annotations')
all_holly_ano_files = [f for f in os.listdir(holly_ano_dir) if f.endswith('.xml')]

# Filter valid HollywoodHeads XMLs with objects
valid_holly_ano_files = []
for ano_file in tqdm(all_holly_ano_files, desc="Filtering HollywoodHeads annotations"):
    src_ano = os.path.join(holly_ano_dir, ano_file)
    is_valid, reason = is_valid_xml_with_objects(src_ano)
    if is_valid:
        valid_holly_ano_files.append(ano_file)
    else:
        print(f"Skipping {src_ano}: {reason}")

# Select every 15th valid annotation
selected_holly_ano_files = valid_holly_ano_files[::10]
selected_holly_base_names = [os.path.splitext(f)[0] for f in selected_holly_ano_files]

# Shuffle with a fixed seed for reproducibility
random.seed(42)
random.shuffle(selected_holly_base_names)

# Split into train (70%), val (15%), test (15%)
N = len(selected_holly_base_names)
train_end = int(0.7 * N)
val_end = int(0.85 * N)
train_holly = selected_holly_base_names[:train_end]
val_holly = selected_holly_base_names[train_end:val_end]
test_holly = selected_holly_base_names[val_end:]

# Create symlinks for selected HollywoodHeads images and annotations, renaming images to .jpg
for base_name in tqdm(selected_holly_base_names, desc="Processing selected HollywoodHeads"):
    # Annotation symlink
    ano_file = f"{base_name}.xml"
    src_ano = os.path.join(holly_ano_dir, ano_file)
    dst_ano = os.path.join(combined_ano_dir, ano_file)
    if os.path.exists(src_ano):
        if not os.path.exists(dst_ano):
            os.symlink(os.path.relpath(src_ano, combined_ano_dir), dst_ano)
        else:
            print(f"Symlink already exists: {dst_ano}")
    else:
        print(f"Annotation not found: {src_ano}")
    
    # Image symlink with .jpeg renamed to .jpg
    src_img_file = f"{base_name}.jpeg"
    dst_img_file = f"{base_name}.jpg"
    src_img = os.path.join(HOLLYWOOD_PATH, 'JPEGImages', src_img_file)
    dst_img = os.path.join(combined_img_dir, dst_img_file)
    if os.path.exists(src_img):
        if not os.path.exists(dst_img):
            os.symlink(os.path.relpath(src_img, combined_img_dir), dst_img)
        else:
            print(f"Symlink already exists: {dst_img}")
    else:
        print(f"Image not found: {src_img}")

# Create combined split files in COMBINED_HEAD/Splits/ with .jpg references
for split in ['train', 'val', 'test']:
    combined_split_file = os.path.join(COMBINED_PATH, 'Splits', f'{split}.txt')
    with open(combined_split_file, 'w') as f:
        # Write SCUT_HEAD base names (filtered for valid XMLs)
        for base_name in scut_splits[split]:
            f.write(base_name + '\n')
        # Write selected HollywoodHeads base names (all valid)
        if split == 'train':
            holly_base_names = train_holly
        elif split == 'val':
            holly_base_names = val_holly
        else:
            holly_base_names = test_holly
        for base_name in holly_base_names:
            f.write(base_name + '\n')

# Create trainval.txt by combining train and val splits
trainval_file = os.path.join(COMBINED_PATH, 'Splits', 'trainval.txt')
with open(trainval_file, 'w') as f:
    for base_name in scut_splits['train'] + scut_splits['val'] + train_holly + val_holly:
        f.write(base_name + '\n')

# Print summary
print(f"SCUT_HEAD (valid only): train={len(scut_splits['train'])}, val={len(scut_splits['val'])}, test={len(scut_splits['test'])}")
print(f"HollywoodHeads selected (valid only): total={len(selected_holly_base_names)}, train={len(train_holly)}, val={len(val_holly)}, test={len(test_holly)}")
print("Dataset combination complete.")