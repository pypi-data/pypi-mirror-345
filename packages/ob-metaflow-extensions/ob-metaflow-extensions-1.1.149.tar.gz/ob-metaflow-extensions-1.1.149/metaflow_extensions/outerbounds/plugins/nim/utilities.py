NIM_MONITOR_LOCAL_STORAGE_ROOT = ".nim-monitor"


def get_storage_path(task_id):
    return f"{NIM_MONITOR_LOCAL_STORAGE_ROOT}/" + task_id + ".sqlite"
