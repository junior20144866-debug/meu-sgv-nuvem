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

st.set_page_config(page_title="JMQJ SGV SaaS", layout="wide", page_icon="🎯")

# --- 2. MOTOR DE RECUPERAÇÃO (MAPEAMENTO TOTAL DBF) ---
def sincronizar_universo_v75():
    try:
        # Configuração da Empresa (DADOS.DBF)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Produtos (CADASTRO.DBF / ENTRADA2.DBF)
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'p_venda'])
        
        # Clientes (CLIENTES.DBF) - Foco nas colunas NOM, RUA, BAI
        cl = supabase.table("Clientes").select("*").order("id").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'NOM', 'RUA', 'BAI', 'TEL1'])
        
        return empresa, df_p, df_c
    except:
        return {"id": 1, "nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO SAAS MODERNO ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .metric-val { font-size: 2.3rem; font-weight: 700; color: #2563EB; }
    .paper { background: white; padding: 35px; border: 1px solid #000; font-family: monospace; color: black; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 💼")
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("ACESSAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = sincronizar_universo_v75()

    with st.sidebar:
        if emp.get('logo_base64'): 
            try: st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        st.subheader(emp.get('nome', 'JMQJ SGV'))
        st.caption(f"CNPJ: {emp.get('cnpj', '')}")
        st.write("---")
        menu = st.radio("MÓDULOS", ["📊 Painel", "🧾 Vendas & O.S", "📦 Estoque", "👥 Clientes", "📂 Carga Massiva", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "📊 Painel":
        st.header(f"Gestão Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>ITENS CADASTRADOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES ATIVOS<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>CAIXA DIA<br><span class='metric-val'>R$ 0,00</span></div>", unsafe_allow_html=True)

    # --- ABA: VENDAS (HERANÇA DO ORDEM.DBF) ---
    elif menu == "🧾 Vendas & O.S":
        st.header("Lançamento de Vendas e Serviços")
        col1, col2 = st.columns([1, 1.3])
        with col1:
            with st.form("v_form"):
                cli = st.selectbox("Cliente (NOM)", df_c['NOM'].tolist() if not df_c.empty else ["Vazio"])
                prod = st.selectbox("Item", [f"{p['descricao']} | R$ {p['p_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                prazo = st.number_input("Prazo p/ Vencimento (Dias)", min_value=0, value=30)
                if st.form_submit_button("📄 GERAR DOCUMENTO"):
                    venc = (datetime.now() + timedelta(days=prazo)).strftime('%d/%m/%Y')
                    with col2:
                        st.markdown(f"""
                        <div class="paper">
                            <table style="width:100%"><tr>
                            <td><img src="{emp.get('logo_base64', '')}" width="80"></td>
                            <td style="text-align:center"><b>{emp.get('nome', '')}</b><br>CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}</td>
                            <td style="text-align:right; border:1px solid #000; padding:5px">PEDIDO: {datetime.now().strftime('%M%S')}<br>{datetime.now().strftime('%d/%m/%Y')}</td>
                            </tr></table>
                            <hr><p><b>CLIENTE:</b> {cli}</p>
                            <table style="width:100%"><tr><th>DESCRIÇÃO</th><th>QTD</th><th>TOTAL</th></tr>
                            <tr><td>{prod.split('|')[0]}</td><td>{qtd}</td><td>{prod.split('R$')[1]}</td></tr>
                            </table><br>
                            <div style="text-align:left"><b>TOTAL: R$ {float(prod.split('R$')[1].replace(',','.'))*qtd:,.2f}</b><br>Vencimento: {venc}</div>
                            <br><br><div style="text-align:center">________________________<br>Assinatura</div>
                        </div>""", unsafe_allow_html=True)

    # --- ABA: CLIENTES (MAPEADO NOM) ---
    elif menu == "👥 Clientes":
        st.header("Base de Clientes")
        if not df_c.empty:
            st.dataframe(df_c[['NOM', 'RUA', 'BAI', 'TEL1']], use_container_width=True, hide_index=True)
        else:
            st.info("Aguardando importação de dados.")

    # --- ABA: CARGA MASSIVA (DNA ESTABILIZADO) ---
    elif menu == "📂 Carga Massiva":
        st.header("Importação de Dados")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "p_venda": float(pv), "unidade": str(r.get('UNIDADE', 'UN'))}).execute()
                    else:
                        # Mapeamento DNA: NOM, RUA, BAI
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', r.get('NOME', ''))),
                            "RUA": str(r.get('RUA', '')), "BAI": str(r.get('BAI', '')),
                            "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES (FIXAÇÃO DE AÇO) ---
    elif menu == "⚙️ Ajustes":
        st.header("Configurações do Sistema")
        with st.form("f_emp"):
            n_e = st.text_input("Empresa", value=emp.get('nome', ''))
            c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Trocar Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": c_e, "end": e_e, "logo_base64": l64}).execute()
                st.success("Dados cravados!"); time.sleep(1); st.rerun()
        
        st.divider()
        if st.button("🔥 RESET TOTAL DO SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
