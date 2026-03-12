import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import requests

# 1. CONEXÃO E CONFIGURAÇÕES
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Sistema de Tradução
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "config": "Configurações", "import": "Importar", "idioma": "Idioma"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "config": "Settings", "import": "Import Data", "idioma": "Language"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "config": "Ajustes", "import": "Importar", "idioma": "Idioma"}
}

if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# 2. PRODUTOS EXTRAÍDOS DO PDF (LISTA COMPLETA)
PRODUTOS_PDF = [
    {"ean13": "00027", "descricao": "CAJUÍNA 200 ML (24 UN)", "unidade": "CX", "preco_venda": 60.00, "estoque_atual": 30.0},
    {"ean13": "00028", "descricao": "CAJUINA 480 ML (12 UN)", "unidade": "PC", "preco_venda": 55.00, "estoque_atual": 0.0},
    {"ean13": "00025", "descricao": "POLPA ABACAXI C/HORTELA (500G)", "unidade": "PC", "preco_venda": 8.00, "estoque_atual": 0.0},
    {"ean13": "00001", "descricao": "POLPA DE ABACAXI (KG)", "unidade": "KG", "preco_venda": 14.00, "estoque_atual": 11.0},
    {"ean13": "00009", "descricao": "POLPA DE ABACAXI (500G)", "unidade": "PC", "preco_venda": 7.00, "estoque_atual": 0.0},
    {"ean13": "00002", "descricao": "POLPA DE ACEROLA (KG)", "unidade": "KG", "preco_venda": 12.00, "estoque_atual": 19.0},
    {"ean13": "00010", "descricao": "POLPA DE ACEROLA (500G)", "unidade": "PC", "preco_venda": 6.00, "estoque_atual": 0.0},
    {"ean13": "00011", "descricao": "POLPA DE AMEIXA (500G)", "unidade": "PC", "preco_venda": 7.50, "estoque_atual": 0.0},
    {"ean13": "00012", "descricao": "POLPA DE AÇAÍ (500G)", "unidade": "PC", "preco_venda": 10.90, "estoque_atual": 0.0},
    {"ean13": "00003", "descricao": "POLPA DE CAJU (KG)", "unidade": "KG", "preco_venda": 9.50, "estoque_atual": 20.0},
    {"ean13": "00014", "descricao": "POLPA DE CAJU (500G)", "unidade": "PC", "preco_venda": 4.75, "estoque_atual": 0.0},
    {"ean13": "00004", "descricao": "POLPA DE CAJÁ (KG)", "unidade": "KG", "preco_venda": 15.00, "estoque_atual": 20.0},
    {"ean13": "00013", "descricao": "POLPA DE CAJÁ (500G)", "unidade": "PC", "preco_venda": 7.50, "estoque_atual": 0.0},
    {"ean13": "00015", "descricao": "POLPA DE CUPUAÇU (500G)", "unidade": "PC", "preco_venda": 8.00, "estoque_atual": 0.0},
    {"ean13": "00005", "descricao": "POLPA DE GOIABA (KG)", "unidade": "KG", "preco_venda": 12.00, "estoque_atual": 16.0},
    {"ean13": "00016", "descricao": "POLPA DE GOIABA (500G)", "unidade": "PC", "preco_venda": 6.00, "estoque_atual": 0.0},
    {"ean13": "00006", "descricao": "POLPA DE GRAVIOLA (KG)", "unidade": "KG", "preco_venda": 15.00, "estoque_atual": 8.0},
    {"ean13": "00017", "descricao": "POLPA DE GRAVIOLA (500G)", "unidade": "PC", "preco_venda": 7.50, "estoque_atual": 0.0},
    {"ean13": "00007", "descricao": "POLPA DE MANGA (KG)", "unidade": "KG", "preco_venda": 11.00, "estoque_atual": 15.0},
    {"ean13": "00018", "descricao": "POLPA DE MANGA (500G)", "unidade": "PC", "preco_venda": 5.50, "estoque_atual": 0.0},
    {"ean13": "00008", "descricao": "POLPA DE MARACUJÁ (KG)", "unidade": "KG", "preco_venda": 22.00, "estoque_atual": 2.0},
    {"ean13": "00019", "descricao": "POLPA DE MARACUJÁ (500G)", "unidade": "PC", "preco_venda": 11.00, "estoque_atual": 0.0},
    {"ean13": "00021", "descricao": "POLPA DE MORANGO (500G)", "unidade": "PC", "preco_venda": 8.50, "estoque_atual": 0.0},
    {"ean13": "00020", "descricao": "POLPA DE TAMARINDO (500G)", "unidade": "PC", "preco_venda": 6.50, "estoque_atual": 0.0},
    {"ean13": "00022", "descricao": "POLPA DE UMBU (500G)", "unidade": "PC", "preco_venda": 6.50, "estoque_atual": 0.0}
]

# 3. FUNÇÕES DE SUPORTE
def safe_query(table):
    try: return supabase.table(table).select("*").execute().data or []
    except: return []

def buscar_cep(cep):
    cep = cep.replace("-", "").replace(".", "")
    if len(cep) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            return r.json() if r.status_code == 200 else {}
        except: return {}
    return {}

# --- INTERFACE PRINCIPAL ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("🔒 Acesso ao Sistema")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True; st.rerun()
else:
    with st.sidebar:
        st.title("JMQJR Evolution")
        st.session_state.lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()))
        menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ABA IMPORTAR (COM DADOS DO PDF) ---
    if menu == f"📑 {T['import']}":
        st.header(f"📑 {T['import']}")
        st.info("Clique abaixo para carregar todos os produtos da Derlyana Alimentos automaticamente.")
        
        with st.expander("🔍 Ver produtos mapeados do PDF"):
            st.table(pd.DataFrame(PRODUTOS_PDF))
            
        if st.button("🚀 EXECUTAR IMPORTAÇÃO COMPLETA"):
            with st.spinner("Processando..."):
                for prod in PRODUTOS_PDF:
                    supabase.table("produtos").upsert(prod).execute()
            st.success("✅ Todos os produtos foram importados/atualizados!")
            st.balloons()

    # --- ABA ESTOQUE (EDIÇÃO TOTAL) ---
    elif menu == f"📦 {T['estoque']}":
        st.header(f"📦 {T['estoque']}")
        prods = safe_query("produtos")
        if prods:
            dfp = pd.DataFrame(prods)
            st.dataframe(dfp, use_container_width=True)
            
            with st.expander("✏️ Editar ou 🗑️ Excluir Produto"):
                sel = st.selectbox("Selecione o produto", dfp['descricao'])
                item = dfp[dfp['descricao'] == sel].iloc[0]
                col1, col2 = st.columns(2)
                n_vlr = col1.number_input("Novo Preço", value=float(item['preco_venda']))
                n_est = col2.number_input("Estoque Atual", value=float(item['estoque_atual'] or 0))
                
                if st.button("💾 Salvar Alterações"):
                    supabase.table("produtos").update({"preco_venda": n_vlr, "estoque_atual": n_est}).eq("id", item['id']).execute()
                    st.success("Atualizado!"); st.rerun()
                
                if st.button("🗑️ EXCLUIR DEFINITIVAMENTE"):
                    supabase.table("produtos").delete().eq("id", item['id']).execute()
                    st.rerun()
        else: st.warning("Estoque vazio. Vá em Importar.")

    # --- ABA CLIENTES (BUSCA CEP AUTOMÁTICA) ---
    elif menu == f"👥 {T['clientes']}":
        st.header(f"👥 {T['clientes']}")
        t1, t2 = st.tabs(["Lista", "Novo Cadastro"])
        with t2:
            with st.form("cli_f"):
                c1, c2 = st.columns(2)
                nome = c1.text_input("Nome")
                doc = c2.text_input("CPF/CNPJ")
                cep_input = c1.text_input("CEP")
                
                # O preenchimento automático acontece via botão de validação
                if st.form_submit_button("🔍 Validar CEP"):
                    dados = buscar_cep(cep_input)
                    st.session_state.cep_data = dados
                
                cep_d = st.session_state.get('cep_data', {})
                rua = c2.text_input("Endereço", value=cep_d.get('logradouro', ''))
                bairro = c1.text_input("Bairro", value=cep_d.get('bairro', ''))
                cidade = c2.text_input("Cidade", value=cep_d.get('localidade', ''))
                uf = c1.text_input("UF", value=cep_d.get('uf', ''))
                
                if st.form_submit_button("💾 Salvar Cliente"):
                    supabase.table("Clientes").insert({
                        "nome_completo": nome, "cpf_cnpj": doc, "cep": cep_input,
                        "endereco": rua, "bairro": bairro, "cidade": cidade, "uf": uf
                    }).execute()
                    st.success("Cliente cadastrado!")

    # --- ABA CONFIGURAÇÕES (LOGO PERSISTENTE) ---
    elif menu == f"⚙️ {T['config']}":
        st.header(f"⚙️ {T['config']}")
        res = safe_query("config_empresa")
        emp = res[0] if res else {}
        
        with st.form("cfg"):
            n_emp = st.text_input("Nome da Empresa", value=emp.get('nome_empresa', ''))
            l_url = st.text_input("URL da Logo (ou use o upload abaixo)", value=emp.get('logo_url', ''))
            if st.form_submit_button("Salvar"):
                supabase.table("config_empresa").upsert({"id": 1, "nome_empresa": n_emp, "logo_url": l_url}).execute()
                st.rerun()

    # --- ABA VENDAS (SIMPLIFICADA PARA TESTE) ---
    elif menu == f"🛒 {T['vendas']}":
        st.header(f"🛒 {T['vendas']}")
        st.info("Selecione os produtos importados para iniciar o pedido.")
        # Lógica de PDV aqui...
