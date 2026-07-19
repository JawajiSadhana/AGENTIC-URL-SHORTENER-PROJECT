def check_safe(tool, args):
    if tool == "shell" and "rm -rf" in args.get("cmd",""): return False
    return True