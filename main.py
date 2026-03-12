import streamlit as st
import pandas as pd

# Função para converter os dados brutos do PDF em uma lista para o Supabase
def processar_importacao_pdf():
    # Dados extraídos do seu PDF (Derlyana Alimentos)
    dados_pdf = [
        {"descricao": "CAJUÍNA 200 ML (24 UN)", "unidade": "CX", "preco_venda": 60.00, "estoque_atual": 30.0, "ean13": "00027"},
        {"descricao": "CAJUINA 480 ML (12 UN)", "unidade": "PC", "preco_venda": 55.00, "estoque_atual": 0.0, "ean13": "00028"},
        {"descricao": "POLPA DE ABACAXI", "unidade": "KG", "preco_venda": 14.00, "estoque_atual": 11.0, "ean13": "00001"},
        {"descricao": "POLPA DE CAJU", "unidade": "KG", "preco_venda": 9.50, "estoque_atual": 20.0, "ean13": "00003"},
        {"descricao": "POLPA DE CAJÁ", "unidade": "KG", "preco_venda": 15.00, "estoque_atual": 20.0, "ean13": "00004"},
        {"descricao": "POLPA DE GRAVIOLA", "unidade": "KG", "preco_venda": 15.00, "estoque_atual": 8.0, "ean13": "00006"}
    ]
    
    for item in dados_pdf:
        # Insere ou atualiza no Supabase
        supabase.table("produtos").upsert(item).execute()
    st.success("✅ Produtos do PDF importados com sucesso!")

# --- DENTRO DO MENU 'IMPORTAR' ---
if menu == f"📑 {T['import']}":
    st.header("📑 Importação de Dados")
    
    st.subheader("1. Importar Tabela 'Derlyana Alimentos'")
    if st.button("🚀 Processar Dados do PDF Enviado"):
        processar_importacao_pdf()
        st.rerun()
    
    st.divider()
    
    st.subheader("2. Importação Manual via Planilha")
    file = st.file_uploader("Suba um CSV com colunas: descricao, unidade, preco_venda, ean13", type=['csv'])
    if file:
        df_csv = pd.read_csv(file)
        st.write("Prévia para conferência:", df_csv.head())
        if st.button("Confirmar Importação em Massa"):
            for _, row in df_csv.iterrows():
                supabase.table("produtos").upsert(row.to_dict()).execute()
            st.success("Importação concluída!")

# --- DENTRO DO MENU 'ESTOQUE' (PARA ALTERAR) ---
elif menu == f"📦 {T['estoque']}":
    # ... (código anterior de listagem)
    res = safe_query("produtos")
    if res:
        dfp = pd.DataFrame(res)
        st.subheader("✏️ Alterar Produto Existente")
        prod_sel = st.selectbox("Selecione o produto para editar", dfp['descricao'])
        
        # Filtra os dados do produto selecionado
        dados_p = dfp[dfp['descricao'] == prod_sel].iloc[0]
        
        with st.form("edit_prod"):
            nova_desc = st.text_input("Descrição", value=dados_p['descricao'])
            novo_vlr = st.number_input("Valor de Venda", value=float(dados_p['preco_venda']))
            novo_est = st.number_input("Estoque Atual", value=float(dados_p['estoque_atual']))
            novo_ean = st.text_input("Código EAN-13", value=str(dados_p['ean13']))
            
            if st.form_submit_button("Atualizar Dados"):
                supabase.table("produtos").update({
                    "descricao": nova_desc,
                    "preco_venda": novo_vlr,
                    "estoque_atual": novo_est,
                    "ean13": novo_ean
                }).eq("id", dados_p['id']).execute()
                st.success("Produto alterado!")
                st.rerun()
