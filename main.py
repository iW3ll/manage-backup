
import gradio as gr
from rclone_utils import install_rclone
from backup_operations import (
    encrypt_file,
    decrypt_file,
    remote_to_remote_backup
)

# Instala rclone (se necessário) ao iniciar
install_rclone()


# 🎛️ INTERFACE GRADIO

with gr.Blocks(title="Rclone Tool") as demo:

    gr.Markdown("# 🔐 Manage Backup ")


    # ABA ENCRYPT
    
    with gr.Tab("Encrypt / Backup Local"):

        input_mode = gr.Radio(
            ["Upload", "Caminho"],
            value="Upload",
            label="Escolha como enviar o arquivo"
        )

        local_file = gr.File(label="Selecionar arquivo", visible=True)

        local_path = gr.Textbox(
            label="Caminho no servidor (/content/arquivo.txt)",
            visible=False
        )

        def toggle_input(mode):
            if mode == "Upload":
                return gr.update(visible=True), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True)

        input_mode.change(
            toggle_input,
            inputs=input_mode,
            outputs=[local_file, local_path]
        )

        remote_name = gr.Textbox(label="Nome do remote", value="dbox")

        remote_type = gr.Dropdown(
            ["dropbox", "drive", "onedrive"],
            value="dropbox",
            label="Tipo de remote"
        )

        token = gr.Textbox(label="Token JSON", lines=2, type="password")

        use_crypt = gr.Checkbox(label="Usar criptografia")

        crypt_password = gr.Textbox(label="Senha crypt", type="password")

        encrypt_btn = gr.Button("Enviar")

        encrypt_output = gr.Textbox(lines=15)

        encrypt_btn.click(
            encrypt_file,
            inputs=[
                input_mode,
                local_file,
                local_path,
                remote_name,
                remote_type,
                token,
                use_crypt,
                crypt_password
            ],
            outputs=encrypt_output
        )

    
    # ABA DECRYPT
    
    with gr.Tab("Decrypt / Restore"):

        remote_name_r = gr.Textbox(label="Nome do remote", value="dbox")

        use_crypt_r = gr.Checkbox(label="Arquivo criptografado", value=True)

        decrypt_btn = gr.Button("Restaurar")

        download_file = gr.File(label="Baixar arquivo restaurado")

        decrypt_output = gr.Textbox(lines=15)

        decrypt_btn.click(
            decrypt_file,
            inputs=[remote_name_r, use_crypt_r],
            outputs=[download_file, decrypt_output]
        )

    # Aba remote para remote
   
    with gr.Tab("Backup Remote → Remote"):

        source_remote = gr.Textbox(label="Remote de origem", value="drive")
        source_path = gr.Textbox(label="Caminho no remote de origem", value="/backup_folder")

        dest_remote = gr.Textbox(label="Remote de destino", value="dbox")
        dest_type = gr.Dropdown(
            ["dropbox", "drive", "onedrive"],
            value="dropbox",
            label="Tipo do remote de destino"
        )
        dest_token = gr.Textbox(label="Token JSON do remote destino", lines=2, type="password")

        use_crypt_r2r = gr.Checkbox(label="Usar criptografia no destino")

        crypt_password_r2r = gr.Textbox(label="Senha crypt (se usar criptografia)", type="password")

        r2r_btn = gr.Button("Iniciar Backup Remote→Remote")

        r2r_output = gr.Textbox(lines=15)

        r2r_btn.click(
            remote_to_remote_backup,
            inputs=[
                source_remote,
                source_path,
                dest_remote,
                dest_type,
                dest_token,
                use_crypt_r2r,
                crypt_password_r2r
            ],
            outputs=r2r_output
        )


if __name__ == "__main__":
    demo.launch(share=True, debug=True)