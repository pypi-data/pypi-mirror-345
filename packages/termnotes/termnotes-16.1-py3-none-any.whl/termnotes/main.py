#!/usr/bin/env python3

from datetime import datetime
import os
import re # Import regular expression module
import shutil
import appdirs
import readline
import pyperclip
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Get the system-specific Notes folder
BASE_DIR = appdirs.user_data_dir("Termnotes", "Termnotes")
# CONFIG_FILE = "config.json" # Not currently used, could be added later
in_folder = None  # Tracks current folder

# Ensure the base directory exists at startup
os.makedirs(BASE_DIR, exist_ok=True)

# --- Utility Functions ---

def check_name(name):
  """
  Checks if a folder or note name already exists (case-insensitive).
  Returns True if the name is available, False otherwise.
  """
  # Case-insensitive check for folders
  found_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and name.lower() == f.lower()]
  found_notes = []

  # Case-insensitive check for notes across all folders
  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      # Check notes within this folder
      notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt") and name.lower() == f.lower().replace(".txt", "")]
      if notes: # If any note matches in this folder
        found_notes.append(True) # Just need to know if *any* note exists with this name
        break # No need to check other folders

  # Name is available if no folder and no note with that name exists
  if not found_folders and not found_notes:
    return True
  return False

def setup():
  """Ensures the base Notes directory exists."""
  # This is now handled by the os.makedirs call at the top level
  # Kept here for potential future setup tasks if needed
  pass

# --- Core Functionality ---

def list_folders():
  """Lists all folders inside the Notes directory, sorted."""
  try:
    folders = sorted([f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))], key=str.lower) # Case-insensitive sort
  except OSError as e:
    print(f"[bold red]Error listing folders: {e}[/bold red]")
    return

  if not folders:
    content = "[dim]└── No folders found. Create one with 'nf name'[/dim]"
  else:
    folder_lines = []
    for i, folder in enumerate(folders):
      prefix = "└──" if i == len(folders) - 1 else "├──"
      folder_lines.append(f"{prefix} [bold]{folder}[/bold] (f)")
    content = "\n".join(folder_lines)

  inner_panel = Panel(content, title="[bold blue]Folders[/bold blue]", expand=True)
  # Panel showing current context (or lack thereof)
  context_panel = Panel("[dim]Currently at root folder level[/dim]", title="", expand=True)

  console.print("\n")
  console.print(inner_panel)
  console.print(context_panel)
  console.print("\n")

def list_notes(folder):
  """Lists all notes inside a specified folder, sorted."""
  folder_path = os.path.join(BASE_DIR, folder)
  if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
    print(f"\n[bold red]Folder '{folder}' not found.[/bold red]\n")
    # Optionally, reset in_folder if it points to a non-existent folder
    global in_folder
    if in_folder == folder:
      in_folder = None
      list_folders() # Go back to folder view
    return

  try:
    notes = sorted([f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")], key=str.lower) # Case-insensitive sort
  except OSError as e:
    print(f"[bold red]Error listing notes in '{folder}': {e}[/bold red]")
    return

  if not notes:
    content = "[dim]└── No notes found. Create one with 'nn name'[/dim]"
  else:
    note_lines = []
    for i, note in enumerate(notes):
      prefix = "└──" if i == len(notes) - 1 else "├──"
      note_lines.append(f"{prefix} [bold]{note}[/bold] (n)")
    content = "\n".join(note_lines)

  # Also list all folders for easy navigation context
  try:
    folders = sorted([f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))], key=str.lower)
  except OSError:
    folders = [] # Handle potential error listing folders

  folder_lines = []
  for i, some_folder in enumerate(folders):
    prefix = "└──" if i == len(folders) - 1 else "├──"
    folder_lines.append(f"{prefix} [bold]{some_folder}[/bold] (f)")
  folder_content = "\n".join(folder_lines) if folder_lines else "[dim]└── No folders[/dim]"

  all_folders_panel = Panel(folder_content, title="[bold blue]All Folders[/bold blue]", expand=True)

  panel_title = f"[bold blue]Notes in: {folder}[/bold blue]"
  folder_panel = Panel(content, title=panel_title, expand=True)

  console.print("\n")
  console.print(all_folders_panel)
  console.print(folder_panel)
  console.print("\n")

def create_folder(name):
  """Creates a new folder inside Notes, checking for name conflicts."""
  if not name:
    print("\n[bold red]Folder name cannot be empty.[/bold red]\n")
    return
  folder_path = os.path.join(BASE_DIR, name)
  if check_name(name): # check_name handles case-insensitivity
    try:
      os.makedirs(folder_path, exist_ok=True)
      print(f"\n[bold green]Folder '{name}' created.[/bold green]\n")
    except OSError as e:
      print(f"\n[bold red]Error creating folder '{name}': {e}[/bold red]\n")
  else:
    print(f"\n[bold red]A folder or note named '{name}' already exists (case-insensitive).[/bold red]\n")

def create_note(folder, name, tags_input, content):
  """Creates a new note inside a folder with plain tags."""
  if not name:
    print("\n[bold red]Note name cannot be empty.[/bold red]\n")
    return

  folder_path = os.path.join(BASE_DIR, folder)
  if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
    print(f"\n[bold red]Folder '{folder}' not found. Cannot create note.[/bold red]\n")
    return

  # --- Process tags plainly ---
  if tags_input.strip():
    lines = tags_input.strip().splitlines()
    # Clean tags: remove whitespace, leading #, ensure not empty, remove duplicates
    cleaned_tags_set = {tag.strip().lstrip('#').strip() for tag in lines if tag.strip().lstrip('#').strip()}
    final_tags_plain = ", ".join(sorted(list(cleaned_tags_set))) # Store sorted unique tags
  else:
    final_tags_plain = ""
  # --- End plain tag processing ---

  # Check if note name (case-insensitive) already exists *within this folder*
  note_filename = f"{name}.txt"
  note_path = os.path.join(folder_path, note_filename)
  name_exists_in_folder = False
  try:
    for existing_file in os.listdir(folder_path):
      if existing_file.lower() == note_filename.lower():
        name_exists_in_folder = True
        break
  except OSError:
     # Handle case where folder might disappear between checks
     print(f"\n[bold red]Error accessing folder '{folder}' while checking note name.[/bold red]\n")
     return

  if not name_exists_in_folder:
    try:
      with open(note_path, "w", encoding='utf-8') as file: # Specify encoding
        # Write the plain tags
        file.write(f"Tags: {final_tags_plain}\n\n")
        file.write(content.strip() + "\n") # Ensure content ends with a newline, but strip excess first
      print(f"\n[bold green]New note '{name}' created in '{folder}'.[/bold green]\n")
    except IOError as e:
      print(f"\n[bold red]Error writing note '{name}': {e}[/bold red]\n")
    except Exception as e:
      print(f"\n[bold red]An unexpected error occurred creating note '{name}': {e}[/bold red]\n")
  else:
    print(f"\n[bold red]A note named '{name}' already exists in '{folder}' (case-insensitive).[/bold red]\n")


def search(query):
  """Searches folders/notes by name, or notes by tag (plain text)."""
  global in_folder
  found_notes_by_name = []
  found_notes_by_tag = {} # Use dict { (folder, note_name) : None } to store unique results
  search_term = query.lower().strip() # Use lowercase, stripped search term

  if not search_term:
    print("\n[bold yellow]Please provide a search term or tag.[/bold yellow]\n")
    return

  # --- Tag Search Logic ---
  if search_term.startswith("#"):
    tag_to_search = search_term[1:].strip().lower()
    if not tag_to_search:
      console.print("\n[bold yellow]Please specify a tag after #.[/bold yellow]\n")
      return

    try:
      for folder in os.listdir(BASE_DIR):
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
          for note_file in os.listdir(folder_path):
            if note_file.endswith(".txt"):
              note_path = os.path.join(folder_path, note_file)
              note_name = note_file[:-4] # More reliable than replace
              try:
                with open(note_path, "r", encoding='utf-8') as f:
                  first_line = f.readline().strip()
                  if first_line.lower().startswith("tags:"):
                    tags_str_plain = first_line[len("tags:"):].strip()
                    note_tags = {tag.strip().lower() for tag in tags_str_plain.split(',') if tag.strip()}
                    if tag_to_search in note_tags:
                      # Store tuple (original case folder, original case note)
                      found_notes_by_tag[(folder, note_name)] = None
              except IOError:
                print(f"[dim]Skipping note {folder}/{note_name} (read error)[/dim]")
              except Exception: # Catch other potential errors reading lines/tags
                 print(f"[dim]Skipping note {folder}/{note_name} (format error)[/dim]")
    except OSError as e:
      print(f"[bold red]Error accessing directories during search: {e}[/bold red]")
      return

    # --- Display Tag Search Results ---
    if found_notes_by_tag:
      results_content = f"[bold blue]Notes found by tag '[i]#{tag_to_search}[/i]':[/bold blue]\n"
      tag_items = sorted(list(found_notes_by_tag.keys()), key=lambda x: (x[0].lower(), x[1].lower())) # Sort results
      for i, (folder, name) in enumerate(tag_items):
        prefix = "└──" if i == len(tag_items) - 1 else "├──"
        results_content += f"{prefix} [bold]{folder}/{name}[/bold] (n)\n"
      results_content = results_content.rstrip()

      results_panel = Panel(results_content, title="[bold green]Tag Search Results[/bold green]")
      console.print("\n")
      console.print(results_panel)

      # --- Tag Search Open Prompt ---
      choice = Prompt.ask("\nType 'o folder/note_name' to open, or 'c' to cancel").strip()
      if choice.lower() == 'c':
        console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
        return
      elif choice.lower().startswith('o '):
        target_spec = choice[2:].strip()
        if '/' not in target_spec:
          print("\n[bold red]Invalid format. Use 'o folder/note_name'.[/bold red]\n")
          return

        try:
          folder_part, note_part = target_spec.split('/', 1)
        except ValueError:
           print("\n[bold red]Invalid format. Use 'o folder/note_name'.[/bold red]\n")
           return

        # Find the exact match from results (case-insensitive comparison)
        match_found = None
        for f_res, n_res in tag_items:
          if f_res.lower() == folder_part.lower() and n_res.lower() == note_part.lower():
            match_found = (f_res, n_res) # Use original case
            break

        if match_found:
          folder_to_open, note_to_open = match_found
          note_file_path = os.path.join(BASE_DIR, folder_to_open, f"{note_to_open}.txt")
          if os.path.exists(note_file_path):
            read_note(folder_to_open, note_to_open)
            in_folder = folder_to_open # Navigate into the folder
          else:
            console.print("\n[bold red]Error: Note file seems missing.[/bold red]\n")
        else:
          console.print(f"\n[bold red]Note '{target_spec}' not found in tag search results.[/bold red]\n")
      else:
        console.print("[bold red]\nInvalid choice.[/bold red]\n")
      return # End tag search

    else: # No tags found
      console.print(f"\n[bold yellow]No notes found with tag '[i]#{tag_to_search}[/i]'.[/bold yellow]\n")
      return


  # --- Name Search Logic (if not tag search) ---
  found_folders_list = []
  found_notes_by_name = [] # List of (folder, note_name) tuples

  try:
    for item in os.listdir(BASE_DIR):
      item_path = os.path.join(BASE_DIR, item)
      # Folder Name Search
      if os.path.isdir(item_path):
        if search_term in item.lower(): # Partial match for folders
          found_folders_list.append(item) # Store original case
        # Note Name Search within this folder
        try:
          for note_file in os.listdir(item_path):
            if note_file.endswith(".txt"):
              note_name = note_file[:-4]
              if search_term in note_name.lower(): # Partial match for notes
                found_notes_by_name.append((item, note_name)) # Store original case (folder, note)
        except OSError:
          print(f"[dim]Could not access items in folder '{item}'[/dim]")
  except OSError as e:
    print(f"[bold red]Error accessing directories during search: {e}[/bold red]")
    return

  # --- Display Name Search Results ---
  if not found_folders_list and not found_notes_by_name:
    console.print(f"\n[bold red]No folders or notes found matching '[i]{query}[/i]'.[/bold red]\n")
    return

  search_results = []
  # Sort results for display
  found_folders_list.sort(key=str.lower)
  found_notes_by_name.sort(key=lambda x: (x[0].lower(), x[1].lower()))

  if found_folders_list:
    search_results.append("[bold blue]Matching Folders:[/bold blue]")
    for i, folder in enumerate(found_folders_list):
      prefix = "└──" if i == len(found_folders_list) - 1 and not found_notes_by_name else "├──"
      search_results.append(f"{prefix} [bold]{folder}[/bold] (f)")

  if found_notes_by_name:
    if found_folders_list: search_results.append("") # Separator
    search_results.append("[bold blue]Matching Notes:[/bold blue]")
    for i, (folder, note) in enumerate(found_notes_by_name):
      prefix = "└──" if i == len(found_notes_by_name) - 1 else "├──"
      search_results.append(f"{prefix} [bold]{folder}/{note}[/bold] (n)")

  results_content = "\n".join(search_results)
  results_panel = Panel(
    results_content, title=f"[bold green]Name Search Results for '[i]{query}[/i]'[/bold green]"
  )
  console.print("\n")
  console.print(results_panel)

  # --- Name Search Open Prompt ---
  prompt_text = "Type 'o folder_name' or 'o folder/note_name' to open, or 'c' to cancel"
  choice = Prompt.ask(f"\n{prompt_text}").strip()

  if choice.lower() == 'c':
    console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
  elif choice.lower().startswith('o '):
    target_name = choice[2:].strip()
    opened = False

    # Check if target is a folder name (case-insensitive match)
    if '/' not in target_name:
      for folder in found_folders_list:
        if folder.lower() == target_name.lower():
          folder_path = os.path.join(BASE_DIR, folder)
          if os.path.isdir(folder_path): # Double check exists
             in_folder = folder # Use original case
             list_notes(in_folder)
             opened = True
             break
          else: # Should not happen if listdir worked, but be safe
             print(f"\n[bold red]Error: Folder '{folder}' seems missing now.[/bold red]\n")
             opened = True # Prevent further checks
             break

    # Check if target is folder/note name (case-insensitive match)
    if not opened and '/' in target_name:
      try:
        target_folder_part, target_note_part = target_name.split('/', 1)
        for f_res, n_res in found_notes_by_name:
          if f_res.lower() == target_folder_part.lower() and n_res.lower() == target_note_part.lower():
            note_path = os.path.join(BASE_DIR, f_res, f"{n_res}.txt")
            if os.path.isfile(note_path): # Check exists
               read_note(f_res, n_res) # Use original case
               in_folder = f_res # Use original case
               opened = True
               break
            else:
               print(f"\n[bold red]Error: Note '{f_res}/{n_res}' seems missing now.[/bold red]\n")
               opened = True # Prevent further checks
               break
      except ValueError:
        # Split failed, invalid format handled below
        pass

    if not opened:
      console.print(f"\n[bold red]Could not find exact match for '{target_name}' in search results. Use format 'folder_name' or 'folder/note_name'.[/bold red]\n")

  else:
    console.print("[bold red]\nInvalid choice.[/bold red]\n")


def read_note(folder, name):
  """Reads and displays a note, applying styling dynamically."""
  note_path = os.path.join(BASE_DIR, folder, f"{name}.txt")
  word_count = 0

  if not os.path.exists(note_path) or not os.path.isfile(note_path):
    console.print(f"\n[bold red]Note '{name}' not found in '{folder}'.[/bold red]\n")
    return

  try:
    with open(note_path, "r", encoding='utf-8') as file:
      all_lines = file.readlines()
  except IOError as e:
    console.print(f"\n[bold red]Error reading note '{name}': {e}[/bold red]\n")
    return
  except Exception as e:
    console.print(f"\n[bold red]An unexpected error occurred reading note '{name}': {e}[/bold red]\n")
    return

  tags_line_styled = ""
  content_start_index = 0

  # --- Dynamically Style Tags for Display ---
  if all_lines and all_lines[0].lower().startswith("tags:"):
    tags_str_plain = all_lines[0][len("tags:"):].strip()
    if tags_str_plain:
      plain_tags = [tag.strip() for tag in tags_str_plain.split(',') if tag.strip()]
      styled_tags = [f"[bold pale_violet_red1]#{tag}[/bold pale_violet_red1]" for tag in plain_tags]
      tags_line_styled = "Tags: " + ", ".join(styled_tags)
    else:
      tags_line_styled = "Tags: [dim]none[/dim]"
    content_start_index = 1
    if len(all_lines) > 1 and all_lines[1].strip() == "":
      content_start_index = 2 # Skip blank line after tags
  else:
    # Handle notes potentially created without the standard Tags line
    tags_line_styled = "[dim]Tags: (not specified)[/dim]"
    content_start_index = 0 # Assume content starts from first line
  # --- End Dynamic Tag Styling ---

  words = []
  modified_content_lines = []

  # Process actual content lines
  for line_num in range(content_start_index, len(all_lines)):
    line = all_lines[line_num].rstrip() # Keep leading whitespace, remove trailing
    words.extend(line.split()) # Basic word count

    # Apply Markdown styling
    if line.lstrip().startswith("#"): # Allow indented headers
      header_text = line.lstrip('#').strip()
      modified_line = f"[bold]{header_text}[/bold]"
    elif line.lstrip().startswith("-[]"):
       todo_text = line.split("-[]", 1)[1].strip()
       indent = line[:line.find("-[]")]
       modified_line = f"{indent}[bold red]☐[/bold red] {todo_text}"
    elif line.lstrip().startswith("-[+]"):
       done_text = line.split("-[+]", 1)[1].strip()
       indent = line[:line.find("-[+]")]
       modified_line = f"{indent}[bold green]☑[/bold green] {done_text}"
    elif line.lstrip().startswith("- "):
       item_text = line.split("- ", 1)[1].strip()
       indent = line[:line.find("- ")]
       modified_line = f"{indent}• {item_text}"
    else:
      modified_line = line # Keep original line if no markdown match

    modified_content_lines.append(modified_line)

  word_count = len(words)

  # Construct final display content
  display_content = tags_line_styled + "\n\n" + "\n".join(modified_content_lines)

  title = f"[bold blue]{name} | {word_count} words[/bold blue]"

  # --- Folder Panel for context ---
  folder_path = os.path.join(BASE_DIR, folder)
  try:
    notes_in_folder = sorted([f[:-4] for f in os.listdir(folder_path) if f.endswith(".txt")], key=str.lower)
  except OSError:
    notes_in_folder = []

  note_lines = []
  for i, note in enumerate(notes_in_folder):
    prefix = "└──" if i == len(notes_in_folder) - 1 else "├──"
    # Highlight the currently open note
    style = "[bold magenta]" if note == name else "[bold]"
    note_lines.append(f"{prefix} {style}{note}{style} (n)")

  folder_content = "\n".join(note_lines) if note_lines else "[dim]└── No notes in this folder[/dim]"
  folder_title = f"[bold blue]Current Folder: {folder}[/bold blue]"
  folder_panel = Panel(folder_content, title=folder_title, expand=True)
  # --- Note Panel ---
  note_panel = Panel(display_content, title=title, expand=True)

  console.print("\n")
  console.print(folder_panel)
  console.print(note_panel)
  console.print("\n")


def delete_note_or_folder(name, is_folder):
  """Deletes a note or folder with confirmation."""
  path = ""
  item_type = ""
  display_name = name # Name used in messages

  if is_folder:
    path = os.path.join(BASE_DIR, name)
    item_type = "Folder"
  elif in_folder: # Deleting a note within the current folder
    # Allow deleting even if name doesn't end with .txt in command
    base_name = name if name.endswith(".txt") else f"{name}.txt"
    path = os.path.join(BASE_DIR, in_folder, base_name)
    item_type = "Note"
    display_name = name.replace(".txt", "") # Use name without extension for messages
  else:
    print("\n[bold red]Cannot delete note: Not inside a folder.[/bold red]\n")
    return

  if not os.path.exists(path):
    # Check if it's a case mismatch before declaring not found
    found_case_insensitive = False
    actual_name = None
    target_dir = BASE_DIR if is_folder else os.path.join(BASE_DIR, in_folder)
    try:
      for item in os.listdir(target_dir):
        if item.lower() == os.path.basename(path).lower():
           found_case_insensitive = True
           actual_name = item.replace(".txt","") if item_type=="Note" else item
           break
    except OSError: pass # Ignore listing error here

    if found_case_insensitive:
      print(f"\n[bold red]{item_type} '{display_name}' not found. Did you mean '[i]{actual_name}[/i]'? (Deletion is case-sensitive)[/bold red]\n")
    else:
      print(f"\n[bold red]{item_type} '{display_name}' not found.[/bold red]\n")
    return

  # Confirmation prompt
  confirm = Prompt.ask(f"\n[bold yellow]Permanently delete {item_type.lower()} '{display_name}'? (y/n)[/bold yellow]", choices=["y", "n"], default="n")

  if confirm.lower() == 'y':
    try:
      if is_folder and os.path.isdir(path):
        shutil.rmtree(path)
        print(f"\n[bold green]Folder '{display_name}' deleted.[/bold green]\n")
        # If the deleted folder was the current 'in_folder', reset it
        global in_folder
        if in_folder == display_name:
          in_folder = None # Reset global in_folder
      elif not is_folder and os.path.isfile(path):
        os.remove(path)
        print(f"\n[bold green]Note '{display_name}' deleted from '{in_folder}'.[/bold green]\n")
      else:
        # This case might occur if the item type changed between check and delete
        print(f"\n[bold red]Error: '{display_name}' is not a {item_type.lower()} or was already deleted.[/bold red]\n")
    except OSError as e:
      print(f"\n[bold red]Error deleting {item_type.lower()} '{display_name}': {e}[/bold red]\n")
    except Exception as e:
       print(f"\n[bold red]An unexpected error occurred during deletion: {e}[/bold red]\n")
  else:
    print("\nDeletion cancelled.\n")

def edit_note_or_folder(name):
  """Edits a note (rename, tags, content) or renames a folder."""
  global in_folder

  # --- Editing a Note ---
  if in_folder:
    original_note_name = name
    note_filename = name if name.endswith(".txt") else f"{name}.txt"
    note_path = os.path.join(BASE_DIR, in_folder, note_filename)
    display_name = original_note_name.replace(".txt", "")

    # Case-sensitive check for existence
    if not os.path.exists(note_path) or not os.path.isfile(note_path):
      print(f"\n[bold red]Note '{display_name}' not found in '{in_folder}'. (Edit is case-sensitive)[/bold red]\n")
      # Suggest close matches if any? (Could be added)
      return

    current_name = display_name # Name without extension

    # --- Step 1: Rename Note (Optional) ---
    new_name_input = Prompt.ask(f"\nEnter new name for note '{current_name}' (or press Enter to keep)", default=current_name).strip()

    if new_name_input and new_name_input != current_name:
      # Check if new name conflicts within the *same* folder (case-insensitive)
      new_filename_check = f"{new_name_input}.txt"
      conflict_exists = False
      try:
         for item in os.listdir(os.path.join(BASE_DIR, in_folder)):
            if item.lower() == new_filename_check.lower():
               conflict_exists = True
               break
      except OSError:
          print(f"[bold red]Error checking folder '{in_folder}' for rename conflict.[/bold red]")
          conflict_exists = True # Prevent rename on error

      if conflict_exists:
        print(f"\n[bold red]A note named '{new_name_input}' already exists in '{in_folder}' (case-insensitive). Rename aborted.[/bold red]\n")
      else:
        try:
          new_path = os.path.join(BASE_DIR, in_folder, new_filename_check)
          os.rename(note_path, new_path)
          print(f"\n[bold green]Note renamed to '{new_name_input}'.[/bold green]")
          current_name = new_name_input # Update name for subsequent steps
          note_path = new_path     # Update path for reading/writing
        except OSError as e:
          print(f"\n[bold red]Error renaming note: {e}[/bold red]\n")
          # Keep original name and path if rename fails

    # --- Step 2: Edit Tags (Plain Text) ---
    try:
      with open(note_path, "r", encoding='utf-8') as f:
        all_lines_edit = f.readlines()
    except IOError as e:
      print(f"\n[bold red]Error reading note '{current_name}' for editing: {e}[/bold red]\n")
      return
    except Exception as e:
       print(f"\n[bold red]Unexpected error reading note '{current_name}': {e}[/bold red]\n")
       return

    old_tags_list = []
    content_start_index_edit = 0

    # Find existing tags and content start
    if all_lines_edit and all_lines_edit[0].lower().startswith("tags:"):
      tags_str_plain = all_lines_edit[0][len("tags:"):].strip()
      if tags_str_plain:
        # Get unique tags, preserving order somewhat (by using split then set then list)
        old_tags_list = list(dict.fromkeys([tag.strip() for tag in tags_str_plain.split(',') if tag.strip()]))
      content_start_index_edit = 1
      if len(all_lines_edit) > 1 and all_lines_edit[1].strip() == "":
        content_start_index_edit = 2
    else:
      print("[yellow]Note does not have a standard 'Tags:' line. Tags can be added/edited.[/yellow]")

    new_tags = old_tags_list[:] # Work on a copy

    # Tag editing loop
    while True:
      console.print(f"\n[bold blue]Current tags:[/bold blue] {', '.join(new_tags) if new_tags else '[dim]none[/dim]'}")
      command = console.input("[bold blue]Edit tags:[/bold blue]\n'a <tag>' add | 'd <tag>' delete | 'r <old> <new>' replace | 'clear' | 'skip'\n[bold blue]cmd: [/bold blue]").strip().lower()

      if command == "skip":
        break
      elif command.startswith("a "):
        tag_to_add = command[2:].strip().lstrip('#').strip() # Clean input tag
        if not tag_to_add:
           print("[yellow]Please provide a tag name to add.[/yellow]")
           continue
        # Add if not already present (case-insensitive check)
        tag_exists = any(t.lower() == tag_to_add.lower() for t in new_tags)
        if not tag_exists:
          new_tags.append(tag_to_add)
          print(f"[green]Tag '{tag_to_add}' added.[/green]")
        else:
          print(f"[yellow]Tag '{tag_to_add}' (or similar case) already exists.[/yellow]")
      elif command.startswith("d "):
        tag_to_del_input = command[2:].strip().lstrip('#').strip()
        if not tag_to_del_input:
           print("[yellow]Please provide a tag name to delete.[/yellow]")
           continue
        original_len = len(new_tags)
        # Case-insensitive delete
        new_tags = [t for t in new_tags if t.lower() != tag_to_del_input.lower()]
        if len(new_tags) < original_len:
          print(f"[green]Tag '{tag_to_del_input}' (and similar case) deleted.[/green]")
        else:
          print(f"[yellow]Tag '{tag_to_del_input}' not found.[/yellow]")
      elif command.startswith("r "):
        parts = command[2:].split(maxsplit=1)
        if len(parts) == 2:
          old_tag_input = parts[0].strip().lstrip('#').strip()
          new_tag_input = parts[1].strip().lstrip('#').strip()
          if not old_tag_input or not new_tag_input:
            print("[yellow]Usage: r <old_tag> <new_tag>[/yellow]")
            continue

          # Find index of old tag (case-insensitive)
          old_tag_index = -1
          for i, t in enumerate(new_tags):
            if t.lower() == old_tag_input.lower():
              old_tag_index = i
              break

          if old_tag_index != -1:
            # Check if new tag conflicts (case-insensitive, excluding self)
            new_tag_conflict = any(t.lower() == new_tag_input.lower() and i != old_tag_index for i, t in enumerate(new_tags))
            if new_tag_conflict:
               print(f"[yellow]Tag '{new_tag_input}' (or similar case) already exists. Cannot replace.[/yellow]")
            else:
               replaced_tag = new_tags[old_tag_index] # Get original case
               new_tags[old_tag_index] = new_tag_input # Replace with new input
               print(f"[green]Tag '{replaced_tag}' replaced with '{new_tag_input}'.[/green]")
          else:
            print(f"[yellow]Tag '{old_tag_input}' not found.[/yellow]")
        else:
          print("[yellow]Usage: r <old_tag> <new_tag>[/yellow]")
      elif command == "clear":
        if new_tags:
          new_tags = []
          print("[green]All tags cleared.[/green]")
        else:
          print("[yellow]No tags to clear.[/yellow]")
      else:
        print("[red]Invalid command.[/red]")

    # Prepare final tags line (plain, sorted unique)
    final_tags_plain = ", ".join(sorted(list(set(new_tags)), key=str.lower)) # Ensure unique and sorted
    final_tags_line = f"Tags: {final_tags_plain}\n"

    # --- Step 3: Edit Content ---
    print(f"\n[bold blue]Editing content for '{current_name}':[/bold blue]")
    # Extract current content lines correctly based on where they started
    current_content_lines = [line.rstrip('\n') for line in all_lines_edit[content_start_index_edit:]]
    new_content_lines = current_content_lines[:] # Edit a copy

    # Content editing loop
    while True:
      print("-" * 20)
      if not new_content_lines:
        print("[dim](Note content is empty)[/dim]")
      else:
        for i, line in enumerate(new_content_lines):
          print(f"{i+1}: {line}")
      print("-" * 20)

      command = console.input("[bold blue]Edit content:[/bold blue]\n'<num>' edit | 'a' append | 'i <num>' insert | 'd <num>' delete | 'c <num>' copy | 'save'\n[bold blue]cmd: [/bold blue]").strip()

      if command.lower() == "save":
        break
      elif command.lower() == "a":
        print("\nEnter lines ('EOF' or Ctrl+D on empty line to finish):")
        while True:
          try:
            # Use standard input, allows pasting multiline text easily
            new_line = input()
            new_content_lines.append(new_line)
          except EOFError:
            print("\n[dim](EOF detected, finished appending)[/dim]")
            break # Exit append loop
      elif command.isdigit():
        try:
          line_number = int(command) - 1
          if 0 <= line_number < len(new_content_lines):
            print(f"Current {line_number+1}: {new_content_lines[line_number]}")
            edited_line = Prompt.ask("New text", default=new_content_lines[line_number])
            new_content_lines[line_number] = edited_line
          else: print("[red]Invalid line number.[/red]")
        except ValueError: print("[red]Invalid number format.[/red]")
      elif command.lower().startswith("i ") and command[2:].isdigit():
        try:
          line_number = int(command[2:]) - 1
          if 0 <= line_number <= len(new_content_lines): # Allow insert at end
            new_line = input(f"Insert before line {line_number + 1}: ")
            new_content_lines.insert(line_number, new_line)
          else: print("[red]Invalid insert line number.[/red]")
        except ValueError: print("[red]Invalid number format.[/red]")
      elif command.lower().startswith("d ") and command[2:].isdigit():
        try:
          line_number = int(command[2:]) - 1
          if 0 <= line_number < len(new_content_lines):
            deleted = new_content_lines.pop(line_number)
            print(f"[green]Line {line_number + 1} deleted.[/green]")
          else: print("[red]Invalid line number.[/red]")
        except ValueError: print("[red]Invalid number format.[/red]")
      elif command.lower().startswith("c ") and command[2:].isdigit():
        try:
          line_number = int(command[2:]) - 1
          if 0 <= line_number < len(new_content_lines):
            pyperclip.copy(new_content_lines[line_number])
            print(f"[green]Line {line_number + 1} copied.[/green]")
          else: print("[red]Invalid line number.[/red]")
        except ValueError: print("[red]Invalid number format.[/red]")
        except pyperclip.PyperclipException: print("[yellow]Could not copy (clipboard unavailable?).[/yellow]")
        except Exception as e: print(f"[red]Error copying: {e}[/red]")
      else:
        print("[red]Invalid command.[/red]")

    # --- Step 4: Save Updated Note ---
    try:
      with open(note_path, "w", encoding='utf-8') as file:
        file.write(final_tags_line)
        # Add blank line only if content exists
        if new_content_lines or (content_start_index_edit == 1 and len(all_lines_edit) > 1): # Handle empty content case
             file.write("\n")
        # Write content lines, ensuring each ends with exactly one newline
        file.writelines(line + "\n" for line in new_content_lines)
      print(f"\n[bold green]Note '{current_name}' updated successfully.[/bold green]\n")
    except IOError as e:
      print(f"\n[bold red]Error saving updated note '{current_name}': {e}[/bold red]\n")
    except Exception as e:
      print(f"\n[bold red]An unexpected error occurred saving note '{current_name}': {e}[/bold red]\n")

  # --- Renaming a Folder ---
  else:
    original_folder_name = name
    folder_path = os.path.join(BASE_DIR, original_folder_name)

    # Case-sensitive check for existence
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
      print(f"\n[bold red]Folder '{original_folder_name}' not found. (Rename is case-sensitive)[/bold red]\n")
      return

    new_name = Prompt.ask(f"\nEnter new name for folder '{original_folder_name}'", default=original_folder_name).strip()

    if not new_name:
      print("\n[yellow]Folder rename cancelled (no name provided).[/yellow]\n")
      return
    if new_name == original_folder_name:
      print("\n[yellow]Folder name unchanged.[/yellow]\n")
      return

    # Check for conflicts (case-insensitive using check_name utility)
    if not check_name(new_name):
      print(f"\n[bold red]Cannot rename: '{new_name}' already exists as a folder or note (case-insensitive).[/bold red]\n")
      return

    # Perform rename
    try:
      new_folder_path = os.path.join(BASE_DIR, new_name)
      os.rename(folder_path, new_folder_path)
      print(f"\n[bold green]Folder renamed from '{original_folder_name}' to '{new_name}'.[/bold green]\n")
    except OSError as e:
      print(f"\n[bold red]Error renaming folder: {e}[/bold red]\n")
    except Exception as e:
      print(f"\n[bold red]An unexpected error occurred renaming folder: {e}[/bold red]\n")

def move_note_or_folder(source_spec, destination_folder):
  """Moves a note to a destination folder."""
  source_spec = source_spec.strip()
  destination_folder = destination_folder.strip()

  if not source_spec or not destination_folder:
     print("\n[bold red]Usage: mv <source> <destination_folder>[/bold red]\nSource can be 'note' (if in folder) or 'folder/note'.")
     return

  source_folder = None
  source_note_name = None
  note_display_name = None

  # Determine source folder and note name from spec
  if '/' in source_spec:
    try:
      source_folder, note_display_name = source_spec.split('/', 1)
    except ValueError:
      print("\n[bold red]Invalid source format. Use 'folder/note'.[/bold red]\n")
      return
  elif in_folder:
    source_folder = in_folder
    note_display_name = source_spec
  else:
    print("\n[bold red]Source folder unclear. Specify as 'folder/note' or enter the source folder first.[/bold red]\n")
    return

  # Ensure note name and get filename
  note_filename = note_display_name if note_display_name.endswith(".txt") else f"{note_display_name}.txt"
  source_folder_path = os.path.join(BASE_DIR, source_folder)
  source_path = os.path.join(source_folder_path, note_filename)

  destination_dir_path = os.path.join(BASE_DIR, destination_folder)
  destination_path = os.path.join(destination_dir_path, note_filename) # Keep original filename

  # --- Validations ---
  if not os.path.exists(source_path) or not os.path.isfile(source_path):
    print(f"\n[bold red]Source note '{source_folder}/{note_display_name}' not found (check case and path).[/bold red]\n")
    return

  if not os.path.exists(destination_dir_path) or not os.path.isdir(destination_dir_path):
    # Try to find case-insensitive match for destination folder
    actual_dest = None
    try:
      for item in os.listdir(BASE_DIR):
         if os.path.isdir(os.path.join(BASE_DIR,item)) and item.lower() == destination_folder.lower():
            actual_dest = item
            break
    except OSError: pass

    if actual_dest:
       print(f"\n[bold red]Destination folder '{destination_folder}' not found. Did you mean '[i]{actual_dest}[/i]'? (Move is case-sensitive)[/bold red]\n")
    else:
       print(f"\n[bold red]Destination folder '{destination_folder}' not found.[/bold red]\n")
    return

  # Check if file already exists at destination (case-insensitive check)
  dest_conflict = False
  try:
      for item in os.listdir(destination_dir_path):
         if item.lower() == note_filename.lower():
            dest_conflict = True
            break
  except OSError:
      print(f"[bold red]Error accessing destination folder '{destination_folder}' contents.[/bold red]")
      return # Abort on error

  if dest_conflict:
    print(f"\n[bold red]A note named '{note_display_name}' already exists in '{destination_folder}' (case-insensitive). Move aborted.[/bold red]\n")
    return

  # Prevent moving to the same location
  if os.path.abspath(source_path).lower() == os.path.abspath(destination_path).lower():
    print(f"\n[bold yellow]Source and destination are the same folder. No move needed.[/bold yellow]\n")
    return

  # --- Perform Move ---
  try:
    shutil.move(source_path, destination_path)
    print(f"\n[bold green]Note '{note_display_name}' moved from '{source_folder}' to '{destination_folder}'.[/bold green]\n")
  except OSError as e:
    print(f"\n[bold red]Error moving note: {e}[/bold red]\n")
  except Exception as e:
    print(f"\n[bold red]An unexpected error occurred moving note: {e}[/bold red]\n")


def run():
  """Main application loop."""
  setup() # Ensure base directory exists
  global in_folder # Allow modification

  # --- Welcome Message ---
  console.print(Panel(r"""[bold cyan]
   █████████╗███████╗██████╗ ███╗   ███╗ ████████╗███████╗ ████████╗███████╗
   ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║ ╚══██╔══╝██╔════╝ ╚══██╔══╝██╔════╝
      ██║   ███████╗██████╔╝██╔████╔██║    ██║   ███████╗    ██║   ███████╗
      ██║   ╚════██║██╔══██╗██║╚██╔╝██║    ██║   ╚════██║    ██║   ╚════██║
      ██║   ███████║██║  ██║██║ ╚═╝ ██║    ██║   ███████║    ██║   ███████║
      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝   ╚══════╝    ╚═╝   ╚══════╝
  [/bold cyan]""", border_style="blue", title="[white]Termnotes[/white]"))
  print("\nType 'help' for commands.")

  # --- Quick Note Logic ---
  quick_note_folder = "quick_notes"
  try:
    quick_folder_path = os.path.join(BASE_DIR, quick_note_folder)
    if not os.path.exists(quick_folder_path):
      print(f"[dim]Creating default '{quick_note_folder}' folder...[/dim]")
      # Use create_folder to show success/error message
      create_folder(quick_note_folder)

    # Ask user about quick note
    open_quick_note = Prompt.ask("\n[bold yellow]Create a quick note now? (y/n)[/bold yellow]", choices=["y", "n"], default="n")

    if open_quick_note.lower() == 'y':
      in_folder = quick_note_folder # Enter quick notes folder
      list_notes(in_folder) # Show existing quick notes first
      # Generate unique name
      quick_note_name = f'QN_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
      quick_tags = "" # No tags needed initially

      print("\nQuick Note content (type 'SAVE' on a new line to finish):")
      quick_content_lines = []
      while True:
        try:
          line = input()
          # Use uppercase SAVE to minimize conflict with content
          if line.strip() == "SAVE":
            break
          quick_content_lines.append(line)
        except EOFError: # Allow Ctrl+D
          print("\n[dim](EOF detected, saving quick note)[/dim]")
          break
      quick_content = "\n".join(quick_content_lines)

      if quick_content.strip(): # Save only if content exists
        create_note(in_folder, quick_note_name, quick_tags, quick_content)
        read_note(in_folder, quick_note_name) # Display the new note
      else:
        console.print("\n[bold yellow]Quick note empty, not saved.[/bold yellow]\n")
        # If aborted, decide where to go. Back to root is sensible.
        in_folder = None
        list_folders()

    else: # User chose 'n' for quick note
      in_folder = None # Start at root
      list_folders()

  except Exception as e:
    print(f"[bold red]Error during startup or quick note setup: {e}[/bold red]")
    in_folder = None # Ensure safe state on error
    list_folders()

  # --- Main Command Loop ---
  while True:
    # Dynamic prompt based on current context
    prompt_prefix = f"[bold blue]{in_folder}> [/bold blue]" if in_folder else "[bold blue]/> [/bold blue]"
    try:
      choice = console.input(prompt_prefix).strip()
    except (KeyboardInterrupt, EOFError):
       print("\n\n[bold yellow]Ctrl+C or Ctrl+D detected. Use 'q' to quit.[/bold yellow]\n")
       continue # Go back to prompt

    if not choice: continue # Ignore empty input

    command_parts = choice.split(maxsplit=1)
    command = command_parts[0].lower()
    # args should default to empty string if no arguments provided
    args = command_parts[1].strip() if len(command_parts) > 1 else ""

    try: # Wrap command processing in try-except
      # --- Navigation ---
      if command == "o":
        if not args:
          print("\n[bold red]Usage: o <folder_name | note_name>[/bold red]\n")
          continue
        name = args
        if in_folder: # Try opening note (case-sensitive)
          note_filename = name if name.endswith(".txt") else f"{name}.txt"
          note_file_path = os.path.join(BASE_DIR, in_folder, note_filename)
          if os.path.exists(note_file_path) and os.path.isfile(note_file_path):
            read_note(in_folder, name.replace(".txt","")) # Use name without ext for read_note
          else:
            print(f"\n[bold red]Note '{name.replace('.txt','')}' not found in '{in_folder}'. (Open is case-sensitive)[/bold red]\n")
        else: # Try opening folder (case-sensitive)
          folder_path = os.path.join(BASE_DIR, name)
          if os.path.exists(folder_path) and os.path.isdir(folder_path):
            in_folder = name
            list_notes(name)
          else:
            print(f"\n[bold red]Folder '{name}' not found. (Open is case-sensitive)[/bold red]\n")

      elif command == "b":
        if in_folder:
          in_folder = None
          list_folders()
        else:
          print("\n[yellow]Already at the root folder level.[/yellow]\n")

      elif command == "l":
        if in_folder: list_notes(in_folder)
        else: list_folders()

      # --- Creation ---
      elif command == "nf":
        if not args:
          print("\n[bold red]Usage: nf <folder_name>[/bold red]\n")
          continue
        if in_folder:
          print("\n[bold yellow]Create folders only from the root directory (use 'b' first).[/bold yellow]\n")
          continue
        create_folder(args) # Handles checks and printing
        list_folders() # Refresh view

      elif command == "nn":
        if not args:
          print("\n[bold red]Usage: nn <note_name>[/bold red]\n")
          continue
        if not in_folder:
          print("\n[bold red]Must be inside a folder to create a note ('o folder_name').[/bold red]\n")
          continue
        name = args

        # --- Tag Input ---
        print("\nNote tags (one per line, 'SAVE' or Ctrl+D on empty line):")
        tags_lines = []
        while True:
          try:
            line = input("> ")
            if line.strip() == "SAVE": break
            tags_lines.append(line)
          except EOFError: break
        tags_input = "\n".join(tags_lines)

        # --- Content Input ---
        print("\nNote content ('SAVE' or Ctrl+D on empty line):")
        content_lines = []
        while True:
          try:
            line = input()
            if line.strip() == "SAVE": break
            content_lines.append(line)
          except EOFError: break
        content_input = "\n".join(content_lines)

        create_note(in_folder, name, tags_input, content_input) # Handles checks
        list_notes(in_folder) # Refresh

      # --- Deletion / Editing / Moving ---
      elif command == "d":
        if not args:
          print("\n[bold red]Usage: d <folder_name | note_name>[/bold red]\n")
          continue
        delete_note_or_folder(args, is_folder=(not in_folder)) # Context determines type
        # Refresh view after potential deletion
        if in_folder and not os.path.exists(os.path.join(BASE_DIR, in_folder)):
          in_folder = None # Reset if current folder deleted
          list_folders()
        elif in_folder:
          list_notes(in_folder)
        else:
          list_folders()

      elif command == "e":
        if not args:
          print("\n[bold red]Usage: e <folder_name | note_name>[/bold red]\n")
          continue
        edit_note_or_folder(args) # Handles folder/note context internally
        # Refresh view after edit
        if in_folder: list_notes(in_folder)
        else: list_folders()

      elif command == "mv":
        mv_args = args.split(maxsplit=1)
        if len(mv_args) != 2:
          print("\n[bold red]Usage: mv <source> <destination_folder>[/bold red]\n"
                "Example: mv mynote drafts  (if in source folder)\n"
                "Example: mv proj/plan work (from root)")
          continue
        source, destination = mv_args
        move_note_or_folder(source, destination) # Handles path logic, validation
        # Refresh view after potential move
        if in_folder: list_notes(in_folder)
        else: list_folders()

      # --- Search ---
      elif command == "s":
        if not args:
          print("\n[bold red]Usage: s <search_term | #tag>[/bold red]\n")
          continue
        search(args) # Search handles its own output and potential navigation

      # --- Special Notes ---
      elif command == "dn":
        daily_folder = "dailys"
        daily_folder_path = os.path.join(BASE_DIR, daily_folder)
        if not os.path.exists(daily_folder_path):
          create_folder(daily_folder) # Create if missing
          list_folders() # Show updated list before potentially entering

        # Ensure we are in the dailys folder
        if in_folder != daily_folder:
          in_folder = daily_folder
          print(f"\n[bold green]Switched to '{daily_folder}' folder.[/bold green]")
          list_notes(in_folder) # Show notes in dailys

        daily_note_name = datetime.today().strftime('%Y-%m-%d')
        daily_note_path = os.path.join(daily_folder_path, f"{daily_note_name}.txt")

        if os.path.exists(daily_note_path):
          print(f"\n[yellow]Daily note '{daily_note_name}' already exists. Opening.[/yellow]")
          read_note(daily_folder, daily_note_name)
        else:
          print(f"\nCreating new daily note: '{daily_note_name}'")
          # Minimal prompts for daily note
          print("Tags (optional, one per line, 'SAVE' or Ctrl+D):")
          tags_lines = []
          while True:
            try:
              line = input("> ")
              if line.strip() == "SAVE": break
              tags_lines.append(line)
            except EOFError: break
          tags_input = "\n".join(tags_lines)

          print("\nContent ('SAVE' or Ctrl+D):")
          content_lines = []
          while True:
            try:
              line = input()
              if line.strip() == "SAVE": break
              content_lines.append(line)
            except EOFError: break
          content_input = "\n".join(content_lines)

          create_note(daily_folder, daily_note_name, tags_input, content_input)
          read_note(daily_folder, daily_note_name) # Show the new note

      # --- Help / Meta ---
      elif command == "help":
        console.print("\n[bold blue]Termnotes Commands:[/bold blue]\n\n"
                      " [bold]Navigation:[/bold]\n"
                      "   o <name>        Open folder or note (case-sensitive)\n"
                      "   l               List folders (root) or notes (in folder)\n"
                      "   b               Go back to root folder list\n\n"
                      " [bold]Creation:[/bold]\n"
                      "   nf <name>       New Folder (at root)\n"
                      "   nn <name>       New Note (in current folder)\n"
                      "   dn              Create/Open today's Daily Note in 'dailys'\n\n"
                      " [bold]Modification:[/bold]\n"
                      "   d <name>        Delete folder or note (confirm, case-sensitive)\n"
                      "   e <name>        Edit folder or note (case-sensitive)\n"
                      "   mv <src> <dest> Move note <src> to <dest> folder\n\n"
                      " [bold]Search:[/bold]\n"
                      "   s <term>        Search folder/note names (case-insensitive)\n"
                      "   s #<tag>        Search notes by tag (case-insensitive)\n\n"
                      " [bold]Other:[/bold]\n"
                      "   md              Show supported Markdown\n"
                      "   help            Show this command list\n"
                      "   help+           Show detailed instructions\n"
                      "   q               Quit Termnotes\n")

      elif command == "help+":
        console.print("\n[bold blue]Termnotes Detailed Instructions:[/bold blue]\n\n"
                      "*   [bold]Names & Case:[/bold] Opening (`o`), deleting (`d`), editing (`e`), and moving (`mv`) specific items is usually [i]case-sensitive[/i]. Searching (`s`) is [i]case-insensitive[/i]. Creating (`nf`, `nn`) checks for conflicts case-insensitively.\n"
                      "*   [bold]Navigation:[/bold] `l` lists contents. `o foldername` enters a folder. `o notename` opens a note (must be in a folder). `b` goes back to the folder list (root).\n"
                      "*   [bold]Creation:[/bold] `nf name` creates a folder (only at root `/ >`). `nn name` creates a note (must be in a folder `foldername >`). `dn` is a shortcut for a dated note in the 'dailys' folder.\n"
                      "*   [bold]Deletion:[/bold] `d name` deletes the folder (if at root) or note (if in folder). [bold yellow]Requires confirmation (y/n).[/bold yellow]\n"
                      "*   [bold]Editing:[/bold] `e name` allows renaming a folder (if at root) or renaming, editing tags, and editing content for a note (if in folder).\n"
                      "*   [bold]Moving Notes:[/bold] `mv source destination_folder`. The `source` can be `notename` (if you are in its folder) or `foldername/notename` (if you are at the root). Destination is the target folder name.\n"
                      "*   [bold]Searching:[/bold] `s term` finds folders/notes containing `term` anywhere in the name. `s #tag` finds notes with that tag. Search results show options to open.\n"
                      "*   [bold]Inputting Tags/Content:[/bold] When prompted, type text line by line. Enter `SAVE` (all caps) on a new line or press `Ctrl+D` (EOF) to finish.\n"
                      "*   [bold]Markdown:[/bold] Use `md` command to see supported syntax (`#` headers, `-`/`•` lists, `-[]`/`-[+]` todos).\n"
                      "*   [bold]Quitting:[/bold] Use `q`.\n")

      elif command == "md":
        console.print("\n[bold blue]Supported Markdown (applied when reading notes):[/bold blue]\n\n"
                      "  `# Heading Text`   -> [bold]Heading Text[/bold]\n"
                      "  `-[] Todo Text`    -> [bold red]☐[/bold red] Todo Text\n"
                      "  `-[+] Done Text`   -> [bold green]☑[/bold green] Done Text\n"
                      "  `- List item`      ->   • List item (respects indent)\n"
                      "  `Tags: tag1, tag2` -> Displayed as: Tags: [bold pale_violet_red1]#tag1[/bold pale_violet_red1], [bold pale_violet_red1]#tag2[/bold pale_violet_red1]\n"
                      "                       (Stored plainly in file as `tag1, tag2`)\n")

      elif command == "q":
        print("\nGoodbye!\n")
        break # Exit the main loop

      else:
        print(f"\n[bold red]Invalid command: '{command}'. Type 'help' for options.[/bold red]\n")

    # --- Graceful Error Handling for Command Processing ---
    except (KeyboardInterrupt, EOFError):
       # Catch Ctrl+C/D during command execution (like long input prompts)
       print("\n\n[bold yellow]Operation interrupted. Returning to prompt.[/bold yellow]\n")
       # Optionally reset state or list current location here
       if in_folder: list_notes(in_folder)
       else: list_folders()
       continue # Go back to prompt safely
    except Exception as e:
      # Catch unexpected errors within a command's logic
      console.print(f"\n[bold red]An unexpected error occurred processing command '{command}':[/bold red]")
      console.print_exception(show_locals=False) # Print traceback for debugging
      print("\nReturning to command prompt...")
      # Stay in the same folder context if possible


# --- Script Entry Point ---
if __name__ == "__main__":
  run()