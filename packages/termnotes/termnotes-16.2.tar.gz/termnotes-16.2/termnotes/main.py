#!/usr/bin/env python3

from datetime import datetime
import os
import shutil
import appdirs
import readline
import pyperclip
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Function to check if name already exists
def check_name(name):
  found_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and name in f]
  found_notes = []

  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt") and name in f]
      found_notes.extend([(folder, note) for note in notes])

  if not found_notes and not found_folders:
    return True
  return False

# Get the system-specific Notes folder
BASE_DIR = appdirs.user_data_dir("Termnotes", "Termnotes")
CONFIG_FILE = "config.json"
in_folder = None  # Tracks current folder

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)

def setup():
  """Ensures the base Notes directory exists."""
  if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def list_folders():
  """Lists all folders inside the Notes directory."""
  folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

  if not folders:
    content = "[dim]└── Create a folder with 'nf name'[/dim]"
  else:
    folder_lines = []
    for i, folder in enumerate(folders):
      if i == len(folders) - 1:  # Last item in the list
        folder_lines.append(f"[bold]{folder}[/bold] (f)")
      else:
        folder_lines.append(f"[bold]{folder}[/bold] (f)")
    content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  inner_panel = Panel(content, title="[bold blue]Folders[/bold blue]", expand=True)  # Customize title color
  empty_panel = Panel("Nothing open", title="", expand=True)

  console.print("\n")
  console.print(inner_panel)
  console.print(empty_panel)
  console.print("\n")

def list_notes(folder):
  """Lists all notes inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)
  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found.[/bold red]\n")
    return

  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]

  if not notes:
      content = "[dim]└── Create a note with 'nn name'[/dim]"
  else:
    note_lines = []
    for i, note in enumerate(notes):
      if i == len(notes) - 1:
        note_lines.append(f"[bold]{note}[/bold] (n)")
      else:
        note_lines.append(f"[bold]{note}[/bold] (n)")
    content = "\n".join([f"├── {line}" for line in note_lines[:-1]] + [f"└── {note_lines[-1]}"])

  folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

  folder_lines = []
  for i, some_folder in enumerate(folders):
    if i == len(folders) - 1:  # Last item in the list
      folder_lines.append(f"[bold]{some_folder}[/bold] (f)")
    else:
      folder_lines.append(f"[bold]{some_folder}[/bold] (f)")
  folder_content = "\n".join([f"├── {line}" for line in folder_lines[:-1]] + [f"└── {folder_lines[-1]}"])

  all_folders_panel = Panel(folder_content, title="[bold blue]Folders[/bold blue]", expand=True)  # Customize title color

  panel_title = f"[bold blue]{folder}[/bold blue]"  # Customize title color
  folder_panel = Panel(content, title=panel_title, expand=True)

  console.print("\n")
  console.print(all_folders_panel)
  console.print(folder_panel)
  console.print("\n")

def create_folder(name):
  """Creates a new folder inside Notes."""
  folder_path = os.path.join(BASE_DIR, name)
  if check_name(name):
    os.makedirs(folder_path, exist_ok=True)
    print(f"\n[bold green]New folder '{name}' created.[/bold green]\n")
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

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
  """Deletes a note or folder."""
  path = os.path.join(BASE_DIR, name)

  if is_folder:
    if os.path.exists(path) and os.path.isdir(path):
      shutil.rmtree(path)
      print(f"\n[bold green]Folder '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Folder not found.[/bold red]\n")
  else:
    note_path = os.path.join(BASE_DIR, name + ".txt")
    if os.path.exists(note_path):
      os.remove(note_path)
      print(f"\n[bold green]Note '{name}' deleted.[/bold green]\n")
    else:
      print("\n[bold red]Note not found.[/bold red]\n")

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


def run():
  # Initialize storage
  setup()
  global in_folder

  print(r"""
 __        __   _                            _
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _ \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
 | |_ ___ _ __ _ __ ___  _ __   ___ | |_ ___  ___
 | __/ _ \ '__| '_ ` _ \| '_ \ / _ \| __/ _ \/ __|
 | ||  __/ |  | | | | | | | | | (_) | ||  __/\__ \
  \__\___|_|  |_| |_| |_|_| |_|\___/ \__\___||___/
  """)
  print("'Help' for commands.")
  quick_note_opened = False
  if quick_note_opened is False:
    if "quick_notes" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
      create_folder("quick_notes")
    in_folder = "quick_notes"
    list_notes(in_folder)
    name = f'{datetime.strftime(datetime.now(), "%d.%m.%y-%H:%M")}'
    tags = ""

    print("Note content (enter 'save' to finish or 'exit' to discard note):")
    content = ""
    while True:
      line = input()
      if line.lower() == "save":  # Stop when the user types "done"
        create_note(in_folder, name, tags, content)
        break
      elif line.lower() == "exit":
        console.print("\n[bold yellow]Note discarded[/bold yellow]\n")
        break
      content += line + "\n"  # Add the line to the note content

    quick_note_opened = True

  while True:
    choice = console.input("[bold blue]cmd: [/bold blue]").strip()

    if choice.startswith("o "):  # Open a folder or note
      name = choice[2:]
      if in_folder:
        read_note(in_folder, name)
      else:
        if os.path.exists(os.path.join(BASE_DIR, name)):
          in_folder = name
          list_notes(name)
        else:
          print("\n[bold red]Folder not found.[/bold red]\n")

    elif choice.startswith("d "):  # Delete folder or note
      name = choice[2:]
      if in_folder:
        delete_note_or_folder(os.path.join(in_folder, name), is_folder=False)
      else:
        delete_note_or_folder(name, is_folder=True)

    elif choice.startswith("nf "):  # New folder
      name = choice[3:]
      create_folder(name)

    elif choice.startswith("nn "):  # New note
      if in_folder:
        name = choice[3:]

        print("Note tags (each on a new line, enter 'save' to finish):")
        tags = ""
        while True:
          line = input()
          if line.lower() == "save":
            break
          tags += line + "\n"

        print("Note content (enter 'save' to finish or 'exit' to discard note):")
        content = ""
        while True:
          line = input()
          if line.lower() == "save":  # Stop when the user types "done"
            create_note(in_folder, name, tags, content)
            break
          elif line.lower() == "exit":
            console.print("\n[bold yellow]Note discarded[/bold yellow]\n")
            break
          content += line + "\n"  # Add the line to the note content

      else:
          print("\nGo into a folder to create a note.\n")

    elif choice == "l":  # List folders or notes
      if in_folder:
        list_notes(in_folder)
      else:
        list_folders()

    elif choice == "b":  # Go back to folders
      if in_folder:
        in_folder = None
        list_folders()
      else:
        print("\nNowhere to go.\n")

    elif choice.startswith("e "):  # Edit folder or note
      name = choice[2:]
      edit_note_or_folder(name)

    elif choice.startswith("s "):
      name = choice[2:]
      search(name)

    elif choice == "help":
        console.print("\n[bold blue]Commands:[/bold blue]\n\no name - open a folder/note\nnf name - create a new folder\nnn name - create a new note\nd name - delete a folder/note\nl - list folders/notes\nb - back to folders\ne name - edit folder/note\ns name - search\ndn - creates a daily note in the 'dailys' folder\nhelp - displays commands\nhelp+ - more specific instructions\nq - quit\nmd - markdown syntax\nmv folder/note destination - moves a note to the destination folder\n")

    elif choice == "help+":
        console.print("\n[bold blue]Instructions:[/bold blue]\n\n[bold]o name[/bold] - if you're in the root folder, it opens a folder, if you're in a folder, it opens a note\n[bold]nf name[/bold] - creates a folder with the given name into the root folder\n[bold]nn name[/bold] - create a new note with the given name. Must be inside of a folder!\n[bold]dn[/bold] - creates a new note with the current dater. Adds it to the 'dailys' folder, if not created then it will create it.\n[bold]d name[/bold] - if you're in the root folder, it deletes a folder, if you're in a folder, it deletes a note\n[bold]l[/bold] - if you're in the root folder, it lists all folders, if you're in a folder, it lists all notes\n[bold]b[/bold] - takes you back to the root folder\n[bold]e name[/bold] - if you're in the root folder, it allows you to edit a folder name, if you're in a folder, it allows you to edit the note name and its contents\n[bold]s name[/bold] - search for folder or note. If found, you can open the folder in which it was found (search is case sensitive)\n([bold]f[/bold]) - type of (folder)\n([bold]n[/bold]) - type of (note)\n[bold]help[/bold] - displays commands\n[bold]help+[/bold] - more specific instructions\n[bold]q[/bold] - quits the application\n[bold]md[/bold] - markdown syntax\n[bold]mv folder/note destination[/bold] - moves a note to the destination folder. [bold]Does not work for names with spaces[/bold]\n")

    elif choice == "q":
      break
    
    elif choice == "md":
      console.print("\n[bold blue]Markdown:[/bold blue]\n\n[bold]-[][/bold] - uncomplete todo\n[bold]-[+][/bold] - complete todo\n[bold]-[/bold] - list item\n[bold]#[/bold] - header\n")

    elif choice == "dn":
      if "dailys" not in [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]:
        create_folder("dailys")
      in_folder = "dailys"
      print(f"[bold green]You are in 'dailys' folder.[/bold green]\n")
      name = datetime.today().strftime('%Y-%m-%d')

      print("Note tags (each on a new line, enter 'save' to finish):")
      tags = ""
      while True:
        line = input()
        if line.lower() == "save":
          break
        tags += line + "\n"

      print("Note content (enter 'save' to finish):")

      content = ""
      while True:
        line = input()
        if line.lower() == "save":  # Stop when the user types "done"
          break
        content += line + "\n"  # Add the line to the note content
      create_note(in_folder, name, tags, content)

    elif choice.startswith("mv "):
      specification = choice[3:].strip()
      if " " not in specification:
        print("\n[bold red]Invalid format. Use 'mv source destination'.[/bold red]\n")
      else:
        # Split the input into source and destination, accounting for spaces in names
        try:
          source, destination = specification.split(" ", 1)
          move_note_or_folder(source.strip(), destination.strip())
        except ValueError:
          print("\n[bold red]Invalid format. Use 'mv source destination'.[/bold red]\n")

    else:
      print("\n[bold red]Invalid command.[/bold red]\n")
