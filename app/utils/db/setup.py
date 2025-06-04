import configparser
import os
import time
import psycopg2

def load_config():
    config = configparser.ConfigParser()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    config_path = os.path.join(base_dir, ".config")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado em {config_path}")
    config.read(config_path)
    if "DATABASE" not in config:
        raise RuntimeError("Seção [DATABASE] não encontrada no arquivo .config")
    return config["DATABASE"]


def get_db_connection():
    db_config = load_config()
    return psycopg2.connect(
        host=db_config.get('host', 'localhost'),
        database=db_config.get('database'),
        user=db_config.get('user'),
        password=db_config.get('password'),
        port=db_config.get('port')
    )

def wait_for_db():
    print("Aguardando banco de dados...")
    while True:
        try:
            conn = get_db_connection()
            conn.close()
            print("Banco disponível!")
            break
        except Exception as e:
            print(f"Erro de conexão: {e}. Tentando novamente em 2 segundos...")
            time.sleep(2)
