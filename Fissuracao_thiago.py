import pandas as pd
import os
import math
from datetime import datetime

def obter_w_perm(ambiente):
    """Retorna o valor de w_perm de acordo com a classe de agressividade ambiental"""
    valores_w_perm = {
        1: 0.4,  # Classe I - Ambiente Rural ou Urbano seco (não agressivo)
        2: 0.3,  # Classe II - Ambiente Urbano úmido/marinho
        3: 0.2,  # Classe III - Ambiente Marinho ou Industrial
        4: 0.1   # Classe IV - Ambiente com agressividade muito forte
    }
    return valores_w_perm.get(ambiente, 0.3)  # Retorna 0.3 como padrão (Classe II)

def calcular_momento_viga_biapoiada(vao, carga):
    """Calcula o momento máximo para uma viga biapoiada com carga distribuída uniforme"""
    # Momento no meio do vão: M = (q * L²) / 8
    momento = (carga * vao**2) / 8
    return momento

def calcular_tensao_armadura(momento, altura_util, largura, area_aco):
    """Calcula a tensão na armadura a partir do momento fletor"""
    # Cálculo simplificado da tensão na armadura usando o braço de alavanca aproximado
    # σs = M / (z * As), onde z é aproximadamente 0.9d
    z = 0.9 * altura_util
    tensao = momento * 1000000 / (z * area_aco)  # Convertendo kN.m para N.mm
    return tensao

def verificar_fissuracao():
    print("\n===== VERIFICAÇÃO DE FISSURAÇÃO EM VIGAS BIAPOIADAS DE CONCRETO =====\n")
    print("DADOS DA VIGA BIAPOIADA:")
    
    try:
        # Dados geométricos da viga
        vao = float(input("Comprimento do vão da viga (L) [m]: "))
        altura = float(input("Altura da viga (h) [cm]: "))
        largura = float(input("Largura da viga (b) [cm]: "))
        d = float(input("Altura útil (d) [cm]: "))
        
        # Dados do carregamento
        carga_opcao = input("Você conhece o momento fletor? (s/n): ").lower()
        if carga_opcao == 's':
            momento = float(input("Momento fletor de cálculo (Md) [kN.m]: "))
        else:
            carga = float(input("Carga distribuída na viga (q) [kN/m]: "))
            momento = calcular_momento_viga_biapoiada(vao, carga)
            print(f"\nMomento fletor calculado (Md): {momento:.2f} kN.m")
        
        # Dados do concreto
        fck_opcao = input("Você conhece o fck do concreto? (s/n): ").lower()
        if fck_opcao == 's':
            fck = float(input("Resistência característica do concreto (fck) [MPa]: "))
        else:
            print("\nValores típicos de fck:")
            print("1 - C20 (20 MPa)")
            print("2 - C25 (25 MPa)")
            print("3 - C30 (30 MPa)")
            print("4 - C35 (35 MPa)")
            print("5 - C40 (40 MPa)")
            fck_escolha = int(input("Escolha a classe do concreto (1-5): "))
            fck_valores = {1: 20, 2: 25, 3: 30, 4: 35, 5: 40}
            fck = fck_valores.get(fck_escolha, 25)
            print(f"Fck adotado: {fck} MPa")
        
        # Dados da armadura
        phi_opcao = input("Você conhece o diâmetro da armadura? (s/n): ").lower()
        if phi_opcao == 's':
            phi = float(input("Diâmetro da armadura (φ) [mm]: "))
        else:
            print("\nDiâmetros típicos para armadura longitudinal:")
            print("1 - 8 mm")
            print("2 - 10 mm")
            print("3 - 12.5 mm")
            print("4 - 16 mm")
            print("5 - 20 mm")
            phi_escolha = int(input("Escolha o diâmetro da armadura (1-5): "))
            phi_valores = {1: 8, 2: 10, 3: 12.5, 4: 16, 5: 20}
            phi = phi_valores.get(phi_escolha, 10)
            print(f"Diâmetro adotado: {phi} mm")
            
        n_barras = int(input("Número de barras na armadura de tração: "))
        area_aco = (math.pi * phi**2 / 4) * n_barras
        print(f"Área de aço calculada (As): {area_aco:.2f} mm²")
        
        # Cálculo da taxa de armadura
        area_concreto = largura * 10 * d * 10  # convertendo cm para mm
        rho = (area_aco / area_concreto) * 100  # em porcentagem
        print(f"Taxa de armadura calculada (ρ): {rho:.3f}%")
        
        # Cálculo da tensão na armadura, caso não tenha sido informada
        tensao_opcao = input("Você conhece a tensão na armadura? (s/n): ").lower()
        if tensao_opcao == 's':
            sigma_s = float(input("Tensão na armadura (σ_s) [MPa]: "))
        else:
            sigma_s = calcular_tensao_armadura(momento, d*10, largura*10, area_aco)
            print(f"Tensão na armadura calculada (σ_s): {sigma_s:.2f} MPa")
        
        # Dados complementares
        alpha = float(input("Fator de aderência (α) [1.0 para barras nervuradas, 0.5 para barras lisas]: ") or "1.0")
        
        c_opcao = input("Você conhece o cobrimento do concreto? (s/n): ").lower()
        if c_opcao == 's':
            c = float(input("Cobrimento do concreto (c) [mm]: "))
        else:
            print("\nClasses de agressividade ambiental:")
            print("1 - Classe I - Rural ou Urbano Seco (cobrimento 25mm)")
            print("2 - Classe II - Urbano (cobrimento 30mm)")
            print("3 - Classe III - Marinho/Industrial (cobrimento 40mm)")
            print("4 - Classe IV - Industrial/Respingos de Maré (cobrimento 50mm)")
            classe_agressividade = int(input("Escolha a classe de agressividade (1-4): "))
            c_valores = {1: 25, 2: 30, 3: 40, 4: 50}
            c = c_valores.get(classe_agressividade, 30)
            print(f"Cobrimento adotado: {c} mm")
        
        # Abertura máxima de fissura permitida
        w_perm_opcao = input("Você conhece a abertura máxima de fissura permitida? (s/n): ").lower()
        if w_perm_opcao == 's':
            w_perm = float(input("Abertura máxima de fissura permitida (w_perm) [mm]: "))
        else:
            print("\nClasses de agressividade ambiental (para w_perm):")
            print("1 - Classe I - Rural/Urbano Seco (w_perm = 0.4mm)")
            print("2 - Classe II - Urbano (w_perm = 0.3mm)")
            print("3 - Classe III - Marinho/Industrial (w_perm = 0.2mm)")
            print("4 - Classe IV - Industrial/Respingos de Maré (w_perm = 0.1mm)")
            classe_w = int(input("Escolha a classe de agressividade (1-4): "))
            w_perm = obter_w_perm(classe_w)
            print(f"Abertura máxima adotada: {w_perm} mm")
            
    except ValueError as e:
        print(f"\nErro: {e}")
        print("Por favor, insira apenas valores numéricos.")
        return
    
    # Criando a estrutura dos dados
    dados = {
        "Parâmetro": [
            "Vão da viga (L)",
            "Altura da viga (h)",
            "Largura da viga (b)",
            "Altura útil (d)",
            "Momento fletor (Md)",
            "Resistência característica do concreto (fck)",
            "Diâmetro da armadura (φ)",
            "Número de barras",
            "Área de aço (As)",
            "Taxa de armadura (ρ)",
            "Tensão na armadura (σ_s)",
            "Fator de aderência (α)",
            "Cobrimento do concreto (c)",
            "Abertura máxima permitida (w_perm)"
        ],
        "Unidade": ["m", "cm", "cm", "cm", "kN.m", "MPa", "mm", "-", "mm²", "%", "MPa", "-", "mm", "mm"],
        "Valor": [vao, altura, largura, d, momento, fck, phi, n_barras, area_aco, rho, sigma_s, alpha, c, w_perm]
    }
    
    # Criando DataFrame para os parâmetros de entrada
    df_entrada = pd.DataFrame(dados)
    
    # Convertendo rho de % para decimal para os cálculos
    rho_decimal = rho / 100
    
    # Cálculo de fctm
    fctm = 0.30 * (fck ** (2/3))
    
    # Cálculo do espaçamento das fissuras (s_r_max)
    s_r_max = 3.4 * c + 0.425 * (alpha * 0.5 * phi / rho_decimal)
    
    # Cálculo da abertura de fissura (w_k)
    E_s = 210000  # MPa, módulo de elasticidade do aço
    beta = 0.6
    eps_diff = (sigma_s - beta * (fctm / rho_decimal)) / E_s if sigma_s > beta * (fctm / rho_decimal) else 0
    w_k = s_r_max * eps_diff if sigma_s > fctm / rho_decimal else 0
    
    # Criando DataFrame para os resultados calculados
    df_resultado = pd.DataFrame({
        "Parâmetro": ["Resistência média à tração do concreto (fctm)", 
                     "Espaçamento médio das fissuras (s_r_max)", 
                     "Abertura estimada da fissura (w_k)"],
        "Unidade": ["MPa", "mm", "mm"],
        "Valor Calculado": [round(fctm, 2), round(s_r_max, 2), round(w_k, 3)]
    })
    
    # Verificação do limite de fissuração
    verificacao = "OK" if w_k <= w_perm else "Excedido"
    
    # Criando um DataFrame para a verificação
    df_verificacao = pd.DataFrame({
        "Verificação": ["Abertura de fissura dentro do limite?"],
        "Resultado": [verificacao],
        "Observação": [f"w_k = {w_k:.3f} mm, w_perm = {w_perm} mm"]
    })
    
    # Exibindo os resultados
    print("\n----- RESULTADOS DA VERIFICAÇÃO -----")
    print("\nParâmetros calculados:")
    print(df_resultado.to_string(index=False))
    
    print("\nVerificação de fissuração:")
    print(df_verificacao.to_string(index=False))
    
    # Saída detalhada da verificação
    if verificacao == "OK":
        print(f"\nVERIFICAÇÃO PASSOU: A abertura de fissura calculada ({w_k:.3f} mm) é menor ou igual ao valor máximo permitido ({w_perm} mm).")
    else:
        print(f"\nVERIFICAÇÃO FALHOU: A abertura de fissura calculada ({w_k:.3f} mm) excede o valor máximo permitido ({w_perm} mm).")
    
    # Perguntar se deseja salvar os resultados em um arquivo Excel
    salvar = input("\nDeseja salvar os resultados em um arquivo Excel? (s/n): ").lower()
    if salvar == 's':
        try:
            # Cria um nome de arquivo com data e hora
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"Fissuracao_Viga_Biapoiada_{data_hora}.xlsx"
            
            with pd.ExcelWriter(file_path) as writer:
                df_entrada.to_excel(writer, sheet_name="Entradas", index=False)
                df_resultado.to_excel(writer, sheet_name="Resultados", index=False)
                df_verificacao.to_excel(writer, sheet_name="Verificação", index=False)
            
            print(f"\nResultados salvos em: {os.path.abspath(file_path)}")
        except Exception as e:
            print(f"\nErro ao salvar o arquivo: {e}")
            print("Verifique se você tem permissão para escrever no diretório atual ou se o arquivo não está em uso.")

# Executar a função
if __name__ == "__main__":
    verificar_fissuracao()