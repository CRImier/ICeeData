menu_name = "ICeeData USBtool"
i = None
o = None

import os
from subprocess import call
from time import sleep
from pyrtitions import get_partitions
from math import ceil
from ui import Menu, Printer, IntegerInDecrementInput, MenuExitException, Refresher, DialogBox, format_for_screen as ffs, Listbox, CharArrowKeysInput

import libmerlin_ex1150 as libmerlin


def pylprint(phrase):
    Printer(ffs(phrase, o.cols, break_words=False), i, o, 3, skippable=True)

def usb_read():
    unfiltered_partitions = get_partitions()
    #Raspberry Pi-specific filtering
    partitions = [partition for partition in unfiltered_partitions if not partition["path"].startswith("/dev/mmcblk0")]
    possible_parts = []
    for partition in partitions:
        if not partition["mounted"]:
            continue
        path = partition["mountpoint"]
        if libmerlin.has_merlin_files(path) or libmerlin.has_fs_dump(path):
            possible_parts.append(partition)
    if not possible_parts:
        pylprint("No drives with data found!"); return
    elif len(possible_parts) > 1:
        pylprint("Select source drive")
        lb_contents = [["{} s:{}".format(part["path"], part["size"]), part] for part in possible_parts]
        current_partition = Listbox(lb_contents, i, o, "Partition selection listbox").activate()
        if not current_partition:
            pylprint("Aborting!"); return
    else:
        current_partition = possible_parts[0]
        pylprint("A drive with data found!")
    #Now working on the partition found
    current_path = current_partition["mountpoint"]
    partitions.remove(current_partition)
    mounted_partitions = [partition for partition in partitions if partition["mounted"]]
    if not mounted_partitions: pylprint("No partitions to transfer data to found!"); return
    Printer(ffs("Choose transfer destination", o.cols, break_words=False), i, o, 1) 
    lb_contents = [[pretty_part_name(part), part] for part in mounted_partitions]
    selected_partition = Listbox(lb_contents, i, o, "").activate()
    if not selected_partition:
        Printer("Aborted", i, o, 1, skippable=True); return
    selected_path = selected_partition["mountpoint"]
    if libmerlin.has_merlin_files(current_path):
        pylprint("Transferring report files")
        #Feature not implemented until requested
        #answer = DialogBox([["Copy", True], ["Transfer", False]], i, o, "Transfer or copy?").activate()
        #if answer is None: Printer("Aborted", i, o, 1, skippable=True); return
        report_path = libmerlin.transfer_reports(current_path, selected_path)
        #if answer == True:
        #    libmerlin.copy_reports(current_path, selected_path)
        print(report_path)
        report_folder = os.path.basename(report_path)
        print(report_folder)
        pylprint("Folder: {}".format(report_folder))
    if libmerlin.has_fs_dump(current_path):
        pylprint("Filesystem image found! Agree to send it to ICeeData?")
        answer = DialogBox("yn", i, o, "Send image?").activate()
        if answer == True:
            libmerlin.send_fs_dump(current_path)
        else:
            Printer("=(", i, o, 0.5, skippable=True)

def pretty_part_name(part):
    if "label" in part:
        part_id = part["label"]
    else:
        part_id = part["uuid"]
    if '.' in part["size"]:
        psize, psmult = part['size'][:-1], part['size'][-1:]
        psize = str(int(round(float(psize))))+psmult
    else:
        psize = part["size"]
    #size max len is 4 chars, two for ': '
    id_limit = o.cols-6
    return "{}: {}".format(part_id[:id_limit], psize)

def problems_menu():
    result = []
    pointer = 0
    with open('problems_and_solutions.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if not line.strip():
            continue
        elif line.startswith('\t'):
            result[pointer][1].append(line.strip())
        else:
            result.append([line.strip(), []])
            pointer = len(result)-1
    
def privacy_policy():
    with open('privacy_policy.txt', 'r') as f:
        text = ''.join(f.readlines())
    formatted_text = ffs(text, o.cols, break_words=False)
    Printer(formatted_text, i, o, 5)

def terms_conditions():
    with open('terms_and_conditions.txt', 'r') as f:
        text = ''.join(f.readlines())
    formatted_text = ffs(text, o.cols, break_words=False)
    Printer(formatted_text, i, o, 5)

def callback():
    main_menu_contents = [
    ["Read from USB", usb_read],
    #["Prepare USB", usb_prepare_menu],
    ["Problems?", problems_menu],
    ["Privacy policy", privacy_policy],
    ["Terms&conditions", terms_conditions]]
    Menu(main_menu_contents, i, o).activate()


def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals
