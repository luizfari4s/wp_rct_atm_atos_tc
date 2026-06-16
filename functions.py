def carregamento(prefixo, path):
    import pandas as pd
    import glob
    import os

    # Busca CSV e Excel
    arquivos = glob.glob(os.path.join(path, f"{prefixo}*.csv")) + \
               glob.glob(os.path.join(path, f"{prefixo}*.xlsx")) + \
               glob.glob(os.path.join(path, f"{prefixo}*.xls"))

    dfs = []

    for arq in arquivos:
        extensao = os.path.splitext(arq)[1].lower()

        if extensao == ".csv":
            df = pd.read_csv(arq, sep=';', low_memory=False)

        elif extensao in [".xlsx", ".xls"]:
            df = pd.read_excel(arq)

        else:
            continue  # ignora formatos desconhecidos

        dfs.append(df)

    if not dfs:
        raise ValueError("Nenhum arquivo encontrado para o prefixo informado.")

    df_final = pd.concat(dfs, ignore_index=True)

     

    

    return df_final

def normalize(df):
    import pandas as pd
    print('\n')

    print("Entrada da função de normalização")
    print("Menor data encontrada:", df['DiaDeCompra'].min(),' | ', "Maior data encontrada:", df['DiaDeCompra'].max())

    print('\n')

    shape_init = df.shape[0]
    df.DiaDeCompra = pd.to_datetime(df.DiaDeCompra, format='%d/%m/%Y')
    df['mes_ref'] = df.DiaDeCompra.dt.to_period('M')
    df['ano_ref'] = df.DiaDeCompra.dt.to_period('Y')
    df['len_us'] = df['UserPS'].str.len()
    df['len_us'] = df['UserPS'].str.len()
   

    bs_9 = df.loc[df.len_us == 9].copy()
    bs_8 = df.loc[df.len_us == 8].copy()
    bs_14 = df.loc[df.len_us == 14].copy() # Mesclado OOH & IHS + IBS
    bs_7 = df.loc[df.len_us == 7].copy()
    bs_6 = df.loc[df.len_us == 6].copy()

    bs_10 = df.loc[df.len_us == 10].copy() # prefixo br-OOH
    bs_11 = df.loc[df.len_us == 11].copy() # prefixo br-OOH
    bs_12 = df.loc[df.len_us == 12].copy() # prefixo br-OOH
    bs_13 = df.loc[df.len_us == 13].copy() # prefixo br-OOH
    bs_15 = df.loc[df.len_us == 15].copy() # prefixo br-OOH

    bs_8.loc[(bs_8.len_us == 8), 'UserPS'] = (bs_8.UserPS.astype(int) - 55000000) + 550000000

    mask = ~(bs_14['Prefijo'].isin(['OOH']))

    bs_14.loc[mask, 'UserPS'] = (
        bs_14.loc[mask, 'UserPS']
        .str.replace('ih', '', regex=False)
        .str.split('-', n=1).str[0]
    )

    bs_7.loc[(bs_7.len_us == 7), 'UserPS'] = (bs_7.UserPS.astype(int) - 5500000) + 550000000

    bs_6.loc[(bs_6.len_us == 6), 'UserPS'] = (bs_6.UserPS.astype(int) - 550000) + 550000000

    df = pd.concat([bs_9, bs_8, bs_14, bs_7, bs_6, bs_10, bs_11, bs_12, bs_13, bs_15])

    df['len_us'] = df['UserPS'].str.len()

    shape_final = df.shape[0]
    
    bool_rt = shape_init + shape_final

    if bool_rt:
        print("Dimensão entrada saida iguais\n")
    else:
        print("Verificar função de normalização da base de atos rep7\n")

    

    return df

def atualizar_base(df,inicio,fim):
    from datetime import datetime
    import pandas as pd
    path = 'C:/Users/70089581/Kantar/BKO - dados-ops/do_rep7/'
    # 1. Pegar apenas o mês mais recente
    # mes_recente = df['mes_ref'].max()
    inicio_fmt = pd.to_datetime(inicio)
    fim_fmt = pd.to_datetime(fim)
    
   
    arquivo_saida = path + f'do_rep7_pstools_br_{inicio_fmt.date()}_a_{fim_fmt.date()}.xlsx'
    df.to_excel(arquivo_saida)
    print(f'Arquivo salvo em: {arquivo_saida}')

    print(f"atualizar_base: Arquivo Excel criado com sucesso! Salvo na pasta sincronizada do SharePoint \n")
    return df

def atualizar_prealoc_atos(prealoc,mes_recente):
    path = "c:/Users/70089581/Kantar/BKO - dados-ops/do_prealoc_atos/"
    merged = prealoc.merge(mes_recente, on='UserPS', how='inner')

    merged.UserPS = merged.UserPS.astype(int)
    merged.UserPS = merged.UserPS - 550000000

    merged.drop(columns='Origen')

    from datetime import datetime

    data_atual = datetime.now().strftime("%Y%m%d")

    merged.drop(columns='Unnamed: 9',inplace=True)
    arquivo_saida = path + f'do_prealoc_atos_{data_atual}.xlsx'
    merged.to_excel(arquivo_saida, index=False)

    print(f'Arquivo salvo em: {arquivo_saida}')

    print(f"atualizar_prealoc_atos: Arquivo Excel criado com sucesso! Salvo na pasta sincronizada do SharePoint \n")

    path

def atualizar_base_criterio(prealoc,rep7):
    path = "c:/Users/70089581/Kantar/BKO - dados-ops/do_base_criterio/"

    merged = prealoc.merge(rep7, on='UserPS', how='inner')

    merged.UserPS = merged.UserPS.astype(int)
    merged.UserPS = merged.UserPS - 550000000

    from datetime import datetime
    
    data_atual = datetime.now().strftime("%Y%m%d")

    #merged.drop(columns='Unnamed: 9',inplace=True)

    df_grouped, df_dist = faixa_de_atos(merged.copy())

    # Nome do arquivo
    arquivo_saida = path + f'do_base_criterio_{data_atual}.xlsx'
    import pandas as pd
    # Salvando os dois DataFrames em abas diferentes do mesmo Excel
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        df_grouped.to_excel(writer, sheet_name='FaixasAtos', index=False)
        df_dist.to_excel(writer, sheet_name='Distribuicao', index=False)

    print(f'Arquivo salvo em: {arquivo_saida}')

    print(f"atualizar_base_critério: Arquivo Excel criado com sucesso! Salvo na pasta sincronizada do SharePoint \n")

def faixa_de_atos(df):
    # Normalização
    df.NumCompras = df.NumCompras.astype(int)
    df.UserPS = df.UserPS.astype(int)
    # print("step 5 - (Faixa de atos) Colunas: ", df.columns, "\n")

    df_grouped = df.groupby(['UserPS', 'Origen_GPM'])['NumCompras'].sum().reset_index().sort_values(by='NumCompras', ascending=False)

    import pandas as pd

    # Definir os limites das faixas (bins) e os rótulos correspondentes
    bins = [0, 4, 9, 14, 19, 24, float('inf')]
    labels = ['1 a 4 atos', '5 a 9 atos', '10 a 14 atos', '15 a 19 atos', '20 a 24 atos', '25+ atos']

    # Criar a nova coluna 'FaixaNumCompras' usando pd.cut
    df_grouped['FaixaNumCompras'] = pd.cut(df_grouped['NumCompras'], bins=bins, labels=labels, right=True)

    print("Usuários únicos que registráram no periodo produtivo atual: ", df_grouped.UserPS.nunique(), "\n")

    from datetime import datetime

    data_atual = datetime.now()
    
    df_grouped['dt_process'] = data_atual

    df_grouped = df_grouped[['dt_process', 'UserPS', 'NumCompras', 'FaixaNumCompras','Origen_GPM']].copy()

    df_dist = df_grouped.groupby('FaixaNumCompras', observed=False)['UserPS'].count().reset_index()


    return df_grouped,df_dist

def pegar_arquivo_mais_recente(pasta, extensao=None):
    import os

    """
    Retorna o caminho do arquivo mais recente dentro da pasta.
    
    :param pasta: caminho da pasta
    :param extensao: opcional (ex: '.csv', '.xlsx')
    :return: caminho completo do arquivo mais recente
    """
    
    arquivos = [
        os.path.join(pasta, f)
        for f in os.listdir(pasta)
        if os.path.isfile(os.path.join(pasta, f))
    ]
    
    # Filtrar por extensão (se informado)
    if extensao:
        arquivos = [f for f in arquivos if f.lower().endswith(extensao.lower())]
    
    if not arquivos:
        return None

    arquivo_mais_recente = max(arquivos, key=os.path.getctime)
    
    return arquivo_mais_recente

def disparar_email(path, str, subject):

    import win32com.client as win32
    from datetime import datetime
    import os
    import time

    os.system('start outlook')


    data_atual = datetime.now().strftime("%Y/%m/%d")

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)

    mail.To = str
    mail.CC = 'fabio.shiraishi@wp.numerator.com; luiz.farias@wp.numerator.com' 
    
    mail.Subject = f'{subject} | {data_atual}'
    mail.Body = 'Segue em anexo.'

    mail.Attachments.Add(path)

    mail.Send()

    print(f'arquivo: {path}\n\ndisparado para: {str}')

    time.sleep(60)

    os.system('taskkill /f /im outlook.exe')

    print(f'sessão finalizada')

import pandas as pd

def filtrar_periodo_vigente( 
    df_dados: pd.DataFrame,
    df_calendar: pd.DataFrame,
    coluna_data: str,
    data_referencia=None
) -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:

    # Define data atual caso não informada
    if data_referencia is None:
        data_referencia = pd.Timestamp.today().normalize()

    # Cópias para evitar alteração no dataframe original
    df = df_dados.copy()
    calendario = df_calendar.copy()

    # Padronizar tipos datetime
    df[coluna_data] = (
        pd.to_datetime(df[coluna_data], errors='coerce')
        .dt.normalize()
    )

    calendario['Desde'] = (
        pd.to_datetime(calendario['Desde'], errors='coerce')
        .dt.normalize()
    )

    calendario['Hasta'] = (
        pd.to_datetime(calendario['Hasta'], errors='coerce')
        .dt.normalize()
    )

    # Debug
    print("QTD dados original qmob:", df.shape[0])
    print("Coluna data:", coluna_data)
    

    # Encontrar período vigente
    periodo = calendario[
        (data_referencia >= calendario['Desde']) &
        (data_referencia <= calendario['Hasta'])
    ]

    if periodo.empty:
        raise ValueError(
            f'Nenhum período fiscal encontrado para a data {data_referencia}'
        )

    # Captura início e fim do período
    inicio = periodo.iloc[0]['Desde']
    fim = periodo.iloc[0]['Hasta']

    print(f"Período encontrado: {inicio} até {fim}")

    # Filtrar dados
    df_filtrado = df[
        (df[coluna_data] >= inicio) &
        (df[coluna_data] <= fim)
    ]

    # Debug final
    print("QTD após filtro no periodo produtivo atual:", df_filtrado.shape[0])

    print('\n\n')

    print("Entrada da Função de filtro de periodo")
    print("Menor data encontrada:", df['DiaDeCompra'].min(),' | ', "Maior data encontrada:", df['DiaDeCompra'].max())

    print('\n\n')


    print("Saida da Função de filtro de periodo : Dados filtrados")
    print("Menor data encontrada:", df_filtrado['DiaDeCompra'].min(),' | ', "Maior data encontrada:", df_filtrado['DiaDeCompra'].max())

    print('\n\n')

    return df_filtrado, inicio, fim