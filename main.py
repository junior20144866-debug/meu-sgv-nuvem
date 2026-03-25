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

# --- 2. MOTOR DE SINCRONIA (DNA DA BÚSSOLA) ---
def sincronizar_v70():
    try:
        # Busca Empresa
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": "", "logo_base64": ""}
        
        # Busca Produtos (Usa P_VENDA conforme sua tabela)
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'p_venda'])
        
        # Busca Clientes (Usa NOM conforme sua tabela)
        cl = supabase.table("Clientes").select("*").order("NOM").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'NOM', 'RUA', 'BAI', 'TEL1', 'CPF'])
        
        return empresa, df_p, df_c
    except:
        return {"id": 1, "nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO SAAS MODERNO ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .metric-val { font-size: 2rem; font-weight: 700; color: #2563EB; }
    .paper { background: white; padding: 30px; border: 1px solid #000; font-family: monospace; color: black; }
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
    emp, df_e, df_c = sincronizar_v70()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("MENU", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Carga Massiva", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "📊 Painel":
        st.header(f"Painel: {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>CAIXA DIA<br><span class='metric-val'>R$ 0,00</span></div>", unsafe_allow_html=True)

    # --- ABA: VENDAS (LAYOUT BÚSSOLA) ---
    elif menu == "💰 Vendas":
        st.header("Lançamento de Vendas")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("venda_form"):
                cli = st.selectbox("Cliente", df_c['NOM'].tolist() if not df_c.empty else ["Carga Pendente"])
                prod = st.selectbox("Produto", [f"{p['descricao']} | R$ {p.get('p_venda', 0)}" for p in df_e.to_dict('records')] if not df_e.empty else ["Carga Pendente"])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                prazo = st.number_input("Prazo p/ Vencimento (Dias)", min_value=0, value=30)
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
                            <table style="width:100%"><tr><th>DESCRIÇÃO</th><th>QTD</th><th>TOTAL</th></tr>
                            <tr><td>{prod.split('|')[0]}</td><td>{qtd}</td><td>{prod.split('|')[1]}</td></tr>
                            </table><br><b>VENCIMENTO: {venc}</b><br><br><br>
                            <div style="text-align:center">________________________<br>Assinatura</div>
                        </div>""", unsafe_allow_html=True)

    # --- ABA: CLIENTES (ACORDAR LISTA) ---
    elif menu == "👥 Clientes":
        st.header("Base de Clientes")
        tab1, tab2 = st.tabs(["📋 Relação", "➕ Manual"])
        with tab1:
            st.dataframe(df_c[['NOM', 'RUA', 'BAI', 'TEL1']], use_container_width=True, hide_index=True)
        with tab2:
            with st.form("novo_cli"):
                n = st.text_input("Nome (NOM)")
                r = st.text_input("Rua (RUA)")
                b = st.text_input("Bairro (BAI)")
                t = st.text_input("Telefone (TEL1)")
                if st.form_submit_button("SALVAR"):
                    # Não enviamos ID, deixamos o banco decidir
                    supabase.table("Clientes").insert({"NOM": n, "RUA": r, "BAI": b, "TEL1": t}).execute()
                    st.rerun()

    # --- ABA: ESTOQUE ---
    elif menu == "📦 Estoque":
        st.header("Estoque")
        st.dataframe(df_e[['descricao', 'unidade', 'p_venda']], use_container_width=True, hide_index=True)

    # --- ABA: CARGA MASSIVA ---
    elif menu == "📂 Carga Massiva":
        st.header("Carga Massiva Inteligente")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Excel (.xlsx)", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "p_venda": float(pv), "unidade": str(r.get('UNIDADE', 'UN'))}).execute()
                    else:
                        # Mapeamento DNA: Busca qualquer variação de nome na sua planilha
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', r.get('NOME', ''))),
                            "RUA": str(r.get('RUA', '')), "BAI": str(r.get('BAI', '')),
                            "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importado!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("Empresa e Reset")
        with st.form("f_emp"):
            n_e = st.text_input("Nome", value=emp.get('nome', ''))
            cn_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            en_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": cn_e, "end": en_e, "logo_base64": l64}).execute()
                st.rerun()
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("ZERAR ESTOQUE", use_container_width=True): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("ZERAR CLIENTES", use_container_width=True): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("RESET TOTAL", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
