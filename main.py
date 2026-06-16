import functions 

def main():

    import time
    
    pre_aloc = functions.carregamento(
        path='C:/Users/70089581/Kantar/BKO - dados-ops/do_preal_fornecedor/ref_prealoc',
        prefixo='pre'
    )
    
    trocas = {
    '{GroupId}' : 'UserPS',
    '{IndividualId}' : 'individual-id',
    '{CreationTimeStamp}' : 'created_at',
    'Origen' : 'Origen_GPM'
    }

    pre_aloc.rename(columns=trocas, inplace=True)

    pre_aloc['UserPS'] = pre_aloc['UserPS'].astype(str)

    print("qty prealoca: ",pre_aloc.shape[0])

    df_cldar = functions.carregamento(
        path='C:/Users/70089581/Kantar/BKO - dados-ops/do_calendario_fiscal',
        prefixo='do_cal'
        )    

    rep7 = functions.carregamento(
        path='C:/Users/70089581/Kantar/BKO - dados-ops/do_rep7/bruto',
        prefixo='Brasil-Reporte-7'
    )
    rep7 = functions.normalize(rep7)

    rep7, inicio, fim = functions.filtrar_periodo_vigente(
        rep7, 
        df_cldar,
        coluna_data='DiaDeCompra'
    )

    



    functions.atualizar_base(rep7, inicio, fim)

    # Ajustar filtro de mês na função para que o rep7 entre com todos os dados na próxima etapa do fluxo
    functions.atualizar_base_criterio(pre_aloc,rep7)

    functions.atualizar_prealoc_atos(pre_aloc,rep7)

    # Disparo Top Client
    tc = 'Arthurribeiro@orbitustech.com; viniciusoliveira@orbitustech.com; landing-worldpanel@orbitustech.com; talita.cesar@wp.numerator.com; brenno.todao@topclient.com.br'
    subject = 'Relatório Atos Brutos Top Client'
    path = functions.pegar_arquivo_mais_recente('c:/Users/70089581/Kantar/BKO - dados-ops/do_prealoc_atos', extensao=None)
    time.sleep(10)
    functions.disparar_email(path, tc, subject)
    
    time.sleep(20)
    
    # Disparo Interno IHS
    interno = 'Marilia.Santana@wp.numerator.com; talita.cesar@wp.numerator.com; Josane.Tonello@wp.numerator.com'
    subject_2 = 'Relatório Critério de Atos'
    path_2 = functions.pegar_arquivo_mais_recente('c:/Users/70089581/Kantar/BKO - dados-ops/do_base_criterio', extensao=None)
    time.sleep(10)

    functions.disparar_email(path_2, interno, subject_2)

if __name__ == '__main__':  
    main() 