import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime, timedelta

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SaaS", layout="wide", page_icon="🚀")

# --- 2. MOTOR DE RECUPERAÇÃO ULTRA-ESTÁVEL ---
def carregar_universo_v72():
    try:
        # Busca Config: Tenta pegar qualquer registro da tabela config
        c = supabase.table("config").select("*").execute().data
        # Se houver dados, pegamos o primeiro. Se não, criamos um molde vazio.
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Busca Produtos e Clientes (Usando seus nomes reais: NOM, p_venda)
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("id").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'p_venda'])
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'NOM', 'RUA', 'BAI'])
        
        return empresa, df_p, df_c
    except Exception as e:
        return {"nome": "SGV", "id": 1}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .metric-val { font-size: 2.2rem; font-weight: 700; color: #2563EB; }
    .paper { background: white; padding: 30px; border: 1px solid #000; font-family: monospace; color: black; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 🚀")
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("ACESSAR"):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_universo_v72()

    with st.sidebar:
        # Tentativa de exibir a logo (se a coluna existir e tiver dados)
        if emp.get('logo_base64'):
            try: st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write(f"CNPJ: {emp.get('cnpj', '')}")
        menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Carga Massiva", "⚙️ Ajustes"])

    # --- DASHBOARD ---
    if menu == "📊 Painel":
        st.header(f"Gestão: {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>CAIXA DIA<br><span class='metric-val'>R$ 0,00</span></div>", unsafe_allow_html=True)

    # --- VENDAS ---
    elif menu == "💰 Vendas":
        st.header("Vendas")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("v_form"):
                cli = st.selectbox("Cliente", df_c['NOM'].tolist() if not df_c.empty else ["Sem Clientes"])
                prod = st.selectbox("Produto", df_e['descricao'].tolist() if not df_e.empty else ["Sem Estoque"])
                qtd = st.number_input("Qtd", min_value=1)
                if st.form_submit_button("GERAR PRÉVIA"):
                    st.success("Prévia gerada abaixo")
        
    # --- CLIENTES (MAPEADO PARA NOM) ---
    elif menu == "👥 Clientes":
        st.header("Clientes")
        if not df_c.empty:
            st.dataframe(df_c[['id', 'NOM', 'RUA', 'BAI']], use_container_width=True, hide_index=True)
        else:
            st.info("Importe os clientes na aba 'Carga Massiva'.")

    # --- CARGA MASSIVA ---
    elif menu == "📂 Carga Massiva":
        st.header("Importação")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "p_venda": float(pv)}).execute()
                    else:
                        supabase.table("Clientes").insert({"NOM": str(r.get('NOM')), "RUA": str(r.get('RUA', '')), "BAI": str(r.get('BAI', ''))}).execute()
                except: pass
            st.success("Carga concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES (O FIM DO EFEITO SANFONA) ---
    elif menu == "⚙️ Ajustes":
        st.header("Configurações da Empresa")
        with st.form("f_emp"):
            nome_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Trocar Logo (PNG)", type=["png"])
            
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo:
                    l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                
                # Payload simplificado para evitar erros de colunas inexistentes
                dados_fixos = {"nome": nome_e, "cnpj": cnpj_e, "end": end_e}
                
                # Se você tiver a coluna de logo no banco, incluímos ela
                if 'logo_base64' in emp: dados_fixos["logo_base64"] = l64
                
                try:
                    # Tenta dar Upsert no ID 1 para cravar os dados
                    supabase.table("config").upsert({"id": 1, **dados_fixos}).execute()
                    st.success("DADOS CRAVADOS COM SUCESSO!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao fixar: {e}")

        st.divider()
        if st.button("🔥 RESET TOTAL DO SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute()
            st.rerun()
