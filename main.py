import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# 1. CONEXÃO E DICIONÁRIO MULTI-IDIOMA
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "config": "Configurações", "import": "Importar", "idioma": "Idioma"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "config": "Settings", "import": "Import Data", "idioma": "Language"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "config": "Ajustes", "import": "Importar", "idioma": "Idioma"}
}

if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# 2. FUNÇÕES DE APOIO E BLINDAGEM
def safe_list(res): return res.data if res.data else []

# --- INTERFACE ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

with st.sidebar:
    st.title("JMQJR Evolution")
    st.session_state.lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()))
    menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

if not st.session_state.get("autenticado"):
    st.title("🔒 Login")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Acessar"):
        st.session_state.autenticado = True; st.rerun()
else:
    # --- ABA CLIENTES (EDIÇÃO COMPLETA) ---
    if menu == f"👥 {T['clientes']}":
        st.header(f"👥 {T['clientes']}")
        t1, t2 = st.tabs(["📋 Lista/Editar", "➕ Novo"])
        
        with t2:
            with st.form("cli_new"):
                c1, c2 = st.columns(2)
                n = c1.text_input("Nome")
                d = c2.text_input("CPF/CNPJ")
                cp = c1.text_input("CEP")
                ru = c2.text_input("Endereço/Rua")
                ba = c1.text_input("Bairro")
                ci = c2.text_input("Cidade")
                uf = c1.selectbox("UF", ["CE", "SP", "RJ", "MG", "PE", "Outros"])
                te = c2.text_input("Telefone")
                if st.form_submit_button("Salvar"):
                    supabase.table("Clientes").insert({"nome_completo":n,"cpf_cnpj":d,"endereco":ru,"bairro":ba,"cep":cp,"cidade":ci,"uf":uf,"telefone":te}).execute()
                    st.success("Cadastrado!"); st.rerun()

        with t1:
            res = safe_list(supabase.table("Clientes").select("*").execute())
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                with st.expander("✏️ Alterar Dados do Cliente"):
                    cli_id = st.selectbox("Selecione o cliente", df['id'], format_func=lambda x: df[df['id']==x]['nome_completo'].values[0])
                    curr = df[df['id']==cli_id].iloc[0]
                    new_n = st.text_input("Nome", value=curr['nome_completo'])
                    new_t = st.text_input("Telefone", value=curr['telefone'])
                    if st.button("Confirmar Alteração"):
                        supabase.table("Clientes").update({"nome_completo": new_n, "telefone": new_t}).eq("id", cli_id).execute()
                        st.success("Atualizado!"); st.rerun()
            else: st.info("Sem dados.")

    # --- ABA ESTOQUE (EAN-13 E EDIÇÃO) ---
    elif menu == f"📦 {T['estoque']}":
        st.header(f"📦 {T['estoque']}")
        t1, t2 = st.tabs(["📋 Meus Produtos", "➕ Adicionar"])
        with t2:
            with st.form("prod_new"):
                c1, c2 = st.columns([2, 1])
                ds = c1.text_input("Descrição")
                ea = c2.text_input("EAN-13 (Cód. Barras)")
                pr = c2.number_input("Preço", min_value=0.0)
                if st.form_submit_button("Salvar"):
                    supabase.table("produtos").insert({"descricao":ds,"ean13":ea,"preco_venda":pr,"estoque_atual":0}).execute()
                    st.success("Salvo!"); st.rerun()
        with t1:
            res = safe_list(supabase.table("produtos").select("*").execute())
            if res:
                dfp = pd.DataFrame(res)
                st.dataframe(dfp, use_container_width=True)
                with st.expander("✏️ Editar Preço/EAN"):
                    p_id = st.selectbox("Selecione o produto", dfp['id'], format_func=lambda x: dfp[dfp['id']==x]['descricao'].values[0])
                    p_curr = dfp[dfp['id']==p_id].iloc[0]
                    n_pr = st.number_input("Novo Preço", value=float(p_curr['preco_venda']))
                    n_ea = st.text_input("Novo EAN", value=str(p_curr['ean13'] if p_curr['ean13'] else ""))
                    if st.button("Atualizar Produto"):
                        supabase.table("produtos").update({"preco_venda": n_pr, "ean13": n_ea}).eq("id", p_id).execute()
                        st.success("Produto Atualizado!"); st.rerun()

    # --- ABA CONFIGURAÇÕES (LOGO PERSISTENTE) ---
    elif menu == f"⚙️ {T['config']}":
        st.header(f"⚙️ {T['config']}")
        res_e = safe_list(supabase.table("config_empresa").select("*").eq("id", 1).execute())
        emp_d = res_e[0] if res_e else {}
        
        c1, c2 = st.columns(2)
        with c1:
            with st.form("cfg_e"):
                nome_e = st.text_input("Empresa", value=emp_d.get('nome_empresa',''))
                cnpj_e = st.text_input("CNPJ", value=emp_d.get('cnpj',''))
                # Campo para salvar o LINK da logo
                l_url = st.text_input("URL da Logomarca (Link da imagem)", value=emp_d.get('logo_url',''))
                if st.form_submit_button("Salvar"):
                    supabase.table("config_empresa").upsert({"id":1, "nome_empresa":nome_e, "cnpj":cnpj_e, "logo_url":l_url}).execute()
                    st.success("Configurações salvas!"); st.rerun()
        with c2:
            if emp_d.get('logo_url'):
                st.image(emp_d['logo_url'], width=200)
                st.caption("Visualização da logo salva no banco.")
            else: st.warning("Adicione um link de imagem ao lado para salvar a logo.")
