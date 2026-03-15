import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONEXÃO E ESTADO DE SESSÃO (ANTI-SANFONA) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Inicialização do Cérebro do Sistema
if 'auth' not in st.session_state: st.session_state.auth = False
if 'empresa' not in st.session_state: st.session_state.empresa = {}

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE SINCRONIZAÇÃO TOTAL ---
def carregar_tudo():
    """Garante que os dados estejam na memória e no banco simultaneamente"""
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute()
        if conf.data: st.session_state.empresa = conf.data[0]
        
        prods = supabase.table("produtos").select("*").execute()
        st.session_state.estoque = prods.data if prods.data else []
        
        clis = supabase.table("Clientes").select("*").execute()
        st.session_state.clientes_db = clis.data if clis.data else []
    except:
        st.error("Erro de conexão com o Banco de Dados.")

# --- 3. INTERFACE VISUAL (ESTILO WINDOWS) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.5rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-lab { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                carregar_tudo()
                st.rerun()
else:
    # REFRESH DE DADOS
    if not st.session_state.empresa: carregar_tudo()
    emp = st.session_state.empresa
    
    # BARRA LATERAL (IDENTIDADE FIXA)
    with st.sidebar:
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- ABA: DASHBOARD (JANELAS) ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-tile"><p class="tile-lab">Estoque</p><p class="tile-num">{len(st.session_state.get("estoque", []))}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-lab">Clientes</p><p class="tile-num">{len(st.session_state.get("clientes_db", []))}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-lab">Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="tile-lab">Status</p><p class="tile-num" style="color:green">ON</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE & CLIENTES (EDIÇÃO INTEGRADA) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Controle de {menu}")
        
        with st.expander("📝 Inserir ou Editar (Use ID 0 para novo)"):
            with st.form("form_master"):
                id_edit = st.number_input("ID do Registro", min_value=0, step=1)
                if tab == "produtos":
                    desc = st.text_input("Descrição")
                    ean = st.text_input("EAN")
                    preco = st.number_input("Preço", format="%.2f")
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": preco}
                else:
                    nome = st.text_input("Nome")
                    doc = st.text_input("CNPJ/CPF")
                    end = st.text_input("Endereço")
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                
                if st.form_submit_button("GRAVAR"):
                    if id_edit == 0: supabase.table(tab).insert(pld).execute()
                    else: supabase.table(tab).update(pld).eq("id", id_edit).execute()
                    carregar_tudo(); st.rerun()

        dados = st.session_state.get("estoque" if tab == "produtos" else "clientes_db", [])
        if dados:
            st.dataframe(pd.DataFrame(dados), use_container_width=True)
            id_del = st.number_input("ID para EXCLUIR", min_value=0)
            if st.button("❌ Confirmar Exclusão"):
                supabase.table(tab).delete().eq("id", id_del).execute()
                carregar_tudo(); st.rerun()

    # --- ABA: CONFIGURAÇÕES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações do Sistema")
        with st.form("cfg"):
            n = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logomarca (PNG/GIF/JPG)", type=["png", "gif", "jpg"])
            if st.form_submit_button("💾 SALVAR E FIXAR IDENTIDADE"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "end": e}).execute()
                carregar_tudo(); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE RESET (Controle Total)")
        col1, col2 = st.columns(2)
        if col1.button("🗑️ ZERAR ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            carregar_tudo(); st.rerun()
        if col2.button("🗑️ ZERAR CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute()
            carregar_tudo(); st.rerun()

    # --- ABA: IMPORTAÇÃO (MOTOR INTELIGENTE) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação em Massa")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 PROCESSAR"):
            df = pd.read_excel(arq)
            for _, row in df.iterrows():
                d = row.to_dict()
                if alvo == "produtos":
                    r = {"descricao": str(d.get('DESCRICAO', '')), "preco_venda": float(d.get('P_VENDA', 0)), "ean13": str(d.get('CODIGO', ''))}
                else:
                    r = {"nome_completo": str(d.get('NOM', '')), "cpf_cnpj": str(d.get('CGC', '')), "endereco": str(d.get('RUA', ''))}
                supabase.table(alvo).insert(r).execute()
            carregar_tudo(); st.rerun()
