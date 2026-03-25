import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re
from datetime import datetime, timedelta

# --- 1. CONEXÃO MESTRA (ESTABILIZADA) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SaaS", layout="wide", page_icon="🚀")

# --- 2. MOTOR DE SINCRONIZAÇÃO (ANTI-SANFONA) ---
def sincronizar_dados():
    try:
        # Busca Empresa (id=1)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": "", "logo_base64": ""}
        
        # Busca Produtos e Clientes
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        
        # O FIM DO GARGALHO DOS CLIENTES: Mapeamento de DNA forçado na leitura
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'rua', 'bairro', 'telefone'])
        if not df_c.empty and 'NOM' in df_c.columns:
            df_c['nome_completo'] = df_c['nome_completo'].fillna(df_c['NOM'])
            
        return empresa, df_p, df_c
    except:
        return {"id": 1, "nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO SAAS MODERNO (Inspirado em NFEmail) ---
st.markdown("""
    <style>
    .stApp { background-color: #F9FAFB; }
    .main-header { color: #111827; font-weight: 800; font-size: 2rem; margin-bottom: 1.5rem; }
    .card { background: white; padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .metric-val { font-size: 2rem; font-weight: 700; color: #2563EB; }
    .paper-invoice { background: white; padding: 40px; border: 1px solid #D1D5DB; font-family: 'Inter', sans-serif; color: #111827; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE NAVEGAÇÃO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h1 style='text-align: center;'>JMQJ SGV</h1>", unsafe_allow_html=True)
        senha = st.text_input("Acesso Mestre", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = sincronizar_dados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        st.write("---")
        menu = st.radio("MENU", ["📊 Painel", "🧾 Vendas & NF", "📦 Estoque", "👥 Clientes", "📂 Importação", "⚙️ Ajustes"])

    # --- DASHBOARD ---
    if menu == "📊 Painel":
        st.markdown(f"<div class='main-header'>Olá, {emp.get('nome')}</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>FATURAMENTO<br><span class='metric-val'>R$ 0,00</span></div>", unsafe_allow_html=True)

    # --- VENDAS & FINANCEIRO (ESTILO SAAS) ---
    elif menu == "🧾 Vendas & NF":
        st.header("Lançamento de Vendas")
        c_v1, c_v2 = st.columns([1, 1.2])
        with c_v1:
            with st.form("f_venda"):
                sel_cli = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor Padrão"])
                sel_prod = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
                qtd = st.number_input("Qtd", min_value=1, value=1)
                prazo = st.number_input("Prazo de Vencimento (Dias)", min_value=0, value=30)
                vias = st.radio("Vias de Impressão", ["1", "2"], horizontal=True)
                if st.form_submit_button("GERAR DOCUMENTO"):
                    st.session_state.venc = (datetime.now() + timedelta(days=prazo)).strftime('%d/%m/%Y')
                    st.session_state.print_ready = True
        
        if st.session_state.get('print_ready'):
            with c_v2:
                st.markdown(f"""
                <div class="paper-invoice">
                    <table style="width:100%"><tr>
                        <td style="width:25%"><img src="{emp.get('logo_base64', '')}" width="100"></td>
                        <td style="text-align:center"><b>{emp.get('nome', 'EMPRESA')}</b><br>CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}</td>
                        <td style="text-align:right; border:1px solid #000; padding:10px">PEDIDO: #4215<br>Vencimento: {st.session_state.venc}<br><b>CÓPIA {vias}</b></td>
                    </tr></table>
                    <hr>
                    <p><b>CLIENTE:</b> {sel_cli}</p>
                    <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
                        <tr style="background:#F3F4F6"><th>DESCRIÇÃO</th><th>QTD</th><th>TOTAL</th></tr>
                        <tr><td>{sel_prod.split('|')[0]}</td><td style="text-align:center">{qtd}</td><td style="text-align:right">{sel_prod.split('R$')[1]}</td></tr>
                    </table>
                    <div style="text-align:right; margin-top:20px; font-size:1.5rem"><b>TOTAL: R$ {float(sel_prod.split('R$')[1].replace(',','.'))*qtd:,.2f}</b></div>
                    <br><br><div style="text-align:center; border-top:1px solid #000; padding-top:10px">Assinatura do Recebedor</div>
                </div>
                """, unsafe_allow_html=True)

    # --- CLIENTES (FIXAÇÃO E DESPERTAR TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("Base de Clientes")
        t1, t2 = st.tabs(["📋 Relação Ativa", "➕ Novo Cadastro"])
        with t1:
            if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)
            else: st.info("Nenhum cliente na base.")
        with t2:
            with st.form("f_cli"):
                n = st.text_input("Nome/Razão Social")
                r = st.text_input("Logradouro (Rua)")
                b = st.text_input("Bairro")
                if st.form_submit_button("SALVAR"):
                    pld = {"nome_completo": n, "rua": r, "bairro": b, "endereco": f"{r}, {b}"}
                    supabase.table("Clientes").insert(pld).execute()
                    st.rerun()

    # --- CARGA MASSIVA (DNA ESTABILIZADO) ---
    elif menu == "📂 Importação":
        st.header("Carga de Dados em Massa")
        alvo = st.selectbox("Escolha o destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba seu arquivo Excel (.xlsx)", type=["xlsx"])
        if arq and st.button("INICIAR IMPORTAÇÃO"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "preco_venda": float(pv), "unidade": str(r.get('UNIDADE', 'UN'))}).execute()
                    else:
                        # MAPEAMENTO FORÇADO DO DNA: NOM vira nome_completo
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')), "bairro": str(r.get('BAI', '')),
                            "endereco": f"{r.get('RUA','')}, {r.get('BAI','')}"
                        }).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES & RESET (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("Identidade da Empresa e Sistema")
        with st.form("f_emp"):
            nome_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_e = st.text_input("Endereço Completo", value=emp.get('end', ''))
            logo = st.file_uploader("Logomarca (PNG)", type=["png"])
            if st.form_submit_button("FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": nome_e, "cnpj": cnpj_e, "end": end_e, "logo_base64": l64}).execute()
                st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE CONTROLE TOTAL (RESET)")
        c1, c2, c3 = st.columns(3)
        if c1.button("ZERAR ESTOQUE", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("ZERAR CLIENTES", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("RESET TOTAL", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
