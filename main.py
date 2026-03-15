import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. NÚCLEO DE CONEXÃO E ESTADO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. ARQUITETURA DE DESIGN (WINDOWS EXPERIENCE) ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px; transition: 0.3s;
    }
    .win-tile:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    .tile-num { font-size: 2.8rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-text { font-weight: bold; color: #555; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORES DE SINCRONIA (O FIM DO EFEITO SANFONA) ---
def db_fetch(tabela):
    try: return supabase.table(tabela).select("*").execute().data
    except: return []

def sync_empresa():
    dados = db_fetch("config")
    return dados[0] if dados else {"nome": "JMQJ SGV", "cnpj": "", "end": ""}

# --- 4. CONTROLE DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1,1])
    with col2:
        st.info("Insira sua chave de acesso para ligar o sistema.")
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave incorreta!")
else:
    # --- DADOS PERSISTENTES ---
    emp = sync_empresa()
    
    # Barra Lateral Polida
    with st.sidebar:
        st.title(emp['nome'])
        st.write("---")
        menu = st.radio("NAVEGAÇÃO", 
            ["🏠 Dashboard", "🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "📑 Importação", "💰 Financeiro", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA: DASHBOARD (JANELAS INTELIGENTES) ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp['nome']}")
        p_count = len(db_fetch("produtos"))
        c_count = len(db_fetch("Clientes"))
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-tile"><p class="tile-text">📦 Estoque</p><p class="tile-num">{p_count}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-text">👥 Clientes</p><p class="tile-num">{c_count}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-text">💰 Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="tile-text">📈 Status</p><p class="tile-num" style="color:green">ON</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE (CONTROLE TOTAL + EDIÇÃO) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Inventário")
        with st.expander("📝 Inserir ou Editar Produto"):
            with st.form("form_p"):
                id_e = st.number_input("ID para Edição (0 para Novo)", min_value=0)
                desc = st.text_input("Descrição")
                ean = st.text_input("Código de Barras (EAN)")
                pre = st.number_input("Preço de Venda", format="%.2f")
                if st.form_submit_button("CONCLUIR OPERAÇÃO"):
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pre}
                    if id_e == 0: supabase.table("produtos").insert(pld).execute()
                    else: supabase.table("produtos").update(pld).eq("id", id_e).execute()
                    st.success("Dados processados!"); st.rerun()
        
        df_p = pd.DataFrame(db_fetch("produtos"))
        if not df_p.empty: st.dataframe(df_p, use_container_width=True)

    # --- ABA: CLIENTES (DADOS COMPLETOS) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        with st.expander("📝 Novo ou Alterar Cliente"):
            with st.form("form_c"):
                id_c = st.number_input("ID para Edição (0 para Novo)", min_value=0)
                nome = st.text_input("Nome/Razão Social")
                doc = st.text_input("CPF/CNPJ")
                end = st.text_input("Endereço Completo")
                if st.form_submit_button("CONCLUIR CADASTRO"):
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                    if id_c == 0: supabase.table("Clientes").insert(pld).execute()
                    else: supabase.table("Clientes").update(pld).eq("id", id_c).execute()
                    st.rerun()
        
        df_c = pd.DataFrame(db_fetch("Clientes"))
        if not df_c.empty: st.dataframe(df_c, use_container_width=True)

    # --- ABA: IMPORTAÇÃO (MOTOR INTELIGENTE) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga de Dados Inteligente")
        dest = st.selectbox("Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Suba sua planilha XLSX", type=["xlsx"])
        if file and st.button("🚀 EXECUTAR CARGA EM MASSA"):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                d = row.to_dict()
                ready = {"descricao": d.get('DESCRICAO'), "preco_venda": d.get('P_VENDA'), "ean13": d.get('CODIGO')} if dest == "produtos" else {"nome_completo": d.get('NOM'), "cpf_cnpj": d.get('CGC'), "endereco": d.get('RUA')}
                if any(ready.values()): supabase.table(dest).insert(ready).execute()
            st.success("Carga concluída!"); st.rerun()

    # --- ABA: CONFIGURAÇÕES (O CORAÇÃO DO CONTROLE) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações e Controle do Sistema")
        
        with st.form("config_master"):
            st.subheader("🏢 Identidade da JMQJ SGV")
            n = st.text_input("Nome Fantasia", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logomarca da Empresa (PNG)", type=["png"])
            if st.form_submit_button("💾 SALVAR E PERSISTIR DADOS"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "end": e}).execute()
                st.success("Dados eternizados no banco!"); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE PERIGO (Limpeza Total)")
        col1, col2 = st.columns(2)
        if col1.button("🔥 ZERAR TODO O ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if col2.button("🔥 ZERAR TODOS OS CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
