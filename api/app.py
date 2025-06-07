# Importa a biblioteca 'os' para ler variáveis de ambiente
import os
from flask import Flask, request, jsonify
import requests

# --- Início da sua Ficha de Informações ---
# AGORA VAMOS LER O TOKEN DE UM LUGAR SEGURO (Vercel Environment Variables)
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN") 

STATUS_EM_ABERTO = "EM ATENDIMENTO"
STATUS_ENCERRADO = "ENCERRADO"
PRIORIDADE_URGENTE = 1


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

    # Lógica para REABRIR (antigo "NÃO")
    if action == 'reabrir':
        payload = { "status": STATUS_EM_ABERTO, "priority": PRIORIDADE_URGENTE }
        response = requests.put(update_url, json=payload, headers=headers)
        print("Resposta da API:", response.json())
        
        comment_payload = {"comment_text": "Chamado reaberto pelo cliente via link no e-mail."}
        requests.post(f"{update_url}/comment", json=comment_payload, headers=headers)
        
        return "Obrigado! Seu chamado foi reaberto e nossa equipe já foi notificada."
    
    # Lógica para ENCERRAR (antigo "SIM")
    elif action == 'encerrar':
        payload = { "status": STATUS_ENCERRADO }
        response = requests.put(update_url, json=payload, headers=headers)
        print("Resposta da API:", response.json())

        return "Obrigado por sua confirmação! O chamado foi encerrado com sucesso."
    
    return "Ação desconhecida.", 400

# Esta parte faz o servidor rodar
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
