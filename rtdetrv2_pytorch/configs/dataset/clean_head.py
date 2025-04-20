import os
import xml.etree.ElementTree as ET

def validate_xml_files(directory):
    """Validate all .xml files in the specified directory.

    Args:
        directory (str): Path to the directory containing .xml files.

    Returns:
        dict: Dictionary with lists of problematic files categorized by issue.
    """
    issues = {
        'empty': [],
        'invalid_xml': [],
        'no_objects': [],
        'malformed_objects': []
    }
    
    for filename in os.listdir(directory):
        if not filename.endswith('.xml'):
            continue
        
        file_path = os.path.join(directory, filename)
        
        # Check for empty file
        if os.path.getsize(file_path) == 0:
            issues['empty'].append(file_path)
            continue
        
        # Try parsing XML
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check for objects
            objects = root.findall('object')
            if not objects:
                issues['no_objects'].append(file_path)
                continue
            
            # Validate object structure
            for obj in objects:
                name = obj.find('name')
                bndbox = obj.find('bndbox')
                if name is None or bndbox is None:
                    issues['malformed_objects'].append(file_path)
                    break
                for coord in ['xmin', 'ymin', 'xmax', 'ymax']:
                    if bndbox.find(coord) is None:
                        issues['malformed_objects'].append(file_path)
                        break
                    try:
                        float(bndbox.find(coord).text)
                    except (TypeError, ValueError):
                        issues['malformed_objects'].append(file_path)
                        break
                else:
                    continue
                break
        
        except ET.ParseError:
            issues['invalid_xml'].append(file_path)
    
    return issues

def print_issues(issues):
    """Print the validation results."""
    print("XML Validation Results:")
    for issue_type, files in issues.items():
        print(f"\n{issue_type.replace('_', ' ').title()}: {len(files)} files")
        for file in files[:5]:  # Show first 5 for brevity
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")

if __name__ == "__main__":
    directory = "./dataset/COMBINED_HEAD/Annotations"
    issues = validate_xml_files(directory)
    print_issues(issues)
    
    # Optionally, save issues to a file
    with open("xml_issues.txt", "w") as f:
        for issue_type, files in issues.items():
            f.write(f"{issue_type.replace('_', ' ').title()}: {len(files)} files\n")
            for file in files:
                f.write(f"  - {file}\n")
            f.write("\n")
    print("\nIssues saved to xml_issues.txt")
