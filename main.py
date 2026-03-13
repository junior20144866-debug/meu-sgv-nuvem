import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

# --- 2. ESTADO DO SISTEMA (Branding) ---
if 'empresa' not in st.session_state:
    st.session_state.empresa = {"nome": "SGV Evolution", "cnpj": "", "end": "", "tel": ""}

# --- 3. PÁGINA: ESTOQUE (RECONSTRUÍDA PARA VISIBILIDADE) ---
def render_estoque():
    st.header("📦 Gestão de Estoque")
    try:
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df = pd.DataFrame(res)
            # Garantimos que os nomes das colunas coincidam com o que vem do banco
            st.dataframe(df, use_container_width=True)
            
            st.subheader("🛠️ Operações Rápidas")
            prod_ref = st.selectbox("Selecionar produto para excluir", [f"{p.get('id')} - {p.get('descricao')}" for p in res])
            if st.button("🗑️ Excluir Produto Selecionado"):
                id_p = prod_ref.split(" - ")[0]
                supabase.table("produtos").delete().eq("id", id_p).execute()
                st.success("Excluído!"); st.rerun()
        else:
            st.info("O banco de dados de produtos está vazio no momento.")
    except Exception as e:
        st.error(f"Erro ao carregar estoque: {e}")

# --- 4. PÁGINA: CLIENTES (CONTROLE TOTAL DE EDIÇÃO) ---
def render_clientes():
    st.header("👥 Gestão de Clientes")
    res = supabase.table("Clientes").select("*").execute().data
    
    if res:
        for c in res:
            with st.expander(f"👤 {c.get('nome_completo', 'Sem Nome')}"):
                with st.form(f"edit_{c['id']}"):
                    novo_nome = st.text_input("Nome", value=c.get('nome_completo', ''))
                    novo_doc = st.text_input("Documento", value=c.get('cpf_cnpj', ''))
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Salvar Alterações"):
                        supabase.table("Clientes").update({"nome_completo": novo_nome, "cpf_cnpj": novo_doc}).eq("id", c['id']).execute()
                        st.success("Atualizado!"); st.rerun()
                    if c2.form_submit_button("🗑️ Excluir Cliente"):
                        supabase.table("Clientes").delete().eq("id", c['id']).execute()
                        st.rerun()
    else:
        st.info("Nenhum cliente na base.")

# --- 5. PÁGINA: CONFIGURAÇÕES (EXPANDIDA) ---
def render_config():
    st.header("⚙️ Configurações da Empresa")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖼️ Identidade Visual")
        logo = st.file_uploader("Trocar Logomarca", type=["png", "jpg"])
        if logo: st.image(logo, width=150)
        
    with col2:
        st.subheader("📝 Dados Corporativos")
        st.session_state.empresa['nome'] = st.text_input("Nome Fantasia", st.session_state.empresa['nome'])
        st.session_state.empresa['cnpj'] = st.text_input("CNPJ", st.session_state.empresa['cnpj'])
        st.session_state.empresa['end'] = st.text_area("Endereço Completo", st.session_state.empresa['end'])
        st.session_state.empresa['tel'] = st.text_input("Telefone/WhatsApp", st.session_state.empresa['tel'])
        if st.button("Salvar Tudo"):
            st.success("Dados da empresa salvos com sucesso!")

    st.divider()
    if st.button("🔥 ZERAR SISTEMA (CUIDADO)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

# --- 6. NAVEGAÇÃO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    if st.text_input("Senha", type="password") == "Naksu@6026":
        st.session_state.auth = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importar", "⚙️ Configurações"])
    
    if menu == "📦 Estoque": render_estoque()
    elif menu == "👥 Clientes": render_clientes()
    elif menu == "⚙️ Configurações": render_config()
    elif menu == "📑 Importar":
        # (Código de importação anterior mantido aqui para funcionar)
        st.header("📑 Importação")
        dest = st.selectbox("Para onde?", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo", type=["xlsx"])
        if arq and st.button("🚀 Processar"):
            df = pd.read_excel(arq)
            for _, row in df.iterrows():
                # Lógica simplificada de inserção
                try:
                    d = {"descricao": str(row.get('DESCRICAO', row.get('NOME')))}
                    supabase.table(dest).insert(d).execute()
                except: pass
            st.success("Importado!"); st.rerun()
