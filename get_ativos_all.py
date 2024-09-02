from iqoptionapi.stable_api import IQ_Option

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

# Obter a lista de ativos disponíveis (digitais e binárias)
def get_all_available_assets():
    iqoption.update_ACTIVES_OPCODE()  # Atualiza a lista de ativos
    assets = iqoption.get_all_open_time()  # Obtém todos os ativos e seus status
    
    available_assets = {}
    for asset_type, assets_info in assets.items():
        for asset, info in assets_info.items():
            if info["open"]:
                available_assets[asset] = {
                    'tipo': asset_type,
                    'instrumento': info['instrument_type']
                }
    
    return available_assets

# Coletar os dados dos ativos disponíveis agora (digitais e binárias)
all_available_assets = get_all_available_assets()

# Exibir os ativos disponíveis
for asset, info in all_available_assets.items():
    if(info['tipo'] == 'digital' or info['tipo'] == 'forex'):
        print(f"Ativo: {asset}")

# Fechar a conexão
iqoption.api.close()
