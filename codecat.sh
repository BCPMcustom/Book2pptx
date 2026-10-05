#!/bin/bash

# codecat.sh - Concatenate code files with fancy headers and spacing
# Usage:
#   ./codecat.sh                          (interactive mode)
#   ./codecat.sh output.txt               (output given, prompt for inputs until Ctrl-Z)
#   ./codecat.sh output.txt list.txt      (batch mode: read from list file)
#   ./codecat.sh output.txt list.txt -o   (batch mode: overwrite output file first)
#   ./codecat.sh output.txt -o            (prompt for inputs, overwrite first)

# ============================================================================
# HELPER FUNCTION: Process a single file and append to destination
# ============================================================================
process_file() {
  local source_file="$1"
  local dest_file="$2"
  
  # Resolve full path (handles relative paths, ~, etc.)
  source_file=$(realpath "$source_file" 2>/dev/null)
  
  if [ $? -ne 0 ]; then
    echo "⚠ Warning: Could not resolve '$source_file', skipping."
    return 1
  fi
  
  # Strip path from filename
  filename=$(basename "$source_file")
  
  # Get the length of the filename
  filename_len=${#filename}
  
  # Calculate box width (filename length + 10 for padding)
  box_width=$((filename_len + 10))
  
  # Append to destination file with header
  {
    printf "\n\n"
    printf "%${box_width}s\n" | tr ' ' '~'
    printf "||   %s   ||\n" "$filename"
    printf "%${box_width}s\n" | tr ' ' '~'
    printf "\n\n\n"
    cat "$source_file"
    printf "\n\n\n"
  } >> "$dest_file"
  
  echo "✓ Appended '$filename' to '$dest_file'"
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

overwrite_flag=false
dest_file=""
list_file=""

# Parse arguments and check for -o flag
for arg in "$@"; do
  if [ "$arg" = "-o" ]; then
    overwrite_flag=true
  elif [ -z "$dest_file" ]; then
    dest_file="$arg"
  elif [ -z "$list_file" ]; then
    list_file="$arg"
  fi
done

# ============================================================================
# CASE 1: argv == 0 (fully interactive)
# ============================================================================
if [ $# -eq 0 ]; then
  read -p "Enter the destination file: " dest_file
  
  echo "Add input files: [ENTER for next file. Ctrl-D to EXIT]"
  while read -p "> " source_file; do
    [ -z "$source_file" ] && continue
    process_file "$source_file" "$dest_file"
  done
  
  echo ""
  echo "✓ Processing complete!"
  exit 0
fi

# ============================================================================
# CASE 2: argv == 1 (output file given, prompt for inputs)
# ============================================================================
if [ $# -eq 1 ] || ([ $# -eq 2 ] && [ "$overwrite_flag" = true ]); then
  
  if [ "$overwrite_flag" = true ]; then
    rm -f "$dest_file"
    echo "🔄 Overwriting '$dest_file'..."
  fi
  
  echo "Add input files: [ENTER for next file. Ctrl-Z to EXIT]"
  while read -p "> " source_file; do
    [ -z "$source_file" ] && continue
    process_file "$source_file" "$dest_file"
  done
  
  echo ""
  echo "✓ Processing complete!"
  exit 0
fi

# ============================================================================
# CASE 3: argv == 2 (batch mode: output file + list file)
# ============================================================================
if [ -n "$list_file" ]; then
  
  # Verify list file exists
  if [ ! -f "$list_file" ]; then
    echo "Error: List file '$list_file' not found."
    exit 1
  fi
  
  if [ "$overwrite_flag" = true ]; then
    rm -f "$dest_file"
    echo "🔄 Overwriting '$dest_file'..."
  fi
  
  # Read each line from list file and process
  while IFS= read -r source_file || [ -n "$source_file" ]; do
    [ -z "$source_file" ] && continue
    process_file "$source_file" "$dest_file"
  done < "$list_file"
  
  echo ""
  echo "✓ Batch processing complete!"
  exit 0
fi

# Strip path from filename (everything left of the last '/')
filename=$(basename "$source_file")

# Get the length of the filename
filename_len=${#filename}

# Calculate box width (filename length + 10 for padding)
box_width=$((filename_len + 10))

# Open/append to destination file and add header
{
  printf "\n\n"
  printf "%${box_width}s\n" | tr ' ' '~'
  printf "||   %s   ||\n\n\n\n\n" "$filename"
  cat "$source_file"
  printf "\n\n\n"
} >> "$dest_file"

echo "✓ Appended '$filename' to '$dest_file'"
