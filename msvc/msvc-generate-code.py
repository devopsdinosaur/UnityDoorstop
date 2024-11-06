import os
import sys
import re

THIS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.realpath(os.path.join(THIS_DIR, ".."))
INFO_FILE = os.path.join(ROOT_DIR, "info.lua")
SRC_DIR = os.path.join(ROOT_DIR, "src")
WINDOWS_SRC_DIR = os.path.join(SRC_DIR, "windows")
TEMPLATE_DIR = os.path.join(WINDOWS_SRC_DIR, "build_tools")
PROXY_DIR = os.path.join(WINDOWS_SRC_DIR, "proxy")
PROXY_FILE = os.path.join(PROXY_DIR, "proxylist.txt")
OUT_DIR = os.path.join(SRC_DIR, "generated", "windows")

def log(text):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()

def read_file_text(path):
    f = open(path, "r")
    data = f.read()
    f.close()
    return data

def write_file_text(path, data):
    os.makedirs(os.path.dirname(path), exist_ok = True)
    f = open(path, "w")
    f.write(data)
    f.close()

def write_template(template_path, out_path, vals):
    data = read_file_text(template_path)
    for key, val in vals.items():
        data = data.replace("${%s}" % key.upper(), val)
    write_file_text(out_path, data)

def proxygen():
    FORMATS = {
        'proxy_defs': "static FARPROC __%(func)s__;",
        'proxy_adds': "__%(func)s__ = GetProcAddress((HMODULE)dll, \"%(func)s\");",
        'proxy_funcs': "void *exp_%(func)s() { return __%(func)s__(); }",
        'export_funcs': "%(func)s = exp_%(func)s",
    }
    vals = {}
    for line in read_file_text(PROXY_FILE).split("\n"):
        func = line.strip()
        if (not func):
            continue
        for key, format in FORMATS.items():
            if (key not in vals.keys()):
                vals[key] = []
            vals[key].append(format % locals())
    for key in vals.keys():
        vals[key] = "\r\n".join(vals[key])
    write_template(os.path.join(TEMPLATE_DIR, "proxy.c.in"), os.path.join(OUT_DIR, "proxy.c"), vals)
    write_template(os.path.join(TEMPLATE_DIR, "dll.def.in"), os.path.join(OUT_DIR, "dll.def"), vals)

def rcgen():
    rx_simple_field = re.compile("^(.*?)=(.*?),*$")
    vals = {}
    for line in read_file_text(INFO_FILE).split("\n"):
        line = line.strip()
        if (not line):
            continue
        match = rx_simple_field.match(line)
        if (match is not None):
            vals[match.group(1).strip()] = match.group(2).strip().strip('\"')
    write_template(os.path.join(TEMPLATE_DIR, "info.rc.in"), os.path.join(OUT_DIR, "info.rc"), vals)

def main(argv):
    proxygen()
    rcgen()
    return 0

if (__name__ == "__main__"):
    sys.exit(main(sys.argv))