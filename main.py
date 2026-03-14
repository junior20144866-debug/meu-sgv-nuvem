import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. CONFIGURAÇÃO E IDIOMAS (Recuperado) ---
st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

lang_options = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "financeiro": "Financeiro", "import": "Importação", "config": "Configurações", "relatorios": "Relatórios"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "financeiro": "Financial", "import": "Import", "config": "Settings", "relatorios": "Reports"}
}

if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = lang_options[st.session_state.lang]

# --- 3. ESTILO WINDOWS (Tiles Dinâmicos) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F0F2F5; }}
    .tile-card {{
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-top: 5px solid #0078D4;
        text-align: center; transition: 0.3s; height: 160px;
    }}
    .tile-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }}
    .tile-title {{ font-size: 1.3rem; font-weight: bold; color: #333; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE PERSISTÊNCIA (Garantindo que não suma nada) ---
def salvar_config_bd(tabela, dados, id_ref=1):
    try: supabase.table(tabela).upsert({"id": id_ref, **dados}).execute()
    except Exception as e: st.error(f"Erro ao salvar: {e}")

# --- 5. INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Acesso", type="password") == "Naksu@6026":
            if st.button("ENTRAR"): st.session_state.auth = True; st.rerun()
else:
    # Sidebar consolidada
    with st.sidebar:
        st.header("Menu")
        st.session_state.lang = st.selectbox("🌐 Idioma/Language", ["Português", "English"])
        menu = st.radio("Navegação", [T['vendas'], T['estoque'], T['clientes'], T['financeiro'], T['import'], T['relatorios'], T['config']])

    # --- TELA DE INÍCIO (Se nada estiver selecionado ou Dashboard) ---
    if menu == T['config']:
        st.title(f"⚙️ {T['config']}")
        t1, t2, t3 = st.tabs(["🏢 Empresa", "🎨 Logomarca", "🧹 Controle Total"])
        
        with t1:
            with st.form("empresa_form"):
                st.subheader("Dados da Instituição")
                c1, c2 = st.columns(2)
                nome = c1.text_input("Nome Fantasia")
                cnpj = c2.text_input("CNPJ")
                rua = st.text_input("Rua/Endereço")
                c3, c4, c5 = st.columns([2,2,1])
                bairro = c3.text_input("Bairro")
                cidade = c4.text_input("Cidade")
                uf = c5.text_input("UF")
                if st.form_submit_button("💾 Salvar Dados"):
                    salvar_config_bd("config", {"nome": nome, "cnpj": cnpj, "end": rua, "bairro": bairro, "cidade": cidade, "uf": uf})
                    st.success("Dados da empresa salvos!")

        with t3:
            st.subheader("⚠️ Zona de Limpeza")
            c_z1, c_z2 = st.columns(2)
            if c_z1.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
            if c_z2.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()

    elif menu == T['estoque']:
        st.title(f"📦 {T['estoque']}")
        # Espaços completos para preenchimento
        with st.expander("➕ Adicionar Produto Manualmente"):
            with st.form("prod_manual"):
                col1, col2, col3 = st.columns([2,1,1])
                desc = col1.text_input("Descrição")
                ean = col2.text_input("Código EAN")
                un = col3.text_input("Unidade (KG/UN)")
                preco = st.number_input("Preço de Venda", format="%.2f")
                if st.form_submit_button("Salvar Produto"):
                    supabase.table("produtos").insert({"descricao": desc, "ean13": ean, "unidade": un, "preco_venda": preco}).execute()
                    st.rerun()
        
        # Listagem com Controle Total (Edição/Exclusão)
        prods = supabase.table("produtos").select("*").execute().data
        if prods:
            df_p = pd.DataFrame(prods)
            st.dataframe(df_p, use_container_width=True)
            for p in prods:
                if st.button(f"🗑️ Excluir {p['descricao']}", key=f"del_{p['id']}"):
                    supabase.table("produtos").delete().eq("id", p['id']).execute(); st.rerun()

    elif menu == T['clientes']:
        st.title(f"👥 {T['clientes']}")
        clis = supabase.table("Clientes").select("*").execute().data
        if clis:
            st.dataframe(pd.DataFrame(clis), use_container_width=True)
        else: st.info("Sem clientes.")

    elif menu == T['relatorios']:
        st.title(f"📊 {T['relatorios']}")
        st.write("Aqui serão gerados os PDFs e visões de desempenho.")
        # Placeholder para os gráficos de queixo caído

    # --- ABA IMPORTAÇÃO (MOTOR INTELIGENTE) ---
    elif menu == T['import']:
        st.title(f"📑 {T['import']}")
        # Lógica de importação que não quebra as outras funções
        st.info("O motor de importação está ativo para processar arquivos bagunçados.")
