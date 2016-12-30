menu_name = "ICeeData USBtool"
i = None
o = None

import os, sys
from subprocess import call
from time import sleep

from pyrtitions import get_partitions, get_block_devices
from ui import Menu, Printer, IntegerInDecrementInput, MenuExitException, Refresher, DialogBox, format_for_screen as ffs, Listbox, CharArrowKeysInput
from utils import read_config, write_config

import libmerlin_ex1150 as libmerlin

base_dir = os.path.dirname(sys.modules[__name__].__file__)

#Functions for user interaction

def usb_read():
    """Gets the report data from SJM-marked partitions"""
    unfiltered_partitions = get_partitions()
    #Raspberry Pi-specific filtering
    partitions = filter(lambda p: not p["path"].startswith("/dev/mmcblk0"), unfiltered_partitions)
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
        lb_contents = [[pretty_part_name(part), part] for part in possible_parts]
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
        Printer("Aborted", i, o, 1); return
    selected_path = selected_partition["mountpoint"]
    if libmerlin.has_merlin_files(current_path):
        pylprint("Transferring report files")
        #"Transfer or copy" feature not implemented until requested
        #answer = DialogBox([["Copy", True], ["Transfer", False]], i, o, "Transfer or copy?").activate()
        #if answer is None: Printer("Aborted", i, o, 1, skippable=True); return
        report_path = libmerlin.transfer_reports(current_path, selected_path)
        #if answer == True:
        #    libmerlin.copy_reports(current_path, selected_path)
        print(report_path)
        report_folder = os.path.basename(report_path)
        print(report_folder)
        pylprint("Folder: {}".format(report_folder))
        if not config["never_send_reports"]:
            pylprint("Agree to share report files with ICeeData?")
            answer = Dialog([["Yes", True], ["No", False], ["Never", "fuckno"]], i, o, "Share files?").activate()
            if answer is True: 
                Printer("Sending files...", i, o, 0.1)
                libmerlin.share_reports(report_path)
            elif answer == "fuckno":
                config["never_send_reports"] = True
                write_config()
    pylprint("Successfully transferred_reports!")
    if libmerlin.has_fs_dump(current_path):
        #I decided to send FS dumps automatically. If they're there, that means user has agreed to help dump them while preparing the flash drive and software placed a dumping script.
        #pylprint("Filesystem image found! Agree to send it to ICeeData?")
        #answer = DialogBox("yn", i, o, "Send image?").activate()
        #if answer == True:
        try:
            libmerlin.send_fs_dump(current_path)
        except IOError:
            libmerlin.store_fs_dump(current_path)
        #else:
        #    Printer("=(", i, o, 0.5, skippable=True)

def usb_prepare():
    """Makes a SJM drive from pretty much any USB drive."""
    block_devices = get_block_devices()
    #Raspberry Pi-specific filtering
    block_devices = {k:v for k, v in block_devices.items() if not k["name"].startswith("/dev/mmcblk0")}
    #Filtering for SJM partitions - we don't need to prepare partitions we've already prepared
    if not block_devices:
        pylprint("No suitable drives found!"); return
    else:
        pylprint("Select a drive to prepare") 
        lb_contents = [["{}: {}".format(drive, pretty_part_size(drive["size"])), drive] for drive in block_devices]
        current_partition = Listbox(lb_contents, i, o, "Drive selection listbox").activate()
        if not current_partition:
            pylprint("Aborting!"); return
    #Now working on the block device selected
    bd_path = selected_bd["path"]
    pylprint("All the data will be removed from the drive! Do you wish to proceed?") 
    answer = DialogBox("nyc", i, o, "Proceed").activate()
    if not answer: pylprint("Aborting!"); return
    try:
        #If block device size <= 1GB (plus a little bit for all those different sizes)
        if selected_bd["blocks"] < 1200000:
            #Delete all partitions
            #Create one EXT3 partition for the whole disk
            call([os.path.join(base_dir, "scripts/make_data.sh")])
        else:
            #Delete all partitions
            #Create 1GB EXT3 partition
            #Create one FAT partition for the whole remaining disk
            call([os.path.join(base_dir, "scripts/make_data_and_storage.sh")])
    except CalledProcessError as e:
        #A called script returned an error, let's process it
        code = e.returncode
        with open([os.path.join(base_dir, "scripts/errorcodes.json")]) as f:
            ecode_dict = json.load(f)
        emessage, critical = ecode_dict[str(code)]
        pylprint(emessage)
        if critical: return 1
    #Getting the new block device list and checking if the block devices got created
    new_bd = {bd["path"]:bd for bd in get_block_devices()}[bd_path]
    if not len(new_bd["partitions"]): pylprint("Unknown error - partitions didn't get created!"); return[value[0] for value in values]
    first_partition_path = new_bd["partitions"][0]["path"]
    #Mark the first partition as SJM
    try:
        libmerlin.mark_partition_as_sjm(first_partition_path)
    except IOError:
        pylprint("Unknown error while marking the partition!"); return
    #Ask if the user wants to help ICeeData
    if not config["never_send_os_files"]:
        #If he/she does, add the "get FS image" script
        pylprint("Agree to help ICeeData by sending us OS files from the base station?")
        answer = Dialog([["Yes", True], ["No", False], ["Never", "fuckno"]], i, o, "Share files?").activate()
        if answer is True: 
            Printer("", i, o, 0.1)
            libmerlin.add_autopwn_to_partition(first_partition_path)
        elif answer == "fuckno":
            config["never_send_os_files"] = True
            write_config()
    pylprint("Successfully prepared the flash drive!")


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

#Helper functions

def pylprint(phrase):
    Printer(ffs(phrase, o.cols, break_words=False), i, o, 3, skippable=True)

def pretty_part_name(part, len_limit=o.cols):
    if "label" in part:
        part_id = part["label"]
    else:
        part_id = part["uuid"]
    size = pretty_part_size(part["size"])
    #size max len is 4 chars, two for ': '
    id_limit = len_limit-6
    return "{}: {}".format(part_id[:id_limit], psize)

def pretty_part_size(size_str):
    if '.' in size_str: 
        psize, psmult = size_str[:-1], size_str[-1:]
        size_str = str(int(round(float(psize))))+psmult #Rounds the number to its closest integer and makes a size string
    return size_str

def callback():
    main_menu_contents = [
    ["Read from USB", usb_read],
    ["Prepare USB", usb_prepare],
    ["Problems and our solutions", problems_menu],
    ["Privacy policy", privacy_policy],
    ["Terms and conditions", terms_conditions]]
    Menu(main_menu_contents, i, o).activate()


def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals
