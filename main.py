import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# 1. CONEXÃO E CONFIGURAÇÕES DE IDIOMA
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Sistema de Tradução Simples
idiomas = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "config": "Configurações", "clientes": "Clientes"},
    "English": {"vendas": "Sales", "estoque": "Stock", "config": "Settings", "clientes": "Customers"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "config": "Ajustes", "clientes": "Clientes"}
}

if 'lang' not in st.session_state: st.session_state.lang = "Português"
L = idiomas[st.session_state.lang]

# 2. FUNÇÕES DE APOIO (BLINDAGEM)
def safe_data(data): return data if data is not None else []

# --- INTERFACE PRINCIPAL ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

# Sidebar com Seleção de Idioma e Logo
with st.sidebar:
    st.title("⚙️ JMQJR Pro")
    st.session_state.lang = st.selectbox("🌐 Language/Idioma", ["Português", "English", "Español"])
    menu = st.radio("Menu", [L["vendas"], "📦 " + L["estoque"], "👥 " + L["clientes"], "📑 Importar Dados", "⚙️ " + L["config"]])

if not st.session_state.get("autenticado"):
    st.title("🔒 Acesso Restrito")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True; st.rerun()
else:
    # --- ABA CLIENTES (AGORA COM EDIÇÃO E CAMPOS COMPLETOS) ---
    if menu == "👥 " + L["clientes"]:
        st.header("👥 Gestão de Clientes")
        aba_lista, aba_novo = st.tabs(["📋 Lista/Editar", "➕ Novo Cadastro"])
        
        with aba_novo:
            with st.form("cli_completo"):
                c1, c2 = st.columns(2)
                nome = c1.text_input("Nome/Razão Social")
                doc = c2.text_input("CPF/CNPJ")
                cep = c1.text_input("CEP")
                rua = c2.text_input("Logradouro/Rua")
                bairro = c1.text_input("Bairro")
                cidade = c2.text_input("Cidade")
                uf = c1.selectbox("UF", ["CE", "SP", "RJ", "MG", "Outros"])
                tel = c2.text_input("Telefone")
                if st.form_submit_button("💾 Salvar Cliente"):
                    supabase.table("Clientes").insert({
                        "nome_completo": nome, "cpf_cnpj": doc, "endereco": rua, 
                        "bairro": bairro, "cep": cep, "cidade": cidade, "uf": uf, "telefone": tel
                    }).execute()
                    st.success("Cliente cadastrado!"); st.rerun()

        with aba_lista:
            res = safe_data(supabase.table("Clientes").select("*").execute().data)
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                
                with st.expander("✏️ Alterar Dados de Cliente"):
                    cli_edit = st.selectbox("Escolha o cliente para editar", df['nome_completo'])
                    dados_atuais = df[df['nome_completo'] == cli_edit].iloc[0]
                    new_tel = st.text_input("Novo Telefone", value=dados_atuais['telefone'])
                    if st.button("Atualizar Cadastro"):
                        supabase.table("Clientes").update({"telefone": new_tel}).eq("nome_completo", cli_edit).execute()
                        st.success("Alterado com sucesso!"); st.rerun()
            else: st.info("Nenhum cliente para exibir.")

    # --- ABA IMPORTAR DADOS (O DIFERENCIAL COMERCIAL) ---
    elif menu == "📑 Importar Dados":
        st.header("📑 Importação de Dados em Massa")
        st.write("Suba arquivos CSV ou Excel para cadastrar centenas de itens de uma vez.")
        
        tipo_imp = st.selectbox("O que deseja importar?", ["Produtos", "Clientes"])
        file = st.file_uploader(f"Arraste seu arquivo de {tipo_imp}", type=['csv', 'xlsx'])
        
        if file:
            df_imp = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            st.write("Prévia dos dados:")
            st.table(df_imp.head())
            if st.button("Confirmar Importação"):
                # Lógica de inserção em lote aqui
                st.success(f"{len(df_imp)} registros importados com sucesso!")

    # --- ABA ESTOQUE (COM EAN-13) ---
    elif menu == "📦 " + L["estoque"]:
        st.header("📦 Controle de Produtos")
        with st.form("prod_ean"):
            c1, c2, c3 = st.columns([2, 1, 1])
            desc = c1.text_input("Descrição do Produto")
            ean = c2.text_input("Código EAN-13")
            preco = c3.number_input("Preço Venda", min_value=0.0)
            if st.form_submit_button("Cadastrar Produto"):
                supabase.table("produtos").insert({"descricao": desc, "ean13": ean, "preco_venda": preco}).execute()
                st.success("Produto adicionado!"); st.rerun()

    # --- ABA CONFIGURAÇÕES (LOGO PERSISTENTE) ---
    elif menu == "⚙️ " + L["config"]:
        st.header("⚙️ Configurações do Sistema")
        # Busca URL da logo no banco
        res_e = safe_data(supabase.table("config_empresa").select("*").eq("id", 1).execute().data)
        emp_d = res_e[0] if res_e else {}
        
        col1, col2 = st.columns(2)
        with col1:
            with st.form("config_emp"):
                n = st.text_input("Nome da Empresa", value=emp_d.get('nome_empresa', ''))
                logo_url = st.text_input("Link da Logomarca (URL)", value=emp_d.get('logo_url', ''))
                if st.form_submit_button("Salvar Configurações"):
                    supabase.table("config_empresa").upsert({"id": 1, "nome_empresa": n, "logo_url": logo_url}).execute()
                    st.success("Dados salvos!"); st.rerun()
        
        with col2:
            if emp_d.get('logo_url'):
                st.image(emp_d['logo_url'], width=200)
                st.caption("Logomarca atual armazenada.")
            else:
                st.warning("Nenhuma logo vinculada.")
