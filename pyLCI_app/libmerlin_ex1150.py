import os
import shutil

report_folder = "Merlin@Home"
fs_dump_name = "full_dump.tgz"
sjm_marker="SJM"
sjm_marker_offset=501

def has_merlin_files(path, name=report_folder):
    return dir_has_name(path, name)

def has_fs_dump(path, name=fs_dump_name):
    return dir_has_name(path, name)

def dir_has_name(dir, name):
    return name in os.listdir(dir)

def copy_reports(current_path, selected_path):
    report_path = os.path.join(current_path, report_folder)
    new_report_path = get_report_path(os.path.join(selected_path, report_folder+"_exported"))
    print("Copying reports from {} to {}".format(report_path, new_report_path))
    shutil.copy(report_path, new_report_path)
    return new_report_path

def transfer_reports(current_path, selected_path):
    report_path = os.path.join(current_path, report_folder)
    new_report_path = get_report_path(os.path.join(selected_path, report_folder+"_exported"))
    print("Moving reports from {} to {}".format(report_path, new_report_path))
    shutil.move(report_path, new_report_path)
    return new_report_path

def share_reports(report_path):
    """Unfinished"""
    print("Sharing reports with ICeeData")

def send_fs_dump(current_path):
    """Unfinished"""
    fs_dump_path = os.path.join(current_path, fs_dump_name)
    print("Sending {} to ICeeData server".format(fs_dump_name))

def get_report_path(base_path):
    if not os.path.exists(base_path): return base_path
    counter = 1
    while os.path.exists("{}_({})".format(base_path, counter)):
        counter += 1
    return "{}_({})".format(base_path, counter)

def mark_paritition_as_sjm(part_path):
    with open(part_path, 'wb+') as f:
        f.seek(sjm_marker_offset)
        f.write(sjm_marker)
        f.flush()
    if not partition_marked_as_sjm(part_path):
        raise IOError("SJM marker could not be verified!")

def partition_marked_as_sjm(part_path):
    with open(part_path, 'rb') as f:
        f.seek(sjm_marker_offset)
        mark = f.read(len(sjm_marker))
    return mark != sjm_marker:

def partition_is_sjm(part_path):
    #First rule - SJM device expor scripts are hardcoded to use the first partition
    if not part_path.endswith('1'): return False 
    #Then, look for the marker
    if not partition_marked_as_sjm(part_path): return False
    #Both conditions apply, return True
