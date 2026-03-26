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

st.set_page_config(page_title="JMQJ SGV SaaS", layout="wide", page_icon="📈")

# --- 2. MOTOR DE RECUPERAÇÃO (MAPEAMENTO DOS ARQUIVOS BÚSSOLA) ---
def sincronizar_universo_v76():
    try:
        # Busca Configuração (id=1)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Busca Produtos (Mapeado p/ p_venda conforme CADASTRO.DBF)
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'p_venda'])
        
        # Busca Clientes (Mapeado p/ NOM, RUA, BAI conforme CLIENTES.DBF)
        cl = supabase.table("Clientes").select("*").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'NOM', 'RUA', 'BAI', 'TEL1'])
        
        return empresa, df_p, df_c
    except Exception as e:
        st.error(f"Erro de sincronia: {e}")
        return {"id": 1, "nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL SAAS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .metric-val { font-size: 2.2rem; font-weight: 700; color: #2563EB; }
    .paper { background: white; padding: 30px; border: 1px solid #000; font-family: monospace; color: black; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 🚀")
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("ACESSAR", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = sincronizar_universo_v76()

    with st.sidebar:
        if emp.get('logo_base64'): 
            try: st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Carga Massiva", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "📊 Painel":
        st.header(f"Gestão: {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>VENDAS HOJE<br><span class='metric-val'>0</span></div>", unsafe_allow_html=True)

    # --- ABA: VENDAS (MODELO BÚSSOLA) ---
    elif menu == "💰 Vendas":
        st.header("Vendas e Pedidos")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("v_form"):
                cli = st.selectbox("Cliente", df_c['NOM'].tolist() if not df_c.empty else ["Carga Pendente"])
                prod = st.selectbox("Produto", df_e['descricao'].tolist() if not df_e.empty else ["Vazio"])
                qtd = st.number_input("Quantidade", min_value=1)
                prazo = st.number_input("Vencimento (Dias)", min_value=0, value=30)
                if st.form_submit_button("GERAR DOCUMENTO"):
                    venc = (datetime.now() + timedelta(days=prazo)).strftime('%d/%m/%Y')
                    with col2:
                        st.markdown(f"""
                        <div class="paper">
                            <table style="width:100%"><tr>
                            <td><img src="{emp.get('logo_base64', '')}" width="70"></td>
                            <td style="text-align:center"><b>{emp.get('nome', '')}</b><br>CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}</td>
                            <td style="text-align:right; border:1px solid #000; padding:5px">PEDIDO: 004215<br>{datetime.now().strftime('%d/%m/%Y')}</td>
                            </tr></table>
                            <hr><p><b>CLIENTE:</b> {cli}</p>
                            <p><b>ITEM:</b> {prod} | QTD: {qtd}</p>
                            <br><b>VENCIMENTO: {venc}</b><br><br><br>
                            <div style="text-align:center">________________________<br>Assinatura</div>
                        </div>""", unsafe_allow_html=True)

    # --- ABA: CLIENTES (ACORDAR LISTA) ---
    elif menu == "👥 Clientes":
        st.header("Relação de Clientes")
        if not df_c.empty:
            st.dataframe(df_c[['NOM', 'RUA', 'BAI', 'TEL1']], use_container_width=True, hide_index=True)
        else:
            st.info("Lista vazia. Verifique a Carga de Dados.")

    # --- ABA: AJUSTES (CONTROLE TOTAL RECUPERADO) ---
    elif menu == "⚙️ Ajustes":
        st.header("Configurações e Controle")
        with st.form("f_emp"):
            n_e = st.text_input("Empresa", value=emp.get('nome', ''))
            c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": c_e, "end": e_e, "logo_base64": l64}).execute()
                st.success("Dados fixados!"); time.sleep(1); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE RESET (CONTROLE TOTAL)")
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("ZERAR ESTOQUE", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cr2.button("ZERAR CLIENTES", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cr3.button("RESET TOTAL", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()

    # --- ABA: CARGA MASSIVA (DNA ESTABILIZADO) ---
    elif menu == "📂 Carga Massiva":
        st.header("Importação")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("XLSX", type=["xlsx"])
        if arq and st.button("🚀 INICIAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "p_venda": float(pv)}).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', r.get('NOME', ''))),
                            "RUA": str(r.get('RUA', '')), "BAI": str(r.get('BAI', '')),
                            "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importado!"); time.sleep(1); st.rerun()
