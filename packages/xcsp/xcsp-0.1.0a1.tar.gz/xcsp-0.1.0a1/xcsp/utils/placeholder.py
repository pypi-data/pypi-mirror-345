import shutil

PLACEHOLDERS = {
    "{{java}}": shutil.which("java"),
    "{{python}}": shutil.which("python"),
    "{{cmake}}": shutil.which("cmake"),
}


def replace_placeholder(cmd):
    for k, v in PLACEHOLDERS.items():
        cmd = cmd.replace(k, str(v))
    return cmd


def replace_solver_dir(cmd, dir):
    return cmd.replace("{{SOLVER_DIR}}", dir)


def replace_core_placeholder(cmd, executable, options):
    cmd = cmd.replace("{{executable}}", str(executable))
    cmd = cmd.replace("{{options}}", options)
    return cmd
