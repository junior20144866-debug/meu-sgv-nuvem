import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONEXÃO SEGURA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR ANTI-TRAVAMENTO (O segredo para ligar o motor) ---
def db_read_safe(tabela):
    try:
        res = supabase.table(tabela).select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        # Se der erro no banco, o sistema avisa mas NÃO trava a tela de login
        return []

# --- 3. ESTILO WINDOWS ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .win-tile {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.2rem; font-weight: 800; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR MOTORES", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Senha incorreta")
else:
    # --- SISTEMA LIGADO ---
    # Só busca dados após o login para evitar o erro de API no boot
    config_list = db_read_safe("config")
    emp = config_list[0] if config_list else {}
    
    st.sidebar.title(emp.get('nome', 'JMQJ SGV'))
    menu = st.sidebar.radio("SISTEMAS", ["🏠 Painel", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: AJUSTES (PERSISTÊNCIA E LOGO) ---
    if menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações e Persistência")
        
        with st.form("form_cfg"):
            n = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            logomarca = st.file_uploader("Logomarca (PNG)", type=["png"])
            if st.form_submit_button("💾 SALVAR E FIXAR"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c}).execute()
                st.success("Configurações salvas!"); st.rerun()
        
        st.divider()
        st.subheader("🔥 ZERAR SISTEMA")
        if st.button("🗑️ LIMPAR TODO O ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if st.button("🗑️ LIMPAR TODOS OS CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()

    # --- ABA: ESTOQUE (EDIÇÃO DIRETA) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Estoque")
        with st.expander("📝 Adicionar / Editar"):
            with st.form("form_p"):
                id_p = st.number_input("ID (0 para novo, ou número para editar)", min_value=0)
                desc = st.text_input("Descrição")
                ean = st.text_input("EAN")
                pr = st.number_input("Preço", format="%.2f")
                if st.form_submit_button("SALVAR"):
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pr}
                    if id_p == 0: supabase.table("produtos").insert(pld).execute()
                    else: supabase.table("produtos").update(pld).eq("id", id_p).execute()
                    st.rerun()

        dados_p = db_read_safe("produtos")
        if dados_p: st.dataframe(pd.DataFrame(dados_p), use_container_width=True)

    # --- ABA: IMPORTAÇÃO (MOTOR DE CARGA) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga de Planilhas")
        tipo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Excel XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df = pd.read_excel(arq)
            for _, row in df.iterrows():
                d = row.to_dict()
                if tipo == "produtos":
                    ready = {"descricao": str(d.get('DESCRICAO', '')), "preco_venda": float(d.get('P_VENDA', 0)), "ean13": str(d.get('CODIGO', ''))}
                else:
                    ready = {"nome_completo": str(d.get('NOM', '')), "cpf_cnpj": str(d.get('CGC', '')), "endereco": str(d.get('RUA', ''))}
                supabase.table(tipo).insert(ready).execute()
            st.success("Carga realizada!"); st.rerun()

    # --- ABA: PAINEL (JANELAS) ---
    elif menu == "🏠 Painel":
        st.header(f"Painel {emp.get('nome', '')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile">PRODUTOS<br><p class="tile-num">{len(db_read_safe("produtos"))}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES<br><p class="tile-num">{len(db_read_safe("Clientes"))}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile">VENDAS<br><p class="tile-num">0</p></div>', unsafe_allow_html=True)
