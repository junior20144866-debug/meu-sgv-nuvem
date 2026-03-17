import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO E SEGURANÇA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide", page_icon="💼")

# --- 2. MOTOR DE SINCRONIA (BUSCA DIRETA NO BANCO) ---
def carregar_dados(tabela):
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except: return []

# --- 3. ESTILO VISUAL MODERNO ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-top: 5px solid #0078D4;
        margin-bottom: 20px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra de Ativação", type="password")
        if st.button("ATIVAR SISTEMA 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # --- CARREGAMENTO GLOBAL (FIM DO EFEITO SANFONA) ---
    config_db = carregar_dados("config")
    emp = config_db[0] if config_db else {}
    estoque = carregar_dados("produtos")
    clientes = carregar_dados("Clientes")

    # --- BARRA LATERAL (IDENTIDADE VISUAL) ---
    with st.sidebar:
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write(f"📍 {emp.get('end', 'Endereço não definido')}")
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="card">Produtos<br><span class="metric-value">{len(estoque)}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card">Clientes<br><span class="metric-value">{len(clientes)}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card">Vendas<br><span class="metric-value">0</span></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="card">Financeiro<br><span class="metric-value">R$ 0,00</span></div>', unsafe_allow_html=True)

    # --- ESTOQUE / CLIENTES (EDIÇÃO E EXCLUSÃO) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Gestão de {menu}")
        
        with st.expander("📝 Cadastro Manual / Edição"):
            with st.form("form_dados"):
                id_reg = st.number_input("ID (0 para Novo)", min_value=0)
                if tab == "produtos":
                    d = st.text_input("Descrição")
                    e = st.text_input("EAN13")
                    p = st.number_input("Preço Venda", format="%.2f")
                    pld = {"descricao": d, "ean13": e, "preco_venda": p}
                else:
                    n = st.text_input("Nome Completo")
                    doc = st.text_input("CPF/CNPJ")
                    en = st.text_input("Endereço")
                    pld = {"nome_completo": n, "cpf_cnpj": doc, "endereco": en}
                
                if st.form_submit_button("CONSOLIDAR"):
                    if id_reg == 0: supabase.table(tab).insert(pld).execute()
                    else: supabase.table(tab).update(pld).eq("id", id_reg).execute()
                    st.rerun()

        dados_tabela = estoque if tab == "produtos" else clientes
        if dados_tabela:
            df = pd.DataFrame(dados_tabela)
            st.dataframe(df, use_container_width=True)
            id_del = st.number_input("ID para EXCLUIR", min_value=0, key="del")
            if st.button("🗑️ Deletar Registro"):
                supabase.table(tab).delete().eq("id", id_del).execute()
                st.rerun()

    # --- IMPORTAÇÃO INTELIGENTE (LIMPEZA DE DADOS) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga Massiva Inteligente")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Suba seu Excel (XLSX)", type=["xlsx"])
        
        if file and st.button("🚀 PROCESSAR E IMPORTAR"):
            df_in = pd.read_excel(file)
            prog = st.progress(0)
            for i, row in df_in.iterrows():
                try:
                    if alvo == "produtos":
                        # Limpeza inteligente de preço (R$, pontos, vírgulas)
                        p_raw = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        pld = {"descricao": str(row.get('DESCRICAO', '')), "preco_venda": float(p_raw), "ean13": str(row.get('CODIGO', ''))}
                    else:
                        pld = {"nome_completo": str(row.get('NOM', '')), "cpf_cnpj": str(row.get('CGC', '')), "endereco": str(row.get('RUA', ''))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
                prog.progress((i + 1) / len(df_in))
            st.success("Carga concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES E CONFIGURAÇÕES (O CORAÇÃO DO CABEÇALHO) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações da Empresa")
        with st.form("form_config"):
            c1, c2 = st.columns(2)
            nome_emp = c1.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cnpj_emp = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_emp = st.text_input("Endereço Completo", value=emp.get('end', ''))
            tel_emp = c1.text_input("Telefone", value=emp.get('tel', ''))
            email_emp = c2.text_input("E-mail", value=emp.get('email', ''))
            logo_url = st.text_input("Link da Logomarca (URL)", value=emp.get('logo_base64', ''))
            
            st.write("---")
            vias = st.radio("Padrão de Impressão", ["1 Via", "2 Vias"], index=0)
            
            if st.form_submit_button("💾 SALVAR CONFIGURAÇÕES"):
                pld_cfg = {
                    "id": 1, "nome": nome_emp, "cnpj": cnpj_emp, 
                    "end": end_emp, "tel": tel_emp, "email": email_emp, 
                    "logo_base64": logo_url
                }
                supabase.table("config").upsert(pld_cfg).execute()
                st.success("Identidade Fixada!"); time.sleep(1); st.rerun()

        st.divider()
        st.subheader("🗑️ MANUTENÇÃO")
        if st.button("🗑️ ZERAR TODO O SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.warning("Banco de dados limpo!"); time.sleep(1); st.rerun()
