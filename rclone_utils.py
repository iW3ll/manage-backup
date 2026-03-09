import subprocess

def install_rclone():
    """Instala o rclone se não estiver presente."""
    try:
        subprocess.run(["rclone", "version"], capture_output=True, check=True)
        print("rclone já está instalado.")
    except:
        print("Instalando rclone...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "rclone"], check=True)
        print("rclone instalado.")

def remote_exists(remote_name):
    """Verifica se um remote existe na configuração do rclone."""
    try:
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True)
        remotes = result.stdout.splitlines()
        return any(remote_name + ":" in r for r in remotes)
    except:
        return False

def create_remote(remote_name, remote_type, config_params):
    """
    Cria um remote no rclone.
    Retorna (output, success).
    """
    cmd = ["rclone", "config", "create", remote_name, remote_type]
    for key, value in config_params.items():
        if value:
            cmd.extend([key, value])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout + result.stderr, True
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr, False