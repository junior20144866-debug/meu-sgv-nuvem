import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import io

# 1. CONEXÃO E IDIOMAS
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

# 2. FUNÇÕES DE APOIO (A BLINDAGEM)
def safe_query(query_func):
    """Executa a query e retorna lista vazia se falhar ou não houver dados."""
    try:
        res = query_func.execute()
        return res.data if res.data else []
    except:
        return []

# --- INTERFACE ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("🔒 Login")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Acessar"):
        st.session_state.autenticado = True; st.rerun()
else:
    with st.sidebar:
        st.title("JMQJR Pro")
        st.session_state.lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()))
        menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ABA CLIENTES (CAMPOS COMPLETOS + EDIÇÃO) ---
    if menu == f"👥 {T['clientes']}":
        st.header(f"👥 {T['clientes']}")
        t1, t2 = st.tabs(["📋 Lista/Editar", "➕ Novo"])
        
        with t2:
            with st.form("cli_new"):
                c1, c2 = st.columns(2)
                n, d = c1.text_input("Nome"), c2.text_input("CPF/CNPJ")
                cp, ru = c1.text_input("CEP"), c2.text_input("Endereço/Rua")
                ba, ci = c1.text_input("Bairro"), c2.text_input("Cidade")
                uf = c1.selectbox("UF", ["CE", "SP", "RJ", "MG", "PE", "Outros"])
                te = c2.text_input("Telefone")
                if st.form_submit_button("Salvar"):
                    supabase.table("Clientes").insert({"nome_completo":n,"cpf_cnpj":d,"endereco":ru,"bairro":ba,"cep":cp,"cidade":ci,"uf":uf,"telefone":te}).execute()
                    st.success("Cadastrado!"); st.rerun()

        with t1:
            res = safe_query(supabase.table("Clientes").select("*"))
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                with st.expander("✏️ Alterar Cadastro"):
                    cli_id = st.selectbox("Cliente", df['id'], format_func=lambda x: df[df['id']==x]['nome_completo'].values[0])
                    curr = df[df['id']==cli_id].iloc[0]
                    col_e1, col_e2 = st.columns(2)
                    up_n = col_e1.text_input("Nome", value=curr['nome_completo'])
                    up_t = col_e2.text_input("Telefone", value=curr['telefone'])
                    if st.button("Confirmar Mudanças"):
                        supabase.table("Clientes").update({"nome_completo": up_n, "telefone": up_t}).eq("id", cli_id).execute()
                        st.success("Atualizado!"); st.rerun()
            else: st.info("Nenhum cliente cadastrado ainda.")

    # --- ABA CONFIGURAÇÕES (UPLOAD AUTOMÁTICO DE LOGO) ---
    elif menu == f"⚙️ {T['config']}":
        st.header(f"⚙️ {T['config']}")
        res_e = safe_query(supabase.table("config_empresa").select("*").eq("id", 1))
        emp_d = res_e[0] if res_e else {}

        c1, c2 = st.columns(2)
        with c1:
            with st.form("cfg_e"):
                nome_e = st.text_input("Empresa", value=emp_d.get('nome_empresa',''))
                cnpj_e = st.text_input("CNPJ", value=emp_d.get('cnpj',''))
                if st.form_submit_button("Salvar Dados"):
                    supabase.table("config_empresa").upsert({"id":1, "nome_empresa":nome_e, "cnpj":cnpj_e}).execute()
                    st.success("Dados salvos!"); st.rerun()
        
        with c2:
            st.subheader("🖼️ Logomarca")
            # Exibe a logo atual se existir
            if emp_d.get('logo_url'):
                st.image(emp_d['logo_url'], width=150)
            
            arquivo_foto = st.file_uploader("Trocar Logomarca", type=['png', 'jpg', 'jpeg'])
            if arquivo_foto and st.button("⬆️ Fazer Upload"):
                # 1. Enviar para o Storage do Supabase
                ext = arquivo_foto.name.split('.')[-1]
                nome_arquivo = f"logo_empresa.{ext}"
                bytes_data = arquivo_foto.getvalue()
                
                # Deleta a antiga se existir para não acumular
                try: supabase.storage.from_("logos").remove([nome_arquivo])
                except: pass
                
                # Sobe a nova
                supabase.storage.from_("logos").upload(nome_arquivo, bytes_data, {"content-type": f"image/{ext}"})
                
                # 2. Gera a URL pública e salva na tabela
                url_publica = supabase.storage.from_("logos").get_public_url(nome_arquivo)
                supabase.table("config_empresa").update({"logo_url": url_publica}).eq("id", 1).execute()
                
                st.success("Logomarca atualizada com sucesso!"); st.rerun()

    # --- ABA IMPORTAR (ESQUELETO PARA O FUTURO) ---
    elif menu == f"📑 {T['import']}":
        st.header(f"📑 {T['import']}")
        st.info("Aqui você poderá subir arquivos CSV/Excel para carregar dados em massa.")
        st.file_uploader("Selecione o arquivo Excel", type=['csv', 'xlsx'])
