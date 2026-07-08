import functions 

def main():

    import time
    
    pre_aloc = functions.carregamento(
        path='C:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_preal_fornecedor/ref_prealoc',
        prefixo='pre'
    )
    
    trocas = {
        '{GroupId}' : 'UserPS',
        '{IndividualId}' : 'individual-id',
        '{CreationTimeStamp}' : 'created_at',
        'Origen' : 'Origen_GPM'
    }
    pre_aloc.rename(
        columns=trocas, 
        inplace=True)
    
    pre_aloc['UserPS'] = pre_aloc['UserPS'].astype(str)
    print("qty prealoca: ",pre_aloc.shape[0])

    df_cldar = functions.carregamento(
        path='C:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_calendario_fiscal',
        prefixo='do_cal'
        )    

    rep7 = functions.carregamento(
        path='C:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_rep7/bruto',
        prefixo='Brasil-Reporte-7'
    )

    rep7 = functions.normalize(rep7)
    rep7_nf = rep7.copy()

    rep7, inicio, fim = functions.filtrar_periodo_vigente(
        rep7, 
        df_cldar,
        coluna_data='DiaDeCompra'
    )

    out = functions.inf_consolidada(
        rep7_nf,
        df_cldar,
        pre_aloc)

    functions.atualizar_consolidado(
        out,
        path_cons='C:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_preal_fornecedor/ref_cosolidado'
        )

    functions.atualizar_base(
        rep7, 
        inicio,
        fim, 
        path_rep7 = 'C:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_rep7/')

    # Ajustar filtro de mês na função para que o rep7 entre com todos os dados na próxima etapa do fluxo
    functions.atualizar_base_criterio(
        pre_aloc,
        rep7,
        path_base_criterio='c:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_base_criterio/')

    functions.atualizar_prealoc_atos(
        pre_aloc,
        rep7,
        path_prealoc_atos = 'c:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_prealoc_atos/')

    '''# Disparo Top Client
    functions.disparar_email(
        path = functions.pegar_arquivo_mais_recente('c:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_prealoc_atos', extensao=None), 
        dest =  'fabio.shiraishi@wp.numerator.com; ' \
                'Arthurribeiro@orbitustech.com; ' \
                'viniciusoliveira@orbitustech.com; ' \
                'landing-worldpanel@orbitustech.com; ' \
                'talita.cesar@wp.numerator.com; ' \
                'brenno.todao@topclient.com.br', 
        subject = 'Relatório Atos Brutos Top Client')
    
    time.sleep(20)
    
    # Disparo Interno Recrutamento
    time.sleep(10)

    functions.disparar_email(
        path = functions.pegar_arquivo_mais_recente('c:/Users/luiz.farias/Numerator International/BKO - projeto-dados-ops/do_base_criterio', extensao=None), 
        dest = 'fabio.shiraishi@wp.numerator.com; ' \
                  'Marilia.Santana@wp.numerator.com; ' \
                  'talita.cesar@wp.numerator.com; ' \
                  'Josane.Tonello@wp.numerator.com; '\
                  'gabriel.leite@wp.numerator.com', 
        subject = 'Relatório Critério de Atos')'''

if __name__ == '__main__':  
    main() 