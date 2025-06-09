# CÓDIGO DE TESTE - Focado em resolver o problema da avaliação por estrelas
import os
from flask import Flask, request, jsonify
import requests

# --- Início da sua Ficha de Informações ---
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN") 
# Verifique se este é o ID correto do seu campo de AVALIAÇÃO (Rating/Emoji)
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

    # --- LÓGICA DE TESTE PARA AVALIAR ---
    if action == 'avaliar':
        nota = request.args.get('nota')
        if not nota:
            return "Erro: Nota não fornecida.", 400

        # Payload de teste: atualiza APENAS o campo personalizado
        payload = {
            "custom_fields": [
                {
                    "id": ID_CAMPO_AVALIACAO, 
                    "value": int(nota) # Tenta enviar o número da nota
                }
            ]
        }
        
        # Envia a requisição para a API do ClickUp
        update_url = f"https://api.clickup.com/api/v2/task/{task_id}"
        response_update = requests.put(update_url, json=payload, headers=headers)
        
        # Esta linha é a mais importante. Ela vai imprimir a resposta completa do ClickUp
        print("--- RESPOSTA DA API DO CLICKUP ---")
        print(response_update.json())
        print("---------------------------------")
        
        return f"Teste com nota {nota} enviado. Verifique a tarefa no ClickUp e os logs na Vercel."
    
    # Mantemos a lógica de reabrir para não quebrar o outro botão
    elif action == 'reabrir':
        return "Ação 'reabrir' recebida, mas não executada neste teste."

    return "Ação desconhecida.", 400

# Esta parte faz o servidor rodar
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
