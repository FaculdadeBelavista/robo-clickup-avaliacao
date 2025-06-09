# Versão Final e Corrigida - Adicionada verificação para evitar reavaliação
import os
from flask import Flask, request, jsonify
import requests

# --- Início da sua Ficha de Informações ---
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN") 
STATUS_EM_ABERTO = "EM ATENDIMENTO"
STATUS_ENCERRADO = "ENCERRADO"
PRIORIDADE_URGENTE = 1
# Usando o ID que você encontrou para o campo de Avaliação
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

    task_url = f"https://api.clickup.com/api/v2/task/{task_id}"

    # Lógica para REABRIR
    if action == 'reabrir':
        payload = { "status": STATUS_EM_ABERTO, "priority": PRIORIDADE_URGENTE }
        requests.put(task_url, json=payload, headers=headers)
        
        comment_payload = {"comment_text": "Chamado reaberto pelo cliente via link no e-mail."}
        requests.post(f"{task_url}/comment", json=comment_payload, headers=headers)
        
        return "Obrigado! Seu chamado foi reaberto e nossa equipe já foi notificada."
    
    # Lógica para AVALIAR (Agora com verificação)
    elif action == 'avaliar':
        # --- PASSO NOVO: Ler o estado atual da tarefa ANTES de fazer qualquer coisa ---
        current_task_data = requests.get(task_url, headers=headers).json()
        
        # Procura pelo campo de avaliação nos dados da tarefa
        evaluation_field = None
        for field in current_task_data.get('custom_fields', []):
            if field.get('id') == ID_CAMPO_AVALIACAO:
                evaluation_field = field
                break

        # Verifica se o campo já tem um valor
        if evaluation_field and 'value' in evaluation_field:
            print("Tentativa de reavaliar um chamado já avaliado. Ação bloqueada.")
            return "Este chamado já foi avaliado anteriormente. Obrigado!"

        # Se não foi avaliado, continua com a lógica normal...
        nota = request.args.get('nota')
        if not nota:
            return "Erro: Nota não fornecida.", 400

        # --- AÇÃO 1: Preencher o campo de avaliação ---
        field_update_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{ID_CAMPO_AVALIACAO}"
        field_payload = { "value": int(nota) }
        response_field = requests.post(field_update_url, json=field_payload, headers=headers)
        print("Resposta do Campo Personalizado:", response_field.text)

        # --- AÇÃO 2: Mudar o status da tarefa ---
        status_payload = { "status": STATUS_ENCERRADO }
        response_status = requests.put(task_url, json=status_payload, headers=headers)
        print("Resposta da Mudança de Status:", response_status.json())
        
        return f"Obrigado por sua avaliação de {nota} estrela(s)! O chamado foi encerrado."
    
    return "Ação desconhecida.", 400

# Esta parte faz o servidor rodar
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
