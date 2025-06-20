import subprocess
import time
import os
import json
import atexit # Para garantir que o ngrok seja encerrado ao sair

print("AutoTrader...")

# Importa a função create_app do seu pacote 'app'
from app import create_app

# Cria a instância do aplicativo Flask
app = create_app()

# Variável para armazenar o processo do ngrok
ngrok_process = None

def start_ngrok():
    global ngrok_process
    print("Starting ngrok tunnel...")
    try:
        # Inicia o ngrok em segundo plano, redirecionando a saída para não poluir o terminal
        ngrok_process = subprocess.Popen(["ngrok", "http", "5000"],
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
        print("Ngrok process started. Waiting for tunnel to establish...")
        time.sleep(5) # Dá um tempo para o ngrok iniciar e o túnel ser estabelecido

        ngrok_url = None
        # Tenta obter a URL do túnel ngrok da API local
        for _ in range(10): # Tenta até 10 vezes (20 segundos)
            try:
                ngrok_api_response = subprocess.check_output(["curl", "-s", "http://localhost:4040/api/tunnels"])
                tunnels_data = json.loads(ngrok_api_response)

                if tunnels_data and 'tunnels' in tunnels_data and len(tunnels_data['tunnels']) > 0:
                    for tunnel in tunnels_data['tunnels']:
                        if tunnel['proto'] == 'https' and 'public_url' in tunnel:
                            ngrok_url = tunnel['public_url']
                            break
                    if ngrok_url:
                        break # Sai do loop se a URL for encontrada
            except Exception as e:
                # print(f"Warning: Could not get ngrok tunnel info ({e}). Retrying...") # Descomente para debug
                pass # Silencia erros de conexão temporários

            time.sleep(2) # Espera antes de tentar novamente

        if ngrok_url:
            print(f"Ngrok tunnel established: {ngrok_url}")
        else:
            print("Could not get ngrok tunnel URL after multiple attempts.")
            print("Please check if ngrok is running correctly or visit http://localhost:4040.")

    except FileNotFoundError:
        print("Error: ngrok not found. Please ensure ngrok is installed and in your system's PATH.")
        print("You can download it from https://ngrok.com/download")
        ngrok_process = None
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        ngrok_process = None

    # Registra uma função para ser executada quando o programa terminar
    atexit.register(stop_ngrok)

def stop_ngrok():
    global ngrok_process
    if ngrok_process:
        print("Terminating ngrok process...")
        ngrok_process.terminate()
        ngrok_process.wait() # Espera o processo terminar
        print("Ngrok process terminated.")

if __name__ == "__main__":
    # Inicia o ngrok apenas se o script for executado diretamente
    start_ngrok()

    print("Starting Flask server...")
    # Inicia o Flask
    # Definindo host="0.0.0.0" permite que ele seja acessível de fora do localhost,
    # o que é necessário para o ngrok se conectar.
    # debug=True é ideal para desenvolvimento.
    app.run(host="0.0.0.0", port=5000, debug=True)

    print("Flask server stopped.")
    # A função stop_ngrok já será chamada automaticamente devido ao atexit.register

