import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re
from datetime import datetime

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v60", layout="wide", page_icon="📈")

# --- 2. MOTOR DE RECUPERAÇÃO E SINCRONIA ---
def sincronizar_v60():
    try:
        # Busca Configuração (id=1)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": "", "wts": "", "logo_base64": ""}
        
        # Busca Estoque e Clientes
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("id").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        # Normalização de Clientes: Garante que 'nome_completo' exista para o código não quebrar
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'rua', 'bairro', 'telefone'])
        
        # Se os dados vieram do Siscom (coluna NOM), transcrevemos para nome_completo na memória
        if 'NOM' in df_c.columns and 'nome_completo' in df_c.columns:
            df_c['nome_completo'] = df_c['nome_completo'].fillna(df_c['NOM'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL WINDOWS 11 ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-card {
        background: white; padding: 22px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.3rem; font-weight: bold; color: #0078D4; }
    .paper { background: white; padding: 40px; border: 1px solid #ddd; font-family: monospace; color: black; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = sincronizar_v60()

    with st.sidebar:
        if emp.get('logo_base64'): 
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("SISTEMA", ["🏠 Dashboard", "💰 Vendas & Financeiro", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Carga de Dados", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Gestão Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">CAIXA DIA<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)

    # --- VENDAS (MODELO BÚSSOLA COM PDF) ---
    elif menu == "💰 Vendas & Financeiro":
        st.header("💰 Módulo de Vendas")
        col_v1, col_v2 = st.columns([1, 1])
        with col_v1:
            with st.form("f_venda"):
                cliente_v = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
                prod_v = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                vias = st.radio("Vias de Impressão", ["1 Via", "2 Vias"], horizontal=True)
                btn_pdf = st.form_submit_button("📄 GERAR PRÉVIA DO PEDIDO")
        
        if btn_pdf:
            with col_v2:
                st.subheader("Visualização do Pedido")
                st.markdown(f"""
                <div class="paper">
                    <table style="width:100%">
                        <tr>
                            <td style="width:20%"><img src="{emp.get('logo_base64', '')}" width="70"></td>
                            <td style="text-align:center">
                                <b>{emp.get('nome', 'EMPRESA')}</b><br>
                                CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}
                            </td>
                            <td style="text-align:right; border:1px solid #000; padding:5px">
                                PEDIDO: 001<br>Data: {datetime.now().strftime('%d/%m/%Y')}<br><b>VIA: {vias}</b>
                            </td>
                        </tr>
                    </table>
                    <hr>
                    <p><b>CLIENTE:</b> {cliente_v}</p>
                    <table style="width:100%; border-collapse: collapse;">
                        <tr style="background:#eee"><th>DESCRIÇÃO</th><th>QTD</th><th>TOTAL</th></tr>
                        <tr>
                            <td>{prod_v.split('|')[0]}</td>
                            <td style="text-align:center">{qtd}</td>
                            <td style="text-align:right">{prod_v.split('R$')[1]}</td>
                        </tr>
                    </table>
                    <br><br><br>
                    <div style="text-align:center">________________________________<br>Assinatura</div>
                </div>
                """, unsafe_allow_html=True)

    # --- ESTOQUE (INCLUSÃO MANUAL BLINDADA) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos")
        tab_l, tab_e = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_l: st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_e:
            op_p = ["Novo Cadastro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Produto", op_p)
            it = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("f_p"):
                d = st.text_input("Descrição", value=it['descricao'] if it else "")
                u = st.text_input("Unidade", value=it['unidade'] if it else "UN")
                pr = st.number_input("Preço", value=float(it['preco_venda'] or 0.0) if it else 0.0)
                if st.form_submit_button("💾 SALVAR"):
                    payload = {"descricao": d, "unidade": u, "preco_venda": pr}
                    if it: supabase.table("produtos").update(payload).eq("id", it['id']).execute()
                    else: supabase.table("produtos").insert(payload).execute()
                    st.rerun()

    # --- CLIENTES (O FIM DO API ERROR) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_cl, tab_ce = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_cl:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        with tab_ce:
            op_c = ["Novo Cadastro"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Cliente", op_c)
            cl = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("f_c"):
                n = st.text_input("Nome/Razão", value=cl['nome_completo'] if cl else "")
                ru = st.text_input("Rua", value=cl.get('rua', '') if cl else "")
                ba = st.text_input("Bairro", value=cl.get('bairro', '') if cl else "")
                tl = st.text_input("Telefone", value=cl.get('telefone', '') if cl else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    # MOTOR DE MAPEAMENTO: Tenta salvar em nome_completo e NOM para garantir compatibilidade
                    payload_c = {"nome_completo": n, "rua": ru, "bairro": ba, "telefone": tl}
                    try:
                        if cl: supabase.table("Clientes").update(payload_c).eq("id", cl['id']).execute()
                        else: supabase.table("Clientes").insert(payload_c).execute()
                        st.rerun()
                    except:
                        # Tenta o nome Siscom (NOM) se o padrão falhar
                        payload_c["NOM"] = n
                        if cl: supabase.table("Clientes").update(payload_c).eq("id", cl['id']).execute()
                        else: supabase.table("Clientes").insert(payload_c).execute()
                        st.rerun()

    # --- CARGA DE DADOS (DNA SISCOM) ---
    elif menu == "📑 Carga de Dados":
        st.header("📑 Carga Massiva")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "preco_venda": float(pv)}).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')), "bairro": str(r.get('BAI', '')), "telefone": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES (FIXAÇÃO POR UPSERT BLINDADO) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Empresa e Reset")
        with st.form("f_emp"):
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Nome Empresa", value=emp.get('nome', ''))
            cn_e = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            en_e = st.text_input("Endereço", value=emp.get('end', ''))
            wt_e = st.text_input("WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                # O Segredo da fixação: Upsert com ID fixo 1
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": cn_e, "end": en_e, "wts": wt_e, "logo_base64": l64}).execute()
                st.rerun()
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().neq("id", -1).execute(); st.rerun()
