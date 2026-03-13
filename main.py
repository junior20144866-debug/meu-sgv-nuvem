import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. TRADUÇÃO ---
texts = {"Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "config": "Configurações"}}
if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# --- 3. FUNÇÕES ---
def formato_br(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def importar_para_banco(df, destino):
    # Sinônimos atualizados conforme seus arquivos reais
    ref = {
        "produtos": {"ean13": "CODIGO", "descricao": "DESCRICAO", "preco_venda": "P_VENDA", "unidade": "UNIDADE"},
        "Clientes": {"nome_completo": "NOM", "cpf_cnpj": "CGC", "telefone": "TEL1", "cidade": "CID"}
    }[destino]
    
    sucesso = 0
    progresso = st.progress(0)
    total = len(df)
    
    for i, row in df.iterrows():
        dados = {}
        for campo_bd, coluna_excel in ref.items():
            if coluna_excel in df.columns:
                val = row[coluna_excel]
                dados[campo_bd] = str(val) if pd.notnull(val) else None
        
        if dados:
            try:
                supabase.table(destino).insert(dados).execute()
                sucesso += 1
            except: pass
        progresso.progress((i + 1) / total)
    return sucesso

# --- 4. FLUXO DE ACESSO ---
if not st.session_state.get("autenticado"):
    st.title("🔒 Login")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Acessar"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- PÁGINA ESTOQUE ---
    if menu == f"📦 {T['estoque']}":
        st.header("📦 Gestão de Estoque")
        with st.expander("➕ Novo Produto (Manual)"):
            with st.form("f_prod", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                desc = c1.text_input("Descrição")
                ean = c2.text_input("Código/EAN")
                prc = c3.number_input("Preço", min_value=0.0)
                if st.form_submit_button("Salvar"):
                    supabase.table("produtos").insert({"descricao": desc, "ean13": ean, "preco_venda": prc}).execute()
                    st.success("Salvo!"); time.sleep(1); st.rerun()
        
        dados = supabase.table("produtos").select("*").order("descricao").execute().data
        if dados:
            df_p = pd.DataFrame(dados)
            df_p['Preço'] = df_p['preco_venda'].apply(formato_br)
            st.dataframe(df_p[['ean13', 'descricao', 'Preço']], use_container_width=True)

    # --- PÁGINA CLIENTES ---
    elif menu == f"👥 {T['clientes']}":
        st.header("👥 Gestão de Clientes")
        with st.expander("➕ Novo Cliente (Manual)"):
            with st.form("f_cli", clear_on_submit=True):
                n = st.text_input("Nome Completo")
                doc = st.text_input("CPF/CNPJ")
                if st.form_submit_button("Cadastrar"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": doc}).execute()
                    st.success("Cadastrado!"); time.sleep(1); st.rerun()
        
        clis = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        if clis: st.dataframe(pd.DataFrame(clis), use_container_width=True)

    # --- PÁGINA IMPORTAÇÃO ---
    elif menu == f"📑 {T['import']}":
        st.header("📑 Importação de Planilhas")
        dest = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
        if arq:
            df_excel = pd.read_excel(arq, engine='openpyxl')
            st.write(f"Arquivo lido: {len(df_excel)} linhas encontradas.")
            if st.button("🚀 Iniciar Importação"):
                qtd = importar_para_banco(df_excel, dest)
                st.success(f"✅ {qtd} registros importados para {dest}!"); st.balloons()

    # --- PÁGINA CONFIG (CONTROLE TOTAL) ---
    elif menu == f"⚙️ {T['config']}":
        st.header("⚙️ Configurações e Controle")
        st.subheader("🗑️ Limpeza de Dados")
        tab = st.selectbox("Zerar tabela:", ["---", "produtos", "Clientes"])
        if tab != "---" and st.button(f"Zerar {tab}"):
            supabase.table(tab).delete().neq("id", -1).execute()
            st.success("Tabela zerada!"); time.sleep(1); st.rerun()
        
        if st.button("🚪 Sair"):
            st.session_state.autenticado = False; st.rerun()
