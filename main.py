import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v46", layout="wide", page_icon="💼")

# --- 2. MOTOR DE TRATAMENTO DE DADOS (DNA SISCOM) ---
def limpar_valor_monetario(v):
    try:
        if pd.isna(v) or str(v).strip() == "": return 0.0
        s = str(v).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
        s = re.sub(r'[^0-9.]', '', s)
        return float(s) if s else 0.0
    except: return 0.0

def buscar_dados_vivos():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        df_e = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        return (conf[0] if conf else {}), df_e, df_c
    except: return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. INTERFACE E ESTILO ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile { background: white; padding: 20px; border-radius: 8px; border-top: 5px solid #0078D4; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .metric-val { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("ATIVAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = buscar_dados_vivos()
    
    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="win-tile">PRODUTOS NO BANCO<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES NO BANCO<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)

    # --- ABA: IMPORTAÇÃO (MAPEAMENTO FLEXÍVEL) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga de Dados (Mapeamento Inteligente)")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba o arquivo XLSX", type=["xlsx"])
        
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            sucesso = 0
            
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        # Mapeia DESCRICAO ou NOME / P_VENDA ou PRECO
                        desc = r.get('DESCRICAO', r.get('descricao', r.get('NOME', '')))
                        if pd.notna(desc) and str(desc).strip() != "":
                            pld = {
                                "descricao": str(desc).strip(),
                                "preco_venda": limpar_valor_monetario(r.get('P_VENDA', r.get('preco_venda', 0))),
                                "ean13": str(r.get('BARRA', r.get('CODIGO', ''))).strip()
                            }
                            supabase.table("produtos").insert(pld).execute()
                            sucesso += 1
                    else:
                        # Mapeia NOM ou NOME / CGC ou CPF
                        nom = r.get('NOM', r.get('nome_completo', r.get('NOME', '')))
                        if pd.notna(nom) and str(nom).strip() != "":
                            pld = {
                                "nome_completo": str(nom).strip(),
                                "cpf_cnpj": str(r.get('CGC', r.get('CPF', r.get('cpf_cnpj', '')))).strip(),
                                "endereco": f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CID', '')}"
                            }
                            supabase.table("Clientes").insert(pld).execute()
                            sucesso += 1
                except: pass
                prog.progress((i + 1) / len(rows))
            
            st.success(f"Carga finalizada: {sucesso} registros integrados com sucesso!")
            time.sleep(1.5); st.rerun()

    # --- ABA: ESTOQUE / CLIENTES ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        st.header(f"Relação de {menu}")
        df_show = df_e if "Estoque" in menu else df_c
        if not df_show.empty:
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.warning("Tabela vazia no banco de dados.")

    # --- ABA: AJUSTES (BOTÕES DE CONTROLE REPOSTOS) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações e Controles")
        with st.form("f_adj"):
            n = st.text_input("Nome Empresa", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 SALVAR CONFIG"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute(); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE RESET (Controle Total)")
        c1, c2, c3 = st.columns(3)
        if c1.button("🗑️ ZERAR ESTOQUE", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("👥 ZERAR CLIENTES", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("🔥 ZERAR TUDO", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
