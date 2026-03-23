import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re
from datetime import datetime, timedelta

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v66", layout="wide", page_icon="📈")

# --- 2. MOTOR DE RECUPERAÇÃO (ESTABILIZADOR DE DADOS) ---
def carregar_universo_v66():
    try:
        # Busca Empresa (id=1)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": "", "logo_base64": ""}
        
        # Busca Produtos
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        
        # Busca Clientes com Mapeamento de DNA (Para "Acordar" a lista)
        cl = supabase.table("Clientes").select("*").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'rua', 'bairro', 'telefone', 'endereco'])
        
        if not df_c.empty:
            # Se a carga veio com 'NOM' (padrão Siscom), espelhamos para 'nome_completo'
            if 'NOM' in df_c.columns:
                df_c['nome_completo'] = df_c['nome_completo'].fillna(df_c['NOM'])
                if 'nome_completo' not in df_c.columns: df_c['nome_completo'] = df_c['NOM']
        
        return empresa, df_p, df_c
    except:
        return {"id": 1, "nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL WINDOWS 11 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4; text-align: center; }
    .metric-val { font-size: 2.3rem; font-weight: bold; color: #0078D4; }
    .paper { background: white; padding: 35px; border: 1px solid #000; font-family: 'Courier New', Courier, monospace; color: black; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR SISTEMA 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_universo_v66()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "💰 Vendas & Financeiro", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Carga de Dados", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">VENDAS HOJE<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- VENDAS & FINANCEIRO (MODELO BÚSSOLA) ---
    elif menu == "💰 Vendas & Financeiro":
        st.header("💰 Lançamento de Vendas")
        col_v1, col_v2 = st.columns([1, 1.3])
        with col_v1:
            with st.form("f_venda"):
                cliente_v = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
                prod_v = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                prazo = st.number_input("Prazo p/ Vencimento (Dias)", min_value=0, value=30)
                vias = st.radio("Vias", ["1", "2"], horizontal=True)
                btn_pdf = st.form_submit_button("📄 GERAR PEDIDO")
        
        if btn_pdf:
            venc = (datetime.now() + timedelta(days=prazo)).strftime('%d/%m/%Y')
            total_v = float(prod_v.split('R$')[1].replace(',','.')) * qtd
            with col_v2:
                st.markdown(f"""
                <div class="paper">
                    <table style="width:100%"><tr>
                        <td style="width:20%"><img src="{emp.get('logo_base64', '')}" width="80"></td>
                        <td style="text-align:center"><b>{emp.get('nome', 'EMPRESA')}</b><br>CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}</td>
                        <td style="text-align:right; border:1px solid #000; padding:5px">PEDIDO: 004215<br>{datetime.now().strftime('%d/%m/%Y')}<br><b>{vias}</b></td>
                    </tr></table>
                    <hr>
                    <p><b>CLIENTE:</b> {cliente_v}</p>
                    <table style="width:100%; border-bottom: 1px solid #000">
                        <tr><th>DESCRIÇÃO</th><th style="text-align:center">QTD</th><th style="text-align:right">TOTAL</th></tr>
                        <tr><td>{prod_v.split('|')[0]}</td><td style="text-align:center">{qtd}</td><td style="text-align:right">{prod_v.split('R$')[1]}</td></tr>
                    </table>
                    <br>
                    <div style="text-align:left">
                        <b>VALOR TOTAL: R$ {total_v:,.2f}</b><br>
                        Vencimento: {venc}
                    </div>
                    <br><br><br>
                    <div style="text-align:center">
                        __________________________________________<br>
                        ASSINATURA / RECEBEMOS O PEDIDO ACIMA
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- CLIENTES (CONTROLE TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab1, tab2 = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab1: st.dataframe(df_c, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("f_cli"):
                n = st.text_input("Nome/Razão")
                ru = st.text_input("Rua")
                ba = st.text_input("Bairro")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    payload = {"nome_completo": n, "rua": ru, "bairro": ba, "endereco": f"{ru}, {ba}"}
                    supabase.table("Clientes").insert(payload).execute()
                    st.rerun()

    # --- CARGA DE DADOS (DNA SISCOM) ---
    elif menu == "📑 Carga de Dados":
        st.header("📑 Importação de Dados")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "preco_venda": float(pv)}).execute()
                    else:
                        # Mapeamento do DNA: NOM para nome_completo
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')), "bairro": str(r.get('BAI', '')),
                            "endereco": f"{r.get('RUA','')}, {r.get('BAI','')}"
                        }).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES (CONTROLE TOTAL REPOSTO) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Empresa e Controle Total")
        with st.form("f_emp"):
            nome_e = st.text_input("Empresa", value=emp.get('nome', ''))
            cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": nome_e, "cnpj": cnpj_e, "end": end_e, "logo_base64": l64}).execute()
                st.success("Dados fixados!"); time.sleep(1); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE RESET (CONTROLE TOTAL)")
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("🗑️ Zerar Estoque", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cr2.button("👥 Zerar Clientes", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cr3.button("🔥 RESET TOTAL DO SISTEMA", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
