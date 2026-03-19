import os
from rclone_utils import run, remote_exists, create_remote, create_crypt, show_config

def encrypt_file(input_mode, local_file, local_path,
                 remote_name, remote_type, token,
                 use_crypt, crypt_password):
    """Faz upload de um arquivo local para um remote, opcionalmente criptografado."""
    # origem
    if input_mode == "Upload":
        if local_file is None:
            return "Erro: selecione um arquivo"
        source = local_file.name
    else:
        if not local_path:
            return "Erro: informe o caminho"
        source = local_path

    output = ""

    # cria remote base
    output += create_remote(remote_name, remote_type, token)

    if not remote_exists(remote_name):
        return "Erro: remote base não existe"

    # destino
    if use_crypt:
        crypt_name = f"{remote_name}-crypt"
        output += create_crypt(crypt_name, remote_name, crypt_password)
        output += "\nCONFIG CRYPT:\n" + show_config(crypt_name)
        dest = f"{crypt_name}:encryption"
    else:
        dest = f"{remote_name}:backup"

    output += f"\nEnviando {source} → {dest}\n"
    cmd = ["rclone", "copy", source, dest, "--progress"]
    output += run(cmd)

    return output

def decrypt_file(remote_name, use_crypt):
    """Restaura um arquivo criptografado (ou não) de um remote para a pasta local."""
    if use_crypt:
        remote_name = f"{remote_name}-crypt"

    if not remote_exists(remote_name):
        return None, f"Erro: remote '{remote_name}' não existe"

    local_dir = "/content/restore"
    os.makedirs(local_dir, exist_ok=True)

    cmd = ["rclone", "copy", f"{remote_name}:encryption", local_dir, "--progress"]
    output = run(cmd)

    files = os.listdir(local_dir)
    file_path = None
    if files:
        file_path = os.path.join(local_dir, files[0])

    return file_path, output

def remote_to_remote_backup(source_remote, source_path,
                            dest_remote, dest_type, dest_token,
                            use_crypt, crypt_password):
    """Copia dados de um remote para outro, com opção de criptografar no destino."""
    if not remote_exists(source_remote):
        return f"Erro: source remote '{source_remote}' não existe"

    output = ""
    # cria remote destino se não existir
    output += create_remote(dest_remote, dest_type, dest_token)

    if not remote_exists(dest_remote):
        return "Erro: remote destino não existe"

    # destino final
    if use_crypt:
        crypt_name = f"{dest_remote}-crypt"
        output += create_crypt(crypt_name, dest_remote, crypt_password)
        output += "\nCONFIG CRYPT DESTINO:\n" + show_config(crypt_name)
        dest_spec = f"{crypt_name}:encryption"
    else:
        dest_spec = f"{dest_remote}:{source_path}"

    source_spec = f"{source_remote}:{source_path}"
    output += f"\nCopiando {source_spec} → {dest_spec}\n"
    cmd = ["rclone", "copy", source_spec, dest_spec, "--progress"]
    output += run(cmd)

    return output