import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA (Não alterar) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. ESTILO WINDOWS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.5rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-text { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE PERSISTÊNCIA BRUTA ---
def db_read(tabela):
    try: return supabase.table(tabela).select("*").execute().data
    except: return []

def db_save_config(dados):
    return supabase.table("config").upsert({"id": 1, **dados}).execute()

# --- 4. SISTEMA DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR MOTORES", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # --- CARREGAMENTO INICIAL DE CONFIGURAÇÕES ---
    config_data = db_read("config")
    emp = config_data[0] if config_data else {}
    
    st.sidebar.title(emp.get('nome', 'JMQJ SGV'))
    menu = st.sidebar.radio("SISTEMAS", ["🏠 Painel Início", "🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- PÁGINA: INÍCIO (JANELAS DINÂMICAS) ---
    if menu == "🏠 Painel Início":
        st.header(f"Gestão Integrada - {emp.get('nome', 'JMQJ')}")
        prods = db_read("produtos")
        clis = db_read("Clientes")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-tile"><p class="tile-text">Estoque</p><p class="tile-num">{len(prods)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-text">Clientes</p><p class="tile-num">{len(clis)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-text">Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="tile-text">Status</p><p class="tile-num" style="color:green">ON</p></div>', unsafe_allow_html=True)

    # --- PÁGINA: ESTOQUE (COM EDIÇÃO DIRETA) ---
    elif menu == "📦 Estoque":
        st.header("📦 Controle de Inventário")
        
        with st.expander("📝 Adicionar ou Editar Produto"):
            with st.form("form_estoque"):
                id_prod = st.number_input("ID para Edição (0 para Novo)", min_value=0)
                desc = st.text_input("Descrição do Produto")
                ean = st.text_input("EAN / Código")
                un = st.text_input("Unidade (KG/UN)")
                preco = st.number_input("Preço de Venda", format="%.2f")
                if st.form_submit_button("SALVAR PRODUTO"):
                    payload = {"descricao": desc, "ean13": ean, "unidade": un, "preco_venda": preco}
                    if id_prod == 0: supabase.table("produtos").insert(payload).execute()
                    else: supabase.table("produtos").update(payload).eq("id", id_prod).execute()
                    st.success("Dados salvos!"); st.rerun()

        dados_p = db_read("produtos")
        if dados_p:
            df_p = pd.DataFrame(dados_p)
            st.dataframe(df_p[["id", "descricao", "ean13", "unidade", "preco_venda"]], use_container_width=True)

    # --- PÁGINA: CLIENTES (DADOS COMPLETOS) ---
    elif menu == "👥 Clientes":
        st.header("👥 Base de Clientes")
        with st.expander("📝 Adicionar ou Editar Cliente"):
            with st.form("form_cliente"):
                id_cli = st.number_input("ID para Edição (0 para Novo)", min_value=0)
                nome = st.text_input("Nome / Razão Social")
                doc = st.text_input("CPF / CNPJ")
                end = st.text_input("Endereço / Bairro / Cidade / UF")
                if st.form_submit_button("SALVAR CLIENTE"):
                    payload = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                    if id_cli == 0: supabase.table("Clientes").insert(payload).execute()
                    else: supabase.table("Clientes").update(payload).eq("id", id_cli).execute()
                    st.rerun()
        
        dados_c = db_read("Clientes")
        if dados_c: st.dataframe(pd.DataFrame(dados_c), use_container_width=True)

    # --- PÁGINA: CONFIGURAÇÕES (BOTÕES ZERAR + LOGO + PERSISTÊNCIA) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Centro de Comando e Ajustes")
        
        with st.form("config_master"):
            st.subheader("🏢 Identidade da Empresa")
            nome_emp = st.text_input("Nome Fantasia", value=emp.get('nome', ''))
            cnpj_emp = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_emp = st.text_input("Endereço Fiscal", value=emp.get('end', ''))
            if st.form_submit_button("💾 SALVAR E PERSISTIR DADOS"):
                db_save_config({"nome": nome_emp, "cnpj": cnpj_emp, "end": end_emp})
                st.success("Configurações eternizadas no banco!"); st.rerun()
        
        st.divider()
        st.subheader("🖼️ Logomarca")
        st.file_uploader("Upload da Logomarca (PNG/JPG)", type=["png", "jpg"])
        
        st.divider()
        st.subheader("🔥 ZONA DE PERIGO (RESET TOTAL)")
        col_z1, col_z2 = st.columns(2)
        if col_z1.button("🗑️ ZERAR TODO O ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if col_z2.button("🗑️ ZERAR TODOS OS CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()

    # --- PÁGINA: IMPORTAÇÃO (MOTOR OPERANTE) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação Inteligente em Massa")
        target = st.selectbox("Para onde enviar os dados?", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba sua planilha XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df = pd.read_excel(arq)
            for _, row in df.iterrows():
                d = row.to_dict()
                if target == "produtos":
                    ready = {"descricao": str(d.get('DESCRICAO', '')), "preco_venda": float(d.get('P_VENDA', 0)), "ean13": str(d.get('CODIGO', ''))}
                else:
                    ready = {"nome_completo": str(d.get('NOM', '')), "cpf_cnpj": str(d.get('CGC', '')), "endereco": str(d.get('RUA', ''))}
                supabase.table(target).insert(ready).execute()
            st.success("Importação concluída! Verifique o Painel de Início."); st.rerun()
