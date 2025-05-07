import shlex
import shutil
import re

PLACEHOLDERS = {
    "{{java}}": shutil.which("java"),
    "{{python}}": shutil.which("python"),
    "{{cmake}}": shutil.which("cmake"),
    "{{bash}}": shutil.which("bash"),
}



def normalize_placeholders(text: str) -> str:
    """
    Convert all placeholders of the form {{ KEY }} to {{ key }} (lowercased key),
    preserving spacing inside the double braces.

    Args:
        text (str): Input string with placeholders.

    Returns:
        str: Modified string with placeholders lowercased.
    """
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
    return pattern.sub(lambda m: f"{{{{ {m.group(1).lower()} }}}}", text)


def replace_placeholder(cmd):
    cmd = normalize_placeholders(cmd)
    for k, v in PLACEHOLDERS.items():
        cmd = cmd.replace(k, str(v))
    return shlex.split(cmd)


def replace_solver_dir_in_list(cmd, dir):
    for index, c in enumerate(cmd):
        cmd[index] = replace_solver_dir_in_str(c, dir)
    return cmd


def replace_solver_dir_in_str(cmd, dir):
    return normalize_placeholders(cmd).replace("{{solver_dir}}", dir)

def replace_core_placeholder(cmd, executable, options):
    cmds = cmd.split()
    result = []
    for item in cmds:
        r = normalize_placeholders(item)
        for k, value in zip(["{{executable}}", "{{options}}"], [str(executable), options]):
            r = r.replace(k, value)
        result.append(r)
    return result
