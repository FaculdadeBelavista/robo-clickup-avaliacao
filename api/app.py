# Versão Final - Com Página de Confirmação em HTML Personalizada
import os
from flask import Flask, request
import requests

# --- Início da sua Ficha de Informações ---
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN") 
STATUS_EM_ABERTO = "EM ATENDIMENTO"
STATUS_ENCERRADO = "ENCERRADO"
PRIORIDADE_URGENTE = 1
ID_CAMPO_AVALIACAO = "ca70dc3d-bae6-4529-bc2b-b762f220d817"
# --- Fim da sua Ficha de Informações ---

headers = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

app = Flask(__name__)

# --- FUNÇÃO ATUALIZADA PARA GERAR A PÁGINA DE RESPOSTA ---
def gerar_pagina_resposta(titulo, mensagem):
    """Gera uma página HTML de resposta bonita e personalizada com logo."""
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                color: #333;
            }}
            .container {{
                text-align: center;
                background-color: #ffffff;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .logo {{
                max-width: 250px;
                margin-bottom: 25px;
            }}
            h1 {{
                font-size: 24px;
                color: #A738FF;
            }}
            p {{
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://inside.faculdadebelavista.edu.br/logo_01_escuro.png" alt="Logo Faculdade Belavista" class="logo">
            <h1>{titulo}</h1>
            <p>{mensagem}</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/avaliacao_tec', methods=['GET'])
def handle_evaluation():
    task_id = request.args.get('id_tarefa')
    action = request.args.get('acao')
    
    if not task_id or not action:
        return gerar_pagina_resposta("Erro na Solicitação", "Os parâmetros necessários não foram encontrados na URL."), 400

    print(f"Recebido: id_tarefa={task_id}, acao={action}")
    
    task_url = f"https://api.clickup.com/api/v2/task/{task_id}"

    # Lógica para REABRIR
    if action == 'reabrir':
        payload = { "status": STATUS_EM_ABERTO, "priority": PRIORIDADE_URGENTE }
        requests.put(task_url, json=payload, headers=headers)
        
        comment_payload = {"comment_text": "Chamado reaberto pelo cliente via link no e-mail."}
        requests.post(f"{task_url}/comment", json=comment_payload, headers=headers)
        
        return gerar_pagina_resposta("Solicitação Recebida!", "Seu chamado foi reaberto e nossa equipe já foi notificada.")
    
    # Lógica para AVALIAR
    elif action == 'avaliar':
        nota = request.args.get('nota')
        if not nota:
            return gerar_pagina_resposta("Erro", "Nota inválida ou não fornecida."), 400

        # Ação 1: Preencher o campo de avaliação
        field_update_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{ID_CAMPO_AVALIACAO}"
        field_payload = { "value": int(nota) }
        requests.post(field_update_url, json=field_payload, headers=headers)

        # Ação 2: Mudar o status da tarefa
        status_payload = { "status": STATUS_ENCERRADO }
        requests.put(task_url, json=status_payload, headers=headers)
        
        return gerar_pagina_resposta("Avaliação Recebida!", f"Obrigado por sua avaliação de {nota} estrela(s)! O chamado foi encerrado.")
    
    return gerar_pagina_resposta("Erro", "Ação desconhecida."), 400

# Esta parte faz o servidor rodar
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
