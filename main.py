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

st.set_page_config(page_title="JMQJ SGV v61", layout="wide", page_icon="📈")

# --- 2. MOTOR DE RECUPERAÇÃO ---
def carregar_sistema_v61():
    try:
        c = supabase.table("config").select("*").execute().data
        empresa = c[0] if c else {"id": None, "nome": "JMQJ SGV", "cnpj": "", "end": "", "wts": "", "logo_base64": ""}
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'rua', 'bairro', 'telefone', 'endereco'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 5px solid #0078D4; text-align: center; }
    .metric-val { font-size: 2.3rem; font-weight: bold; color: #0078D4; }
    .paper { background: white; padding: 30px; border: 1px solid #000; font-family: 'Courier New', Courier, monospace; color: black; line-height: 1.1; }
    .divider-dotted { border-top: 1px dotted #000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_sistema_v61()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        menu = st.radio("SISTEMA", ["🏠 Dashboard", "💰 Vendas & Financeiro", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Carga de Dados", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Gestão Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">PEDIDOS HOJE<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- VENDAS & FINANCEIRO (MODELO BÚSSOLA REFINADO) ---
    elif menu == "💰 Vendas & Financeiro":
        st.header("💰 Lançamento de Pedidos")
        col_v1, col_v2 = st.columns([1, 1])
        with col_v1:
            with st.form("f_venda"):
                cliente_sel = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
                prod_sel = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Sem Produtos"])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                prazo = st.number_input("Prazo de Vencimento (Dias)", min_value=0, value=30)
                vias = st.radio("Impressão", ["1", "2"], horizontal=True)
                btn_pdf = st.form_submit_button("📄 GERAR PRÉVIA DO PEDIDO")
        
        if btn_pdf:
            vencimento = (datetime.now() + timedelta(days=prazo)).strftime('%d/%m/%Y')
            with col_v2:
                st.subheader("Visualização do Pedido")
                st.markdown(f"""
                <div class="paper">
                    <table style="width:100%">
                        <tr>
                            <td style="width:20%"><img src="{emp.get('logo_base64', '')}" width="80"></td>
                            <td style="text-align:center">
                                <b style="font-size:18px">{emp.get('nome', 'EMPRESA')}</b><br>
                                CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}<br>{emp.get('wts', '')}
                            </td>
                            <td style="text-align:right; border:1px solid #000; padding:5px">
                                <b>PEDIDO: 004215</b><br>Data: {datetime.now().strftime('%d/%m/%Y')}<br>Venc: {vencimento}<br><b>{vias}</b>
                            </td>
                        </tr>
                    </table>
                    <div class="divider-dotted"></div>
                    <p><b>CLIENTE:</b> {cliente_sel}</p>
                    <table style="width:100%; text-align:left">
                        <tr style="border-bottom: 1px solid #000"><th>DESCRIÇÃO DO ITEM</th><th>UNI</th><th>VALOR</th><th>QTD</th><th>TOTAL</th></tr>
                        <tr>
                            <td>{prod_sel.split('|')[0]}</td><td>PC</td><td>{prod_sel.split('R$')[1]}</td><td>{qtd}</td><td>{float(prod_sel.split('R$')[1].replace(',','.'))*qtd:,.2f}</td>
                        </tr>
                    </table>
                    <br><br>
                    <div style="display: flex; justify-content: space-between;">
                        <div><b>CONDIÇÕES DE PAGAMENTO:</b><br>À vista - {datetime.now().strftime('%d/%m/%Y')}</div>
                        <div style="text-align:right"><b>VALOR TOTAL: R$ {float(prod_sel.split('R$')[1].replace(',','.'))*qtd:,.2f}</b></div>
                    </div>
                    <br><br><br>
                    <div style="text-align:center">________________________________<br>Assinatura</div>
                </div>
                """, unsafe_allow_html=True)

    # --- ESTOQUE (PRODUTOS OK) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos")
        tab_list, tab_edit = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_list: st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_edit:
            op_p = ["Novo Cadastro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Produto", op_p)
            it = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("form_p"):
                d = st.text_input("Descrição", value=it['descricao'] if it else "")
                u = st.text_input("Unidade", value=it['unidade'] if it else "UN")
                p = st.number_input("Preço", value=float(it['preco_venda'] or 0.0) if it else 0.0)
                if st.form_submit_button("💾 SALVAR"):
                    payload = {"descricao": d, "unidade": u, "preco_venda": p}
                    if it: supabase.table("produtos").update(payload).eq("id", it['id']).execute()
                    else: supabase.table("produtos").insert(payload).execute()
                    st.rerun()

    # --- CLIENTES (BLINDAGEM CONTRA API ERROR) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_cl, tab_ce = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_cl:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        with tab_ce:
            op_c = ["Novo Cadastro"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Cliente", op_c)
            cl = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("form_cli"):
                n = st.text_input("Nome/Razão", value=cl['nome_completo'] if cl else "")
                ru = st.text_input("Rua", value=cl.get('rua', '') if cl else "")
                ba = st.text_input("Bairro", value=cl.get('bairro', '') if cl else "")
                tl = st.text_input("Telefone", value=cl.get('telefone', '') if cl else "")
                if st.form_submit_button("💾 SALVAR"):
                    # MOTOR BLINDADO: Envia endereço completo para evitar rejeição do banco
                    dados_c = {"nome_completo": n, "rua": ru, "bairro": ba, "telefone": tl, "endereco": f"{ru}, {ba}"}
                    try:
                        if cl: supabase.table("Clientes").update(dados_c).eq("id", cl['id']).execute()
                        else: supabase.table("Clientes").insert(dados_c).execute()
                        st.rerun()
                    except Exception as e: st.error(f"Erro de Banco de Dados: {e}")

    # --- CARGA (DNA SISCOM) ---
    elif menu == "📑 Carga de Dados":
        st.header("📑 Importação Massiva")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("Subir XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "preco_venda": float(pv)}).execute()
                    else:
                        # Mapeamento do seu Excel CLIENTES.xlsx (NOM, RUA, BAI, TEL1)
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')), "bairro": str(r.get('BAI', '')), 
                            "telefone": str(r.get('TEL1', '')), "endereco": f"{r.get('RUA','')}, {r.get('BAI','')}"
                        }).execute()
                except: pass
            st.success("Importado!"); time.sleep(1); st.rerun()

    # --- AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Empresa e Reset")
        with st.form("form_emp"):
            nome_e = st.text_input("Nome Empresa", value=emp.get('nome', ''))
            cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_e = st.text_input("Endereço", value=emp.get('end', ''))
            wts_e = st.text_input("WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                payload_e = {"nome": nome_e, "cnpj": cnpj_e, "end": end_e, "wts": wts_e, "logo_base64": l64}
                try:
                    # Tenta atualizar o primeiro registro, se não houver, insere
                    if emp.get('id'): supabase.table("config").update(payload_e).eq("id", emp['id']).execute()
                    else: supabase.table("config").insert(payload_e).execute()
                    st.rerun()
                except Exception as e: st.error(f"Erro ao fixar: {e}")
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().neq("id", -1).execute(); st.rerun()
