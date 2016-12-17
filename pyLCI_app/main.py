menu_name = "ICeeData USBtool"
i = None
o = None

from subprocess import call
from time import sleep
from pyrtitions import get_partitions

from ui import Menu, Printer, IntegerInDecrementInput, MenuExitException, Refresher, DialogBox, format_for_screen as ffs, Listbox, CharArrowKeysInput

import libmerlin_ex1150 as libmerlin

def pylprint(phrase):
    Printer(ffs(phrase, o.cols, break_words=False), i, o, 3, skippable=True)

def usb_read():
    unfiltered_partitions = get_partitions()
    #Raspberry Pi-specific filtering
    partitions = [partition for partition in unfiltered_partitions if not partition["name"].startswith("/dev/mmcblk0")]
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
        pylprint("More than one drive found")
        lb_contents = [["{} s:{}".format(part["path"], part["size"]), part] for part in possible_parts]
        current_partition = Listbox(lb_contents, i, o, "Partition selection listbox")
        if not current_partition:
            pylprint("Aborting!"); return
    else:
        current_partition = possible_parts[0]
    #Now working on the partition found
    current_path = current_partition["mountpoint"]
    partitions.remove(current_partition)
    if not partitions:
        pylprint("No partitions to transfer data to found!")
    mounted_partitions = [partition for partition in partitions if partition["mounted"]]
    Printer(["Choose", "destination"], i, o, 1) 
    lb_contents = []
    for part in mounted_partitions:
        if "label" in part:
            part_pname = part["label"]
        else:
            part_pname = part["uuid"]
        
        lb_contents.append()
    lb_contents = [part["pretty_name"], part["path"] for part in mounted_partitions]
    lb = Listbox(lb_contents, i, o, "")
    selected_partition = lb.activate()
    if not selected_partition:
        Printer("Aborted", i, o, 1, skippable=True); return
    if libmerlin.has_merlin_files(current_path):
        pylprint("Report files found")
os.copy(os.path.join(current_partition["mountpoint"], "Merlin@Home/"), os.path.join(selected_partition["mountpoint"], "Merlin@Home/"))
        Printer("Copied files", i, o, 1, skippable=True)
    else:
        pylprint("Report files not found!")
    if libmerlin.has_fs_dump(current_path):
        pylprint("Filesystem image found! Agree to send it to ICeeData?")
        dbox = DialogBox("yn", i, o, "Send image?")
        answer = dbox.activate()
        if answer == True:
            fs_image_path = os.path.join(partition["mountpoint"], "full_dump.tgz"
            send_fs_image(fs_image_path, iceedata_server)
            os.remove(fs_image_path, "full_dump.tgz"))
        else:
            Printer("=(", i, o, 0.5, skippable=True)
                

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
    ["Prepare USB", usb_prepare_menu],
    ["Problems?", problems_menu],
    ["Privacy policy", privacy_policy],
    ["Terms&conditions", terms_conditions]]
    Menu(main_menu_contents, i, o).activate()


def init_app(input, output):
    global i, o
    i = input; o = output #Getting references to output and input device objects and saving them as globals
