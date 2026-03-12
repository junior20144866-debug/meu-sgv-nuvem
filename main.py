import streamlit as st
from supabase import create_client
import pandas as pd
import time

# 1. CONEXÃO
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. FUNÇÃO DE FORMATAÇÃO BRASILEIRA (1.234,56)
def formato_br(valor):
    if valor is None: return "0,00"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 3. FUNÇÃO DE IMPORTAÇÃO EM MASSA
def importar_dados_massa(df, tabela):
    total = len(df)
    progresso = st.progress(0)
    for i, row in df.iterrows():
        dados = row.to_dict()
        # O .upsert usa a coluna unique (ean13) para não duplicar
        supabase.table(tabela).upsert(dados).execute()
        progresso.progress((i + 1) / total)
    return total

# --- INTERFACE ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

menu = st.sidebar.radio("Navegação", ["🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importar Dados"])

# --- ABA IMPORTAR (SUBSTITUI O PDF) ---
if menu == "📑 Importar Dados":
    st.header("📑 Importação Profissional")
    tipo = st.selectbox("Destino dos dados", ["produtos", "Clientes"])
    
    st.info(f"Suba um arquivo Excel ou CSV. As colunas devem ser idênticas às do banco: " + 
            ("ean13, descricao, preco_venda, unidade" if tipo == "produtos" else "nome_completo, cpf_cnpj, telefone"))
    
    arquivo = st.file_uploader("Selecionar Planilha", type=["xlsx", "csv"])
    if arquivo:
        df = pd.read_excel(arquivo) if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
        st.dataframe(df.head())
        if st.button("🚀 Iniciar Processamento"):
            qtd = importar_dados_massa(df, tipo)
            st.success(f"✅ {qtd} registros processados com sucesso!")
            st.balloons()

# --- ABA ESTOQUE (COM FORMATAÇÃO BR) ---
elif menu == "📦 Estoque":
    st.header("📦 Gestão de Estoque")
    
    # Formulário que limpa ao salvar (UX melhorada)
    with st.form("novo_prod", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        desc = c1.text_input("Descrição")
        ean = c2.text_input("EAN-13")
        preco = c3.number_input("Preço", min_value=0.0, step=0.01)
        if st.form_submit_button("💾 Salvar"):
            if desc and ean:
                supabase.table("produtos").upsert({"descricao": desc, "ean13": ean, "preco_venda": preco}).execute()
                st.success("Salvo!")
                time.sleep(1)
                st.rerun()

    # Visualização com números brasileiros
    res = supabase.table("produtos").select("*").execute().data
    if res:
        df_exibir = pd.DataFrame(res)
        # Aplicando a formatação na visualização
        df_exibir['Preço (R$)'] = df_exibir['preco_venda'].apply(formato_br)
        st.dataframe(df_exibir[['ean13', 'descricao', 'Preço (R$)']], use_container_width=True)
