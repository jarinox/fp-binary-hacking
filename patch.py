import os
import sys
import shutil
import argparse
from typing import List

from src.ips import IPS
from src.gb import GBFile

def apply_patch(patch_path: str, gb_file: GBFile):
    """Apply an IPS patch to a Game Boy ROM file."""
    try:
        ips = IPS(patch_path)
        print(f"Applying patch: {os.path.basename(patch_path)}")
        
        # Apply each patch in the IPS file
        for patch in ips.patches:
            gb_file.write(patch.offset, patch.data)
        
        print(f"✓ Successfully applied {os.path.basename(patch_path)}")
        return True
    except Exception as e:
        print(f"✗ Failed to apply {os.path.basename(patch_path)}: {e}")
        return False

def load_available_patches() -> dict:
    """Load all available patches from the patches directory."""
    available_patches = {}
    
    if not os.path.exists("patches"):
        print("Error: patches directory not found")
        return available_patches
    
    for filename in os.listdir("patches"):
        if filename.endswith(".ips"):
            patch_name = filename[:-4]  # Remove the .ips extension
            patch_path = os.path.join("patches", filename)
            available_patches[patch_name] = patch_path
    
    return available_patches

def check_patch_conflicts(patch_paths: List[str]) -> bool:
    """Check if selected patches have conflicts."""
    if len(patch_paths) < 2:
        return False
    
    ips_objects = []
    try:
        for path in patch_paths:
            ips_objects.append(IPS(path))
        
        # Check for conflicts between all pairs
        for i in range(len(ips_objects)):
            for j in range(i + 1, len(ips_objects)):
                if ips_objects[i].has_conflict(ips_objects[j]):
                    patch1_name = os.path.basename(patch_paths[i])
                    patch2_name = os.path.basename(patch_paths[j])
                    print(f"⚠ Warning: Conflict detected between {patch1_name} and {patch2_name}")
                    return True
        
        return False
    except Exception as e:
        print(f"Error checking patch conflicts: {e}")
        return False

def show_help():
    """Display help information."""
    help_text = """
Game Boy ROM Patch Manager
==========================

This tool allows you to apply IPS patches to Game Boy ROM files.

Usage:
    python patch.py [options] [patch_names...]

Options:
    -h, --help          Show this help message
    -l, --list          List all available patches
    -a, --all           Apply all available patches
    -i, --interactive   Interactive mode to select patches
    -f, --force         Apply patches even if conflicts are detected
    --input FILE        Input ROM file (default: sod.gb)
    --output FILE       Output ROM file (default: sod.mod.gb)

Examples:
    python patch.py --list
    python patch.py MoonJump FastSkating
    python patch.py --all
    python patch.py --interactive
    python patch.py --input mygame.gb --output mygame_patched.gb MoonJump

Available patches are loaded from the 'patches/' directory.
"""
    print(help_text)

def list_patches(available_patches: dict):
    """List all available patches."""
    if not available_patches:
        print("No patches found in the patches directory.")
        return
    
    print(f"\nAvailable patches ({len(available_patches)}):")
    print("=" * 40)
    for i, patch_name in enumerate(sorted(available_patches.keys()), 1):
        print(f"{i:2}. {patch_name}")
    print()

def interactive_mode(available_patches: dict) -> List[str]:
    """Interactive patch selection mode."""
    if not available_patches:
        print("No patches available.")
        return []
    
    list_patches(available_patches)
    
    selected_patches = []
    patch_list = sorted(available_patches.keys())
    
    while True:
        try:
            user_input = input("\nEnter patch numbers (comma-separated), 'all' for all patches, or 'done' to finish: ").strip()
            
            if user_input.lower() == 'done':
                break
            elif user_input.lower() == 'all':
                selected_patches = list(available_patches.keys())
                break
            elif user_input:
                numbers = [int(x.strip()) for x in user_input.split(',')]
                for num in numbers:
                    if 1 <= num <= len(patch_list):
                        patch_name = patch_list[num - 1]
                        if patch_name not in selected_patches:
                            selected_patches.append(patch_name)
                            print(f"Added: {patch_name}")
                        else:
                            print(f"Already selected: {patch_name}")
                    else:
                        print(f"Invalid patch number: {num}")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return []
    
    return selected_patches


def main():
    """Main function with command line interface."""
    available_patches = load_available_patches()
    
    parser = argparse.ArgumentParser(description='Apply IPS patches to Game Boy ROM files', add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    parser.add_argument('-l', '--list', action='store_true', help='List available patches')
    parser.add_argument('-a', '--all', action='store_true', help='Apply all patches')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive patch selection')
    parser.add_argument('-f', '--force', action='store_true', help='Apply patches even with conflicts')
    parser.add_argument('--input', default='sod.gb', help='Input ROM file (default: sod.gb)')
    parser.add_argument('--output', default='sod.mod.gb', help='Output ROM file (default: sod.mod.gb)')
    parser.add_argument('patches', nargs='*', help='Patch names to apply')
    
    args = parser.parse_args()
    
    # Handle help
    if args.help:
        show_help()
        return
    
    # Handle list patches
    if args.list:
        list_patches(available_patches)
        return
    
    # Determine which patches to apply
    selected_patches = []
    
    if args.all:
        selected_patches = list(available_patches.keys())
    elif args.interactive:
        selected_patches = interactive_mode(available_patches)
    elif args.patches:
        # Validate patch names
        for patch_name in args.patches:
            if patch_name in available_patches:
                selected_patches.append(patch_name)
            else:
                print(f"Error: Patch '{patch_name}' not found.")
                print(f"Available patches: {', '.join(sorted(available_patches.keys()))}")
                return
    else:
        print("No patches specified. Use --help for usage information.")
        return
    
    if not selected_patches:
        print("No patches selected.")
        return
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input ROM file '{args.input}' not found.")
        return
    
    # Get patch paths
    patch_paths = [available_patches[name] for name in selected_patches]
    
    # Check for conflicts
    if not args.force and check_patch_conflicts(patch_paths):
        response = input("Conflicts detected. Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Operation cancelled.")
            return
    
    # Create backup and copy ROM
    try:
        if args.output == args.input:
            backup_name = f"{args.output}.backup"
            print(f"Creating backup: {backup_name}")
            shutil.copyfile(args.output, backup_name)
        
        print(f"Copying {args.input} to {args.output}")
        shutil.copyfile(args.input, args.output)
        
        # Open the ROM file
        gb_file = GBFile(args.output)
        
        # Apply patches
        print(f"\nApplying {len(selected_patches)} patch(es):")
        success_count = 0
        
        for patch_name in selected_patches:
            patch_path = available_patches[patch_name]
            if apply_patch(patch_path, gb_file):
                success_count += 1
        
        print(f"\nCompleted: {success_count}/{len(selected_patches)} patches applied successfully.")
        
        if success_count > 0:
            print(f"Modified ROM saved as: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()

