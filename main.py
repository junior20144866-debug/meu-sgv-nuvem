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

st.set_page_config(page_title="JMQJ SGV v47", layout="wide", page_icon="📈")

# --- 2. MOTOR DE TRATAMENTO DE DADOS (DNA SISCOM/FPQ) ---
def limpar_valor(v):
    try:
        if pd.isna(v) or str(v).strip() == "": return 0.0
        s = str(v).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
        s = re.sub(r'[^0-9.]', '', s)
        return float(s) if s else 0.0
    except: return 0.0

def carregar_dados():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        df_e = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda', 'unidade'])
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        return (conf[0] if conf else {}), df_e, df_c
    except: return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO WINDOWS 11 (ACRYLIC DESIGN) ---
st.markdown("""
    <style>
    .stApp { background-color: #F3F3F3; }
    .win-card {
        background: white; padding: 24px; border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.08); border: 1px solid #E5E5E5;
        text-align: center; transition: 0.3s;
    }
    .win-card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.12); }
    .metric-title { font-size: 0.85rem; color: #5D5D5D; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.4rem; font-weight: 700; color: #0078D4; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR SISTEMA 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_dados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV OPERACIONAL'))
        st.write("---")
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "🛒 Vendas (PDV)", "📦 Estoque & Produtos", "👥 Clientes", "📑 Importação Massiva", "⚙️ Ajustes & Reset"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Gerencial | {emp.get('nome', 'SGV')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-card"><p class="metric-title">Produtos</p><p class="metric-value">{len(df_e)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card"><p class="metric-title">Clientes</p><p class="metric-value">{len(df_c)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card"><p class="metric-title">Vendas Hoje</p><p class="metric-value">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-card"><p class="metric-title">Financeiro</p><p class="metric-value">0,00</p></div>', unsafe_allow_html=True)

    # --- ABA: VENDAS (PDV COM 1 OU 2 VIAS) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Ponto de Venda")
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            st.subheader("Carrinho")
            cli_sel = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor Final"])
            prod_sel = st.selectbox("Produto", [f"{p['id']} - {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Estoque Vazio"])
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            vias = st.radio("Vias de Impressão", ["1 Via", "2 Vias"], horizontal=True)
        with col_v2:
            st.subheader("Totalização")
            st.markdown('<div class="win-card">VALOR TOTAL<br><span class="metric-value">R$ 0,00</span></div>', unsafe_allow_html=True)
            if st.button("✅ FINALIZAR E IMPRIMIR"):
                st.success(f"Venda concluída! Emitindo {vias}...")

    # --- ABA: ESTOQUE (INCLUSÃO MANUAL E EDIÇÃO) ---
    elif menu == "📦 Estoque & Produtos":
        st.header("📦 Gestão de Produtos")
        with st.expander("➕ Inclusão Manual / Edição"):
            with st.form("form_prod"):
                c1, c2, c3 = st.columns([3, 1, 1])
                d = c1.text_input("Descrição do Produto")
                u = c2.text_input("Unidade (Ex: UN, KG)")
                p = c3.number_input("Preço de Venda", format="%.2f")
                if st.form_submit_button("💾 SALVAR PRODUTO"):
                    supabase.table("produtos").insert({"descricao": d, "unidade": u, "preco_venda": p}).execute()
                    st.rerun()
        
        if not df_e.empty:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
            sel_p = st.selectbox("Selecione para Excluir", ["..."] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')])
            if sel_p != "..." and st.button("🗑️ Deletar Produto"):
                supabase.table("produtos").delete().eq("id", int(sel_p.split(" - ")[0])).execute()
                st.rerun()

    # --- ABA: IMPORTAÇÃO (O FIM DO GARGALO) ---
    elif menu == "📑 Importação Massiva":
        st.header("📑 Carga de Dados Inteligente")
        alvo = st.selectbox("Tabela Destino", ["produtos", "Clientes"])
        st.info("Mapeamento automático: DESCRICAO, P_VENDA, NOM, RUA, BAI, CID, UF, CEP.")
        file = st.file_uploader("Suba o arquivo XLSX", type=["xlsx"])
        if file and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(file)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            count = 0
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        desc = r.get('DESCRICAO', r.get('NOME', ''))
                        if pd.notna(desc) and str(desc).strip() != "":
                            pld = {"descricao": str(desc).strip(), "unidade": str(r.get('UNIDADE', 'UN')), "preco_venda": limpar_valor(r.get('P_VENDA', 0))}
                            supabase.table("produtos").insert(pld).execute()
                            count += 1
                    else:
                        nom = r.get('NOM', r.get('NOME', ''))
                        if pd.notna(nom) and str(nom).strip() != "":
                            endereco = f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CEP', '')} {r.get('CID', '')}/{r.get('UF', '')}"
                            pld = {"nome_completo": str(nom).strip(), "cpf_cnpj": str(r.get('CGC', r.get('CPF', ''))), "endereco": endereco}
                            supabase.table("Clientes").insert(pld).execute()
                            count += 1
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success(f"Carga finalizada: {count} registros salvos!"); time.sleep(1.5); st.rerun()

    # --- ABA: AJUSTES & RESET (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Configurações da Empresa & Resets")
        with st.form("f_empresa"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cn = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            end = st.text_input("Endereço (Rua, Bairro, CEP, Cidade, UF)", value=emp.get('end', ''))
            wts = st.text_input("Telefone / WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logomarca (PNG)", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": cn, "end": end, "wts": wts, "logo_base64": l_b64}).execute()
                st.rerun()

        st.divider()
        st.subheader("🛑 ZONA DE RESET CONTROLADO")
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        if col_r1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if col_r2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if col_r3.button("🗑️ Zerar Ajustes"): supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
        if col_r4.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
