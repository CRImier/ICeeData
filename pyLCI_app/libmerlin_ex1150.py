import os
import shutil

report_folder = "Merlin@Home"
fs_dump_name = "full_dump.tgz"

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
    print("Sharing reports with ICeeData")

def send_fs_dump(current_path):
    fs_dump_path = os.path.join(current_path, fs_dump_name)
    print("Sending {} to ICeeData server".format(fs_dump_name))

def get_report_path(base_path):
    if not os.path.exists(base_path): return base_path
    counter = 1
    while os.path.exists("{}_({})".format(base_path, counter)):
        counter += 1
    return "{}_({})".format(base_path, counter)
