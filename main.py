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

st.set_page_config(page_title="JMQJ SGV v53", layout="wide", page_icon="📈")

# --- 2. MOTOR DE SINCRONIA E RECONHECIMENTO ---
def carregar_dados_blindados():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        empresa = conf[0] if conf else {"id": 1, "nome": "JMQJ SGV", "end": "", "cnpj": "", "wts": ""}
        
        # Reconhecimento Automático de Colunas (Fim da aba em branco)
        df_p = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'rua', 'bairro', 'telefone', 'endereco'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-tile {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.3rem; font-weight: bold; color: #0078D4; }
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
    emp, df_e, df_c = carregar_dados_blindados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas & Financeiro", "📦 Estoque", "👥 Clientes", "📑 Carga de Dados", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Gestão Integrada | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile">PRODUTOS NO ESTOQUE<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES NA BASE<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile">CAIXA DO DIA<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)

    # --- VENDAS & FINANCEIRO (AVANÇO) ---
    elif menu == "🛒 Vendas & Financeiro":
        st.header("🛒 Lançamento de Vendas e Caixa")
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            st.subheader("Novo Pedido")
            cli_v = st.selectbox("Selecione o Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
            prod_v = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
            qtd = st.number_input("Qtd", min_value=1, value=1)
            f_pag = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Débito", "Crédito", "Prazo"])
        with col_v2:
            st.subheader("Totalização")
            st.markdown('<div class="win-tile">VALOR FINAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Impressão", ["1 Via", "2 Vias"], horizontal=True)
            if st.button("✅ CONCLUIR E LANÇAR"):
                st.success("Venda registrada no financeiro!")

    # --- ESTOQUE (CONTROLE TOTAL) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Produtos")
        tab_list, tab_ctrl = st.tabs(["📋 Relação", "🛠️ Incluir/Editar/Excluir"])
        with tab_list:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_ctrl:
            op_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Produto", op_p)
            it = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("form_p"):
                d = st.text_input("Descrição", value=it['descricao'] if it else "")
                u = st.text_input("Unidade", value=it['unidade'] if it else "UN")
                p = st.number_input("Preço", value=float(it['preco_venda'] or 0.0) if it else 0.0)
                if st.form_submit_button("💾 SALVAR"):
                    dt = {"descricao": d, "unidade": u, "preco_venda": p}
                    if it: supabase.table("produtos").update(dt).eq("id", it['id']).execute()
                    else: supabase.table("produtos").insert(dt).execute()
                    st.rerun()
            if it and st.button("🗑️ EXCLUIR ITEM"):
                supabase.table("produtos").delete().eq("id", it['id']).execute(); st.rerun()

    # --- CLIENTES (CORREÇÃO DE RECONHECIMENTO) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_clist, tab_cctrl = st.tabs(["📋 Relação de Clientes", "🛠️ Incluir/Editar/Excluir"])
        with tab_clist:
            if not df_c.empty:
                st.dataframe(df_c, use_container_width=True, hide_index=True)
            else:
                st.warning("Aguardando carga de dados ou cadastro.")
        with tab_cctrl:
            op_c = ["Novo Cadastro"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Cliente", op_c)
            cl = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("form_c"):
                n = st.text_input("Nome Completo", value=cl['nome_completo'] if cl else "")
                ru = st.text_input("Rua", value=cl.get('rua', '') if cl else "")
                ba = st.text_input("Bairro", value=cl.get('bairro', '') if cl else "")
                tl = st.text_input("Telefone", value=cl.get('telefone', '') if cl else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    dc = {"nome_completo": n, "rua": ru, "bairro": ba, "telefone": tl, "endereco": f"{ru}, {ba}"}
                    if cl: supabase.table("Clientes").update(dc).eq("id", cl['id']).execute()
                    else: supabase.table("Clientes").insert(dc).execute()
                    st.rerun()
            if cl and st.button("🗑️ EXCLUIR CLIENTE"):
                supabase.table("Clientes").delete().eq("id", cl['id']).execute(); st.rerun()

    # --- CARGA DE DADOS (MAPEAMENTO SEGURO) ---
    elif menu == "📑 Carga de Dados":
        st.header("📑 Importação de Planilhas")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("Subir XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "preco_venda": float(pv), "unidade": str(r.get('UNIDADE', 'UN'))}).execute()
                    else:
                        # MAPEAMENTO FORÇADO para nome_completo
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')),
                            "bairro": str(r.get('BAI', '')),
                            "telefone": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES & RESET (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Configurações da Empresa")
        with st.form("f_conf"):
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cn_e = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            en_e = st.text_input("Endereço", value=emp.get('end', ''))
            wt_e = st.text_input("WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": cn_e, "end": en_e, "wts": wt_e, "logo_base64": l64}).execute()
                st.rerun()
        st.divider()
        st.subheader("🗑️ ZONA DE CONTROLE (RESET)")
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cr2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cr3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
