from iqoptionapi.stable_api import IQ_Option
import time
import pymysql
from datetime import datetime
import requests  # Nova importação

# Configurações de login da IQ Option
email = "flavio.pessoalbr@gmail.com"
password = "32412426Aabcz@"

# Configurações do banco de dados MySQL
db_host = "localhost"
db_user = "root"
db_password = ""
db_name = "binarias"
db_table = "timeframes"

# URL para notificar após atualização do banco de dados
notification_url = "http://127.0.0.1:8000/get-ativos"

# Conectar à IQ Option
iqoption = IQ_Option(email, password)
iqoption.connect()

# Verificar se a conexão foi bem-sucedida
if iqoption.check_connect():
    print("Conectado com sucesso!")
else:
    print("Erro ao conectar")
    exit()

# Conectar ao banco de dados MySQL
connection = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name,
    cursorclass=pymysql.cursors.DictCursor
)

# Dicionário para armazenar o preço de abertura fixo por par
fixed_open_prices = {}

# Função para iniciar o stream de velas de 1 minuto para os pares desejados
def start_stream(pairs):
    for pair in pairs:
        iqoption.start_candles_stream(pair, 1, 1)
        # Notificar a URL após a operação no banco de dados
        

# Função para salvar ou atualizar as informações no banco de dados
def save_or_update_data(pair, data):
    with connection.cursor() as cursor:
        # Converter o timestamp do candle para o formato do banco de dados
        candle_time = datetime.fromtimestamp(data['from']).strftime('%Y-%m-%d %H:%M:00')

        # Verificar se já existe um registro para o mesmo ativo e timeframe com base no 'created_at'
        sql_check = f"""
        SELECT * FROM {db_table} 
        WHERE ativo=%s AND timeframe='M1' 
        AND created_at=%s LIMIT 1"""
        cursor.execute(sql_check, (pair, candle_time))
        result = cursor.fetchone()

        # Verificar se o preço de abertura já foi fixado para este candle
        if pair not in fixed_open_prices or fixed_open_prices[pair]['timestamp'] != data['from']:
            fixed_open_prices[pair] = {
                'open': data['open'],
                'timestamp': data['from']
            }

        open_price = fixed_open_prices[pair]['open']

        if result:
            # Atualizar o registro existente
            sql_update = f"""UPDATE {db_table} SET 
                             close=%s, high=%s, low=%s, vol=%s, updated_at=NOW()
                             WHERE id=%s"""
            cursor.execute(sql_update, (data['close'], data['max'], data['min'], data['volume'], result['id']))
        else:
            # Inserir um novo registro
            sql_insert = f"""INSERT INTO {db_table} 
                             (ativo, open, close, high, low, vol, timeframe, created_at, updated_at)
                             VALUES (%s, %s, %s, %s, %s, %s, 'M1', %s, NOW())"""
            cursor.execute(sql_insert, (pair, open_price, data['close'], data['max'], data['min'], data['volume'], candle_time))

        connection.commit()

        

# Função para exibir as informações a cada tick e salvar no banco de dados
def monitor_pairs(pairs):
    while True:
        for pair in pairs:
            candles = iqoption.get_realtime_candles(pair, 1)
            # Iterar sobre uma lista das chaves para evitar problemas
            for timestamp in list(candles.keys()):
                data = candles[timestamp]
                print(f"Par: {pair}")
                print(f"Preço de abertura: {fixed_open_prices.get(pair, {}).get('open', data['open'])}")
                print(f"Preço de fechamento: {data['close']}")
                print(f"Preço mais alto: {data['max']}")
                print(f"Preço mais baixo: {data['min']}")
                print(f"Volume: {data['volume']}")
                print("-" * 30)
                save_or_update_data(pair, data)
                
        try:
            response = requests.get(notification_url)
            if response.status_code == 200:
                print(f"Notificação enviada para {notification_url}")
            else:
                print(f"Falha ao notificar {notification_url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Erro ao tentar notificar {notification_url}: {e}")
        time.sleep(1)  # Intervalo de 1 segundo para não sobrecarregar a API
        

# Iniciar o stream de velas e monitorar os pares
pairs = ["EURUSD", "EURGBP", "EURJPY"]
start_stream(pairs)
monitor_pairs(pairs)

# Fechar a conexão ao banco de dados (quando necessário)
# connection.close()
