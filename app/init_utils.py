def get_windows_host_ip_from_wsl():
    """Obtiene la IP del host de Windows desde WSL leyendo /etc/resolv.conf"""
    try:
        with open("/etc/resolv.conf") as f:
            for line in f:
                if line.startswith("nameserver"):
                    return line.split()[1].strip()
    except FileNotFoundError:
        return None
    return None