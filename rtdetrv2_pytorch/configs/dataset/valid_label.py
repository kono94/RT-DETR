# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 08:28:53 2018
@author: Peng Dezhi
Modified for SCUT_HEAD dataset
"""

import xml.etree.ElementTree as ET
import os

def valid_annotation_label(filename, labelname):
    tree = ET.parse(filename)
    objs = tree.findall('object')
    
    if not objs:  # Handle empty annotations
        print(f"Warning: {filename} has no objects")
        return False

    for obj in objs:
        name = obj.find('name').text
        if name != labelname:
            print(f"Found unexpected label '{name}' in {filename}")
            return False
        
    return True

def get_unique_labels(anno_dir):
    unique_labels = set()
    for filename in os.listdir(anno_dir):
        filepath = os.path.join(anno_dir, filename)
        print(f"Checking file: {filepath}")  # Debug print
        try:
            tree = ET.parse(filepath)
            for obj in tree.findall('object'):
                name = obj.find('name').text
                unique_labels.add(name)
        except ET.ParseError as e:
            print(f"Error parsing {filepath}: {e}")
            continue  # Skip invalid files
    return unique_labels

if __name__ == '__main__':
    anno_dir = './Annotations'  # Adjust to your SCUT_HEAD Annotations path
    filename_list = os.listdir(anno_dir)

    # Print unique labels in the dataset
    print("Unique labels in dataset:", get_unique_labels(anno_dir))

    # Check if all objects are labeled 'head'
    expected_label = 'person'  # Adjust based on SCUT_HEAD annotations
    for filename in filename_list:
        filepath = os.path.join(anno_dir, filename)
        if not valid_annotation_label(filepath, expected_label):
            print(f"File with unexpected labels: {filename}")