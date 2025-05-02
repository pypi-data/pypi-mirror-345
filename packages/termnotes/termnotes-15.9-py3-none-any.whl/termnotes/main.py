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

def create_note(folder, name, tags, content):
  """Creates a new note inside a folder."""
  folder_path = os.path.join(BASE_DIR, folder)

  if not os.path.exists(folder_path):
    print("\n[bold red]Folder not found. Create the folder first.[/bold red]\n")
    return

  if len(tags) > 0:
    lines = tags.splitlines()
    final_tags = ", ".join(lines)
  else:
    final_tags = ""

  if check_name(name):
    note_path = os.path.join(folder_path, f"{name}.txt")
    with open(note_path, "w") as file:
      if len(final_tags) > 0:
        file.write(f"Tags: {final_tags}\n\n")
      else:
        file.write("Tags: \n\n")
      file.write(content)
    print(f"\n[bold green]New note '{name}' created in '{folder}'.[/bold green]\n")
  else:
    print("\n[bold red]There's already a file with that name.[/bold red]\n")

def search(query):
  """Searches for folders, notes by name, or notes by tags and prompts to open."""
  global in_folder
  found_notes_by_name = []
  found_notes_by_tag = {}
  search_term = query.lower()

  if query.startswith("#"):
    tag_to_search = query[1:].strip().lower()
    for folder in os.listdir(BASE_DIR):
      folder_path = os.path.join(BASE_DIR, folder)
      if os.path.isdir(folder_path):
        for note_file in os.listdir(folder_path):
          if note_file.endswith(".txt"):
            note_path = os.path.join(folder_path, note_file)
            note_name = note_file.replace(".txt", "")
            with open(note_path, "r") as f:
              first_line = f.readline().strip()
              if first_line.lower().startswith("tags:"):
                tags_str = first_line[len("tags:"):].strip()
                note_tags = [tag.strip().lstrip('#').lower() for tag in tags_str.split(",") if tag.strip()]
                if tag_to_search in note_tags:
                  if note_name not in found_notes_by_tag:
                    found_notes_by_tag[note_name] = folder

  if found_notes_by_tag:
    results_content = "[bold blue]Notes found by tag:[/bold blue]\n"
    tag_items = list(found_notes_by_tag.items())
    for i, (name, folder) in enumerate(tag_items):
      if i == len(tag_items) - 1:
        results_content += f"└── [bold]{folder}/{name}[/bold] (n)"
      else:
        results_content += f"├── [bold]{folder}/{name}[/bold] (n)\n"
    results_panel = Panel(results_content, title="[bold green]Tag Search Results[/bold green]")
    console.print("\n")
    console.print(results_panel)
    choice = Prompt.ask("\nType 'o + note name' to open or 'c' to cancel").strip().lower()
    if choice != 'c' and choice.startswith('o '):
      name = choice[2:].strip()
      if len(name) > 0:
        folder_to_open = ""
        exact_match = False
        # First try exact matches
        for search_name, folder in found_notes_by_tag.items():
          if search_name.lower() == name.lower():
            folder_to_open = folder
            name = search_name  # Use the actual case from the filename
            exact_match = True
            break

        # If no exact match, try partial matches
        if not exact_match:
          matches = []
          for search_name, folder in found_notes_by_tag.items():
            if name.lower() in search_name.lower():
              matches.append((search_name, folder))

          # If we have just one match, use it
          if len(matches) == 1:
            name, folder_to_open = matches[0]
          # If multiple matches, ask the user to be more specific
          elif len(matches) > 1:
            console.print("\n[bold yellow]Multiple matches found:[/bold yellow]")
            for i, (match_name, match_folder) in enumerate(matches):
              console.print(f"{i+1}: {match_folder}/{match_name}")
            console.print("\n[bold yellow]Please use more specific name or full note name.[/bold yellow]\n")
            return

        if folder_to_open:
          if os.path.exists(os.path.join(BASE_DIR, folder_to_open, f"{name}.txt")):
            read_note(folder_to_open, name)
            in_folder = folder_to_open
            return
          else:
            console.print("\n[bold red]Note not found in the specified folder.[/bold red]\n")
            return
        else:
          console.print("\n[bold red]No note found matching that name.[/bold red]\n")
          return
      else:
        console.print("\n[bold red]Invalid open format.[/bold red]\n")
        return
    elif choice == 'c':
      console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
      return
    else:
      console.print("[bold red]\nInvalid choice.[/bold red]\n")
      return

  # Search folders (exact match only)
  found_folders = [
    f for f in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, f)) and f.lower() == search_term
  ]

  # Search notes (exact match only)
  for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(folder_path):
      notes = [
        (folder, f.replace(".txt", ""))
        for f in os.listdir(folder_path)
        if f.endswith(".txt") and f.lower().replace('.txt', '') == search_term
      ]
      found_notes_by_name.extend(notes)

  if not found_folders and not found_notes_by_name:
    console.print("\n[bold red]No matching folders or notes found[/bold red]\n")
    return

  search_results = []
  if found_folders:
    search_results.append("[bold blue]Folder:[/bold blue]")
    for folder in found_folders:
      search_results.append(f"├── [bold]{folder}[/bold] (f)")
  if found_notes_by_name:
    if found_folders:
      search_results.append("\n[bold blue]Note:[/bold blue]")
    else:
      search_results.append("[bold blue]Note:[/bold blue]")
    for folder, note in found_notes_by_name:
      search_results.append(f"└── [bold]{folder}/{note}[/bold] (n)")

  results_content = "\n".join(search_results)
  results_panel = Panel(
    results_content, title="[bold green]Search Results[/bold green]"
  )
  console.print("\n")
  console.print(results_panel)

  choice = Prompt.ask(
    f"\nType 'o' to open or 'c' to cancel search"
  ).lower()

  if choice == "o":
    if len(found_folders) == 1 and not found_notes_by_name:
      folder_to_open = found_folders[0]
      if os.path.exists(os.path.join(BASE_DIR, folder_to_open)):
        in_folder = folder_to_open
        list_notes(in_folder)
        return
    elif not found_folders and len(found_notes_by_name) == 1:
      folder, note_to_open = found_notes_by_name[0]
      read_note(folder, note_to_open)
      in_folder = folder
      return
    elif found_folders or found_notes_by_name:
      print("\n[bold yellow]Multiple results found. Please be more specific or use 'o folder/note_name'[/bold yellow]\n")
      return
  elif choice == "c":
    console.print("[bold yellow]\nSearch canceled.[/bold yellow]\n")
  else:
    console.print("[bold red]\nInvalid choice.[/bold red]\n")

def read_note(folder, name):
  """Reads and displays a note with bold Markdown headings."""
  note_path = os.path.join(BASE_DIR, folder, f"{name}.txt")
  word_count = 0

  if not os.path.exists(note_path):
    console.print(f"\n[bold red]Note '{name}' not found in '{folder}'.[/bold red]\n")
    return

  with open(note_path, "r") as file:
    content = file.read()
    lines = content.split('\n')
    words = []
    for line in lines[1:]:
      for word in line.split():
          words.append(word)

  with open(note_path, "r") as f:
    first_line = f.readline().strip()
    if first_line.lower().startswith("tags:"):
      tags_str = first_line[len("tags:"):].strip()
      note_tags = [tag.strip().lstrip('#').lower() for tag in tags_str.split(",") if tag.strip()]
      lines_with_tags = [f"[bold pale_violet_red1]#{tag}[/bold pale_violet_red1]" for tag in note_tags]
      final_tags = ", ".join(lines_with_tags)

  modified_lines = []
  for line in lines[1:]:
    if line.startswith("#"):
      # Replace Markdown heading with rich's bold markup
      modified_line = f"[bold]{line.lstrip("#").strip()}[/bold]"
      modified_lines.append(modified_line)
    elif line.startswith("-[]"):
      modified_line = f"[bold red]- [/bold red]{line.lstrip("-[]").strip()}"
      modified_lines.append(modified_line)
    elif line.startswith("-[+]"):
      modified_line = f"[bold green]+ [/bold green]{line.lstrip("-[+]").strip()}"
      modified_lines.append(modified_line)
    elif line.startswith("- "):
      modified_line = f"\t• {line.lstrip("- ").strip()}"
      modified_lines.append(modified_line)
    else:
      modified_lines.append(line)

  if len(final_tags) > 0:
    content = f"Tags: {final_tags}\n"
  else:
    content = "Tags: \n"
  content += "\n".join(modified_lines)  # Join the modified lines back into content
  word_count = len(words)

  title = f"[bold blue]{name} | {word_count} words[/bold blue]"

  folder_path = os.path.join(BASE_DIR, folder)
  notes = [f.replace(".txt", "") for f in os.listdir(folder_path) if f.endswith(".txt")]
  note_lines = []
  for i, note in enumerate(notes):
    if i == len(notes) - 1:
      note_lines.append(f"[bold]{note}[/bold] (n)")
    else:
      note_lines.append(f"[bold]{note}[/bold] (n)")
  folder_content = "\n".join([f"├── {line}" for line in note_lines[:-1]] + [f"└── {note_lines[-1]}"])
  folder_title = f"[bold blue]{folder}[/bold blue]"
  folder_panel = Panel(folder_content, title=folder_title, expand=True)
  note_panel = Panel("\n" + content, title=title, expand=True)

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

def extract_tags_from_styled_string(styled_tags_str):
  """Extracts a list of lowercase tags specifically from '[bold pale_violet_red1]#tag[/bold pale_violet_red1]' format."""
  tags = []
  for styled_tag in styled_tags_str.split(','):
    cleaned_tag = styled_tag.strip()
    start_bold = cleaned_tag.find("[bold pale_violet_red1]")
    end_bold = cleaned_tag.find("[/bold pale_violet_red1]")

    if start_bold != -1 and end_bold != -1 and start_bold < end_bold:
      tag_start = start_bold + len("[bold pale_violet_red1]")
      extracted_tag = cleaned_tag[tag_start:end_bold].lstrip('#').lower()
      if extracted_tag:
        tags.append(extracted_tag)
    # If the tag doesn't match the expected bold format, you might want to handle it differently
    # For example, just strip '#' and lowercase if no styling is found.
    else:
      cleaned_plain_tag = cleaned_tag.lstrip('#').lower()
      if cleaned_plain_tag:
        tags.append(cleaned_plain_tag)
  return tags

def edit_note_or_folder(name):
  """Edits a note (rename and modify content) or renames a folder."""
  global in_folder

  if in_folder:  # Editing a note
    note_path = os.path.join(BASE_DIR, in_folder, f"{name}.txt")

    if not os.path.exists(note_path):
      print("\n[bold red]Note not found.[/bold red]\n")
      return

    # Step 1: Rename the note (optional)
    print("\nPress Enter to keep the current name, or type a new name:")
    new_name = input().strip()

    if new_name and new_name != name and check_name(new_name):
      new_path = os.path.join(BASE_DIR, in_folder, f"{new_name}.txt")
      os.rename(note_path, new_path)
      print(f"\n[bold green]Note renamed to '{new_name}'.[/bold green]\n")
      name = new_name  # Update name
      note_path = new_path  # Update path

    with open(note_path, "r") as f:
      old_tags_plain = f.readline().strip()

    # Use extract_tags_from_styled_string to get clean tags
    old_tags_list = []
    parts = old_tags_plain.split(": ")
    if len(parts) > 1:
      tag_string = parts[1]
      old_tags_list = extract_tags_from_styled_string(tag_string)

    print(f"\n[bold blue]Current tags:[/bold blue]")
    for i, tag in enumerate(old_tags_list, 1):
      print(f"{i}: {tag}")

    new_tags = old_tags_list[:]

    while True:
      command = console.input("[bold blue]\nEnter:[/bold blue]\n'line number' to edit a tag\n'a' to add a tag/tags\n'd + line number' to delete a tag\n'c + line number' to copy a tag\n'save' to save:\n\n[bold blue]cmd: [/bold blue]").strip()

      if command.lower() == "save":
        break
      elif command.lower() == "a":
        print("\nAdd tags (enter 'save' when finished):")
        while True:
          new_line = input().strip()
          if new_line.lower() == "save":
            break
          new_tags.append(new_line)  # Append new tags without newline
      elif command.isdigit():
        line_number = int(command) - 1
        if 0 <= line_number < len(new_tags):
          print(f"Current: {new_tags[line_number].strip()}")
          new_text = input("Edited tag: ").strip()
          if new_text:
            new_tags[line_number] = new_text  # Modify without newline
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("d ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_tags):
          del new_tags[line_number]
          print(f"\n[bold green]Tag {line_number + 1} deleted.[/bold green]")
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("c ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_tags):
          copied_line = new_tags[line_number]
          pyperclip.copy(copied_line)
          print(f"\n[bold green]Tag nr {line_number + 1} copied to clipboard.[/bold green]")
        else:
          print("[bold red]Invalid line number.[/bold red]")
      else:
        print("[bold red]Invalid command.[/bold red]")

    # Format tags for output
    if new_tags:
      processed_tags = []
      for tag in new_tags:
        cleaned_tag = tag.strip().replace("#", '')
        if cleaned_tag:
          processed_tags.append(f"[bold pale_violet_red1]#{cleaned_tag}[/bold pale_violet_red1]")
      final_tags = ", ".join(processed_tags)
    else:
      final_tags = ""

    with open(note_path, "r") as file:
      all_lines = file.readlines()

    if all_lines:
      first_line = all_lines[0].strip()
      if first_line.startswith("Tags:"):
        all_lines[0] = f"Tags: {final_tags}\n"
      else:
        all_lines.insert(0, f"Tags: {final_tags}\n\n")
    else:
      all_lines = [f"Tags: {final_tags}\n", "\n"]

    with open(note_path, "w") as file:
      file.writelines(all_lines)

    print("\n[bold green]Tags updated successfully.[/bold green]\n")
    # Step 2: Edit existing content
    with open(note_path, "r") as file:
      old_content = file.readlines()

    print(f"\n[bold blue]Current content:[/bold blue]")
    for i, line in enumerate(old_content, 1):
      print(f"{i}: {line.strip()}")

    new_content = old_content[:]  # Copy old content

    while True:
      command = console.input("[bold blue]\nEnter:[/bold blue]\n'line number' to edit\n'a' to append\n'd + line number' to delete\n'c + line number' to copy line\n'save' to save:\n\n[bold blue]cmd: [/bold blue]").strip()

      if command.lower() == "save":
        break
      elif command.lower() == "a":
        print("\nType new lines (enter 'save' when finished):")
        while True:
          new_line = input()
          if new_line.lower() == "save":
            break
          new_content.append(new_line + "\n")  # Append new lines
      elif command.isdigit():
        line_number = int(command) - 1
        if 0 <= line_number < len(new_content):
          print(f"Current: {new_content[line_number].strip()}")
          new_text = input("New text: ").strip()
          if new_text:
            new_content[line_number] = new_text + "\n"  # Modify the line
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("d ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_content):
          del new_content[line_number]  # Delete the specified line
          print(f"\n[bold green]Line {line_number + 1} deleted.[/bold green]")
        else:
          print("[bold red]Invalid line number.[/bold red]")
      elif command.startswith("c ") and command[2:].isdigit():
        line_number = int(command[2:]) - 1
        if 0 <= line_number < len(new_content):
            copied_line = new_content[line_number]  # Copy the specified line
            pyperclip.copy(copied_line)  # Copy the line to the clipboard
            print(f"\n[bold green]Line {line_number + 1} copied to clipboard.[/bold green]")
        else:
            print("[bold red]Invalid line number.[/bold red]")
      else:
        print("[bold red]Invalid command.[/bold red]")

    # Save updated content
    with open(note_path, "w") as file:
      file.writelines(new_content)

    print("\n[bold green]Note updated successfully.[/bold green]\n")

  else:  # Renaming a folder
    folder_path = os.path.join(BASE_DIR, name)
    if not os.path.exists(folder_path):
      print("\n[bold red]Folder not found.[/bold red]\n")
      return

    print("\nEnter a new name for the folder:")
    new_name = input().strip()

    # Corrected condition to check the new folder name
    if new_name and new_name != name and check_name(new_name):
      new_folder_path = os.path.join(BASE_DIR, new_name)
      os.rename(folder_path, new_folder_path)
      print(f"\n[bold green]Folder renamed to '{new_name}'.[/bold green]\n")

      if in_folder == name:
        in_folder = new_name  # Update reference
    else:
      print("\n[bold red]Invalid or duplicate folder name.[/bold red]\n")

def move_note_or_folder(source, destination):
  """Moves a note or folder to a new destination."""
  # Resolve source and destination paths relative to BASE_DIR
  if source.endswith(".txt") is False:
    source = f"{source}.txt"
  source_path = os.path.abspath(os.path.join(BASE_DIR, source.strip()))
  destination_path = os.path.abspath(os.path.join(BASE_DIR, destination.strip()))

  # Check if the source exists
  if not os.path.exists(source_path):
    print(f"\n[bold red]Source '{source}' not found.[/bold red]\n")
    return

  # Check if the destination is a valid folder
  if not os.path.exists(destination_path) or not os.path.isdir(destination_path):
    print(f"\n[bold red]Destination folder '{destination}' not found.[/bold red]\n")
    return

  try:
    # Perform the move operation
    shutil.move(source_path, destination_path)
    print(f"\n[bold green]'{source}' moved to '{destination}'.[/bold green]\n")
  except Exception as e:
    print(f"\n[bold red]Error moving: {e}[/bold red]\n")


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
