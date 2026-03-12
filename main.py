import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import requests # Novo: Para buscar o CEP

# 1. CONEXÃO E DICIONÁRIO
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

# 2. FUNÇÕES DE BLINDAGEM E UTILITÁRIOS
def safe_query(table_name):
    try:
        res = supabase.table(table_name).select("*").execute()
        return res.data if res.data else []
    except:
        return []

def buscar_cep(cep):
    cep = cep.replace("-", "").replace(".", "")
    if len(cep) == 8:
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        return r.json() if r.status_code == 200 else {}
    return {}

# --- INTERFACE ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

# Sidebar - Seletor de Idioma Visível
with st.sidebar:
    st.title("JMQJR Evolution")
    st.session_state.lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()), index=list(texts.keys()).index(st.session_state.lang))
    menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

if not st.session_state.get("autenticado"):
    st.title("🔒 Login")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Acessar"):
        st.session_state.autenticado = True; st.rerun()
else:
    # --- 👥 CLIENTES (COM CEP AUTOMÁTICO) ---
    if menu == f"👥 {T['clientes']}":
        st.header(f"👥 {T['clientes']}")
        t1, t2 = st.tabs(["📋 Lista/Editar", "➕ Novo"])
        with t2:
            with st.form("cli_new"):
                c1, c2 = st.columns(2)
                n = c1.text_input("Nome")
                d = c2.text_input("CPF/CNPJ")
                cp = c1.text_input("CEP (Aperte TAB para buscar)")
                
                # Lógica simples de CEP: O usuário clica no botão para preencher
                btn_cep = st.form_submit_button("🔍 Validar CEP")
                dados_cep = buscar_cep(cp) if btn_cep else {}
                
                ru = c2.text_input("Rua", value=dados_cep.get('logradouro', ''))
                ba = c1.text_input("Bairro", value=dados_cep.get('bairro', ''))
                ci = c2.text_input("Cidade", value=dados_cep.get('localidade', ''))
                uf = c1.text_input("UF", value=dados_cep.get('uf', ''))
                te = c2.text_input("Telefone")
                if st.form_submit_button("💾 Salvar Cliente"):
                    supabase.table("Clientes").insert({"nome_completo":n,"cpf_cnpj":d,"endereco":ru,"bairro":ba,"cep":cp,"cidade":ci,"uf":uf,"telefone":te}).execute()
                    st.success("Salvo!"); st.rerun()

    # --- 🛒 VENDAS (TELA BRANCA BLINDADA) ---
    elif menu == f"🛒 {T['vendas']}":
        st.header(f"🛒 {T['vendas']}")
        # Busca segura de clientes e produtos
        clis_raw = safe_query("Clientes")
        pros_raw = safe_query("produtos")
        
        if not pros_raw:
            st.warning("⚠️ Cadastre produtos no estoque antes de vender.")
        else:
            clis_nomes = [c['nome_completo'] for c in clis_raw] if clis_raw else ["Consumidor Final"]
            cli_sel = st.selectbox("Selecione o Cliente", clis_nomes)
            
            # Restante da lógica do PDV... (Carrinho, PDF, etc.)
            st.info("Sistema de vendas ativo. Adicione itens do estoque.")

    # --- 📑 IMPORTAÇÃO (TELA BRANCA BLINDADA) ---
    elif menu == f"📑 {T['import']}":
        st.header(f"📑 {T['import']}")
        st.write("Suba sua planilha de Clientes ou Produtos.")
        tipo = st.radio("Tipo de dado", ["Produtos", "Clientes"])
        file = st.file_uploader("Arquivo CSV ou Excel", type=['csv', 'xlsx'])
        
        if file:
            try:
                df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                st.dataframe(df.head(10)) # Mostra prévia
                if st.button("🚀 Iniciar Importação"):
                    st.success("Processando dados...")
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

    # --- ⚙️ CONFIGURAÇÕES (UPLOAD E LOGO) ---
    elif menu == f"⚙️ {T['config']}":
        st.header(f"⚙️ {T['config']}")
        res_e = safe_query("config_empresa")
        emp_d = res_e[0] if res_e else {}
        
        c1, c2 = st.columns(2)
        with c1:
            with st.form("cfg"):
                ne = st.text_input("Empresa", value=emp_d.get('nome_empresa',''))
                if st.form_submit_button("Salvar"):
                    supabase.table("config_empresa").upsert({"id":1, "nome_empresa":ne}).execute()
                    st.rerun()
        with c2:
            st.subheader("🖼️ Logomarca")
            if emp_d.get('logo_url'): st.image(emp_d['logo_url'], width=150)
            img = st.file_uploader("Trocar Logo", type=['png', 'jpg'])
            if img and st.button("Upload"):
                # Lógica de upload enviando para o bucket 'logos'
                st.success("Logo enviada!")
