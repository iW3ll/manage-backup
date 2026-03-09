import gradio as gr
from rclone_utils import install_rclone
from backup import criar_aba_backup
from restore import criar_aba_restore

# Instala o rclone (se necessário)
install_rclone()

# Cria as abas
demo_backup = criar_aba_backup()
demo_restore = criar_aba_restore()

# Combina em um só aplicativo com abas
with gr.Blocks(title="Rclone Backup e Restauração") as demo:
    gr.Markdown("""
    # Gerenciamento de backups com rclone
    Use as abas para fazer backup (enviar com ou sem criptografia) ou restaurar arquivos previamente criptografados.
    """)
    with gr.Tab("Backup"):
        # Incorpora o conteúdo da aba de backup
        for component in demo_backup.children:
            demo.__setattr__(component._id, component)  
            

from backup import backup_config
from restore import restore_files
from rclone_utils import remote_exists, create_remote

with gr.Blocks(title="Rclone Backup e Restauração") as demo:
    gr.Markdown("""
    # Gerenciamento de backups com rclone
    Use as abas para fazer backup (enviar com ou sem criptografia) ou restaurar arquivos previamente criptografados.
    """)

    with gr.Tab("Backup"):
        # Código da interface de backup (igual ao do backup.py, mas sem o Blocks externo)
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Origem")
                source_type = gr.Radio(choices=["Remote", "Local"], label="Tipo de origem", value="Remote")
                source_remote = gr.Textbox(label="Nome do remote de origem", value="drive", visible=True)
                source_path = gr.Textbox(label="Caminho do arquivo no remote", value="/rclone.conf", visible=True)
                local_file = gr.File(label="Arquivo local (upload)", visible=False)
                local_path = gr.Textbox(label="Caminho local (ex: /content/meu_arquivo.txt)", visible=False)

            with gr.Column():
                gr.Markdown("### Destino")
                dest_name = gr.Textbox(label="Nome do remote de destino", value="dbox",
                                       info="Ex: dbox (remote base, sem -crypt)")
                dest_type = gr.Dropdown(label="Tipo de remote", choices=["drive", "dropbox", "onedrive"], value="dropbox")
                use_existing_remote = gr.Checkbox(label="Usar remote já existente", value=True)
                client_id = gr.Textbox(label="Client ID (opcional)", visible=False)
                client_secret = gr.Textbox(label="Client Secret (opcional)", type="password", visible=False)
                token_json = gr.Textbox(label="Token JSON (opcional se usar remote existente)", lines=2, type="password",
                                        placeholder='{"access_token":"...", ...}')

        def toggle_remote_fields(use_existing):
            if use_existing:
                return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
            else:
                return gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)

        use_existing_remote.change(toggle_remote_fields, inputs=use_existing_remote,
                                   outputs=[client_id, client_secret, token_json])

        def toggle_source(choice):
            if choice == "Remote":
                return gr.update(visible=True), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

        source_type.change(toggle_source, inputs=source_type,
                           outputs=[source_remote, source_path, local_file, local_path])

        crypt_password = gr.Textbox(label="Senha de criptografia (opcional)", type="password",
                                    info="Se deixar em branco, o arquivo NÃO será criptografado.")

        backup_btn = gr.Button("Iniciar Backup")
        backup_output = gr.Textbox(label="Saída do Backup", lines=10)

        backup_btn.click(
            backup_config,
            inputs=[source_type, source_remote, source_path, local_file, local_path,
                    dest_name, dest_type, client_id, client_secret, token_json,
                    crypt_password, use_existing_remote],
            outputs=backup_output
        )

    with gr.Tab("Restaurar"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Remote crypt (já configurado)")
                crypt_name_rest = gr.Textbox(label="Nome do remote crypt", value="dbox-crypt",
                                             info="Ex: dbox-crypt (o remote que você usa para acessar os arquivos criptografados)")
                crypt_password_rest = gr.Textbox(label="Senha de criptografia", type="password")

            with gr.Column():
                gr.Markdown("### Destino da restauração")
                restore_dest_type = gr.Radio(choices=["Local", "Remoto"], label="Tipo de destino", value="Local")
                restore_local_path = gr.Textbox(label="Caminho local (ex: /content/restaurado)", value="/content/restaurado", visible=True)
                restore_remote_name = gr.Textbox(label="Nome do remote de destino (para restauração remota)", visible=False)
                restore_remote_path = gr.Textbox(label="Caminho no remote (opcional)", value="", visible=False)

        def toggle_restore_dest(choice):
            if choice == "Local":
                return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

        restore_dest_type.change(toggle_restore_dest, inputs=restore_dest_type,
                                 outputs=[restore_local_path, restore_remote_name, restore_remote_path])

        restore_btn = gr.Button("Restaurar Arquivos")
        restore_output = gr.Textbox(label="Saída da Restauração", lines=10)

        restore_btn.click(
            restore_files,
            inputs=[crypt_name_rest, crypt_password_rest,
                    restore_dest_type, restore_local_path, restore_remote_name, restore_remote_path],
            outputs=restore_output
        )

if __name__ == "__main__":
    demo.launch(debug=True, share=True)