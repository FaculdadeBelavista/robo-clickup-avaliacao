# Importa a biblioteca 'os' para ler variáveis de ambiente
import os
from flask import Flask, request, jsonify
import requests

# --- Início da sua Ficha de Informações ---
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN") 
STATUS_EM_ABERTO = "EM ATENDIMENTO"
STATUS_ENCERRADO = "ENCERRADO"
PRIORIDADE_URGENTE = 1
# Adicionamos o ID do seu novo campo de avaliação
ID_CAMPO_AVALIACAO = "ca70dc3d-bae6-4529-bc2b-b762f220d817"
# --- Fim da sua Ficha de Informações ---


headers = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

app = Flask(__name__)

@app.route('/avaliacao_tec', methods=['GET'])
def handle_evaluation():
    task_id = request.args.get('id_tarefa')
    action = request.args.get('acao')
    
    if not task_id or not action:
        return "Erro: Faltando parâmetros na URL.", 400

    print(f"Recebido: id_tarefa={task_id}, acao={action}")

    update_url = f"https://api.clickup.com/api/v2/task/{task_id}"

    # Lógica para REABRIR (Problema não resolvido)
    if action == 'reabrir':
        payload = { "status": STATUS_EM_ABERTO, "priority": PRIORIDADE_URGENTE }
        requests.put(update_url, json=payload, headers=headers)
        
        comment_payload = {"comment_text": "Chamado reaberto pelo cliente via link no e-mail."}
        requests.post(f"{update_url}/comment", json=comment_payload, headers=headers)
        
        return "Obrigado! Seu chamado foi reaberto e nossa equipe já foi notificada."
    
    # Lógica para AVALIAR (Quando o cliente clica na estrela)
    elif action == 'avaliar':
        nota = request.args.get('nota')
        if not nota:
            return "Erro: Nota não fornecida.", 400

        # Prepara os dados para atualizar o Status e o Campo de Avaliação
        payload = {
            "status": STATUS_ENCERRADO,
            "custom_fields": [
                {
                    "id": ID_CAMPO_AVALIACAO, 
                    "value": int(nota) # A MÁGICA: Apenas enviamos o número da nota!
                }
            ]
        }
        
        # Envia a requisição para a API do ClickUp
        response_update = requests.put(update_url, json=payload, headers=headers)
        print("Resposta da atualização de avaliação:", response_update.json())
        
        return f"Obrigado por sua avaliação de {nota} estrela(s)!"
    
    return "Ação desconhecida.", 400

# Esta parte faz o servidor rodar
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
