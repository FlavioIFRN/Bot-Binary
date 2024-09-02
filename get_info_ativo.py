from iqoptionapi.stable_api import IQ_Option
import time

# Configurações de login
email = "flavio.pessoalbr@gmail.com"
password = "32412426Aabcz@"

# Conectar à IQ Option
iqoption = IQ_Option(email, password)
iqoption.connect()

# Verificar se a conexão foi bem-sucedida
if iqoption.check_connect():
    print("Conectado com sucesso!")
else:
    print("Erro ao conectar")
    exit()

# Função para obter informações detalhadas de um par específico
def get_asset_info(pair):
    # Atualiza a lista de ativos
    iqoption.update_ACTIVES_OPCODE()
    assets_info = iqoption.get_all_open_time()
    
    # Verificar se o par existe e se está disponível
    for asset_type, assets in assets_info.items():
        if pair in assets:
            info = assets[pair]
            if info["open"]:
                print(f"Par: {pair}")
                print("Status: Aberto")
                
                # Inicia o stream de velas (candles) de 1 minuto para o par
                iqoption.start_candles_stream(pair, 1, 1)
                time.sleep(1)
                
                # Obtém as informações do candle atual
                candles = iqoption.get_realtime_candles(pair, 1)
                for timestamp, data in candles.items():
                    print(f"Preço de abertura: {data['open']}")
                    print(f"Preço de fechamento: {data['close']}")
                    print(f"Preço mais alto: {data['max']}")
                    print(f"Preço mais baixo: {data['min']}")
                    print(f"Volume: {data['volume']}")
                
                iqoption.stop_candles_stream(pair, 1)
                
            else:
                print(f"Par: {pair}")
                print("Status: Fechado")
                if 'open_time' in info and isinstance(info['open_time'], dict):
                    open_time = info['open_time'].get('seconds')
                    if open_time:
                        print(f"Próxima abertura: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(open_time))}")
            
            # Detalhes adicionais do ativo
            print(f"Tipo de ativo: {info['instrument_type']}")
            return
    
    print("Par não encontrado ou não disponível.")

# Informe o par desejado
pair = input("Informe o par de moedas ou ativo: ").upper()

# Obter e exibir as informações detalhadas do par
get_asset_info(pair)

# Fechar a conexão
iqoption.api.close()
