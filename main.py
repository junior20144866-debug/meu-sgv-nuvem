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

st.set_page_config(page_title="JMQJ SGV v44", layout="wide", page_icon="💼")

# --- 2. MOTOR DE LIMPEZA (DNA SISCOM) ---
def limpar_valor_monetario(v):
    """Garante que o P_VENDA do seu Excel vire um número que o banco aceita"""
    try:
        if pd.isna(v) or v == "" or str(v).strip() == "": return 0.0
        # Remove R$, espaços, pontos de milhar e troca vírgula por ponto
        s = str(v).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
        # Mantém apenas números e o ponto
        s = re.sub(r'[^0-9.]', '', s)
        return float(s) if s else 0.0
    except:
        return 0.0

def buscar_dados():
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_p['preco_venda'] = pd.to_numeric(df_p['preco_venda'], errors='coerce').fillna(0.0)
        
        df_cl = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        return (c[0] if c else {}), df_p, df_cl
    except: return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. INTERFACE ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile { background: white; padding: 20px; border-radius: 8px; border-top: 5px solid #0078D4; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .val-m { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = buscar_dados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: IMPORTAÇÃO (MAPEADA PELO SEU EXCEL REAL) ---
    if menu == "📑 Importação":
        st.header("📑 Importação Inteligente (Mapeamento Siscom)")
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
                        desc = str(r.get('DESCRICAO', '')).strip()
                        if desc: # Só importa se tiver nome
                            pld = {
                                "descricao": desc,
                                "preco_venda": limpar_valor_monetario(r.get('P_VENDA', 0)),
                                "ean13": str(r.get('BARRA', r.get('CODIGO', ''))).strip()
                            }
                            supabase.table("produtos").insert(pld).execute()
                            sucesso += 1
                    else:
                        nom = str(r.get('NOM', r.get('NOME', ''))).strip()
                        if nom:
                            pld = {
                                "nome_completo": nom,
                                "cpf_cnpj": str(r.get('CGC', r.get('CPF', ''))).strip(),
                                "endereco": f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CID', '')}"
                            }
                            supabase.table("Clientes").insert(pld).execute()
                            sucesso += 1
                except Exception as e:
                    pass # Silencia erros de linhas vazias
                prog.progress((i + 1) / len(rows))
            
            st.success(f"Carga finalizada: {sucesso} registros salvos!")
            time.sleep(1.5)
            st.rerun()

    # --- EXIBIÇÃO ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = menu.replace("📦 ", "").replace("👥 ", "")
        st.header(f"Relação de {tab}")
        df_show = df_e if tab == "Estoque" else df_c
        if not df_show.empty:
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.warning(f"A tabela de {tab} está vazia no banco de dados.")

    # --- DASHBOARD ---
    elif menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="win-tile">PRODUTOS<br><span class="val-m">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES<br><span class="val-m">{len(df_c)}</span></div>', unsafe_allow_html=True)

    # --- AJUSTES ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Ajustes")
        with st.form("f"):
            n = st.text_input("Empresa", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute(); st.rerun()
        
        st.divider()
        if st.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
