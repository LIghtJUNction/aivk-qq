import base64
import os
import shutil # Import shutil to use which

def _get_cmd(title: str = "NapCat.Shell", cwd: str = "", cmd: str | list = [], shell_type: str = "pwsh"):
    """
    生成在新的 Windows Terminal (wt) 窗口中执行命令的命令行字符串。
    !! 前提: Windows Terminal (wt.exe) 必须已安装并在系统的 PATH 环境变量中。!!

    Args:
        title (str): 新 wt 窗口的标题。
        cwd (str): 新 shell 的初始工作目录。如果为空字符串，则默认为用户主目录。
        cmd (str | list): 要在新 shell 中执行的命令。
                          - 如果是字符串，它应该是一个完整的、格式正确的命令或脚本片段，
                            适合目标 shell (pwsh/powershell/cmd)。
                          - 如果是列表，列表元素将被简单地用空格连接成一个字符串。
                            这适用于简单命令及其参数。对于包含空格或特殊字符的复杂参数，
                            建议直接提供格式化好的字符串 `cmd`。
                          - 如果为空列表或空字符串，则只打开 shell 并设置工作目录。
        shell_type (str): 要启动的 shell 类型。支持 'pwsh' (默认), 'powershell', 或 'cmd'。
                          大小写不敏感。

    Returns:
        str: 一个完整的命令行字符串，可用于 `subprocess.run(...)` 或 `os.system(...)`
             来启动配置好的 Windows Terminal 窗口。

    Raises:
        ValueError: 如果 `shell_type` 不是 'pwsh', 'powershell', 或 'cmd' 之一。
        # 注意: 不检查 cwd 是否实际存在，由目标 shell 处理。
    """
    # (Imports moved to top level)

    if isinstance(cmd, str):
        cmd_str = cmd
    elif isinstance(cmd, list) and cmd: # Check if list is not empty
        # Simple join: suitable for basic commands.
        # For complex args (spaces, quotes), provide a pre-formatted string cmd.
        cmd_str = " ".join(map(str, cmd))
    else:
        cmd_str = "" # Handles empty list, empty string, or other types

    # Determine working directory, default to user's home if not provided
    cwd_path = str(cwd) if cwd else os.path.expanduser("~")
    # Ensure consistent quoting for wt arguments
    # Basic double quoting works unless title/cwd contain double quotes.
    title_arg = f'"{title}"'
    cwd_arg = f'"{cwd_path}"' # wt -d expects quoted path if it contains spaces

    shell_type = shell_type.lower()

    if shell_type in ["pwsh", "powershell"]:
        # Rely solely on wt -d for setting the directory.
        # Construct the PowerShell script to execute *only* the command.
        ps_script = cmd_str # Directly use the command string

        # Encode the script using UTF-16 LE for -EncodedCommand
        # Handle empty cmd_str case for encoding
        ps_bytes = ps_script.encode('utf-16-le') if ps_script else b''
        ps_encoded_cmd = base64.b64encode(ps_bytes).decode('ascii') if ps_bytes else ''

        # Select the correct PowerShell executable
        if shell_type == "pwsh":
            shell_executable = "pwsh"
        else: # shell_type == "powershell"
            # Try to find the full path to powershell.exe
            powershell_path = shutil.which("powershell")
            if powershell_path:
                # Use the full path directly, without adding extra quotes,
                # assuming the path itself doesn't contain spaces (true for standard location).
                shell_executable = powershell_path
                # Optional: Log that we found and are using the full path
                # print(f"DEBUG: Using full path for powershell (no extra quotes): {shell_executable}")
            else:
                # Fallback to just using "powershell" if not found
                shell_executable = "powershell"
                # Optional: Log a warning
                # print("WARNING: Could not find full path for powershell.exe via shutil.which. Falling back to 'powershell'.")

        # Construct the final wt command. If no command, -EncodedCommand will be empty.
        # PowerShell -NoExit will keep the window open even with empty command.
        return f'wt --title {title_arg} -d {cwd_arg} -- {shell_executable} -NoExit -EncodedCommand {ps_encoded_cmd}'

    elif shell_type == "cmd":
        # Rely solely on wt -d for setting the directory.
        # Construct the command line for cmd.exe *only* with the command.
        cmdline = cmd_str # Directly use the command string

        # Construct the final wt command for cmd
        # /k keeps the cmd window open. If cmdline is empty, it just opens cmd.
        # Pass the command directly to cmd /k. Quoting within cmd_str is caller's responsibility.
        return f'wt --title {title_arg} -d {cwd_arg} -- cmd /k {cmdline}'

    else:
        raise ValueError("shell_type 仅支持 'pwsh', 'powershell', 'cmd'")

# ... potentially other code in the file ...

