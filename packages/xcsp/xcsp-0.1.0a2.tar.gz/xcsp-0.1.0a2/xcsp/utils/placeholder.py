import shutil

PLACEHOLDERS = {
    "{{java}}": shutil.which("java"),
    "{{python}}": shutil.which("python"),
    "{{cmake}}": shutil.which("cmake"),
}


def replace_placeholder(cmd):
    for k, v in PLACEHOLDERS.items():
        cmd = cmd.replace(k, str(v))
    return cmd.split()


def replace_solver_dir(cmd, dir):
    for index, c in enumerate(cmd):
        cmd[index] = c.replace("{{SOLVER_DIR}}", dir)
    return cmd

def replace_core_placeholder(cmd, executable, options):
    cmds = cmd.split()
    result = []
    for item in cmds :
        result.append(item.replace("{{executable}}", str(executable)).replace("{{options}}", options))
    return result
