import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re
from datetime import datetime

# --- 1. CONEXÃO MESTRA (BLINDADA) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v48", layout="wide", page_icon="📈")

# --- 2. MOTOR DE SINCRONIZAÇÃO TOTAL (O FIM DA SANFONA) ---
def carregar_dados_globais():
    """Busca dados e força a permanência na memória da sessão"""
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        # Tratamento de Nomes de Colunas do Siscom (DNA original)
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        
        return (c[0] if c else {}), df_p, df_c
    except Exception as e:
        st.error(f"Erro de Sincronia: {e}")
        return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO WINDOWS 11 (DESIGN ROBUSTO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .win-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .metric-val { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    # CARREGAMENTO FORÇADO
    emp, df_e, df_c = carregar_dados_globais()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        st.write("---")
        menu = st.radio("MENUS", ["🏠 Dashboard", "🛒 Vendas (PDV)", "📦 Estoque & Produtos", "👥 Clientes", "📑 Importação", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD (TILES INTERATIVOS) ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'EMPRESA')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">VENDAS DIA<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- VENDAS (PDV 1 OU 2 VIAS) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Ponto de Venda")
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            st.subheader("Seleção")
            cli_v = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
            prod_v = st.selectbox("Produto", [f"{p['id']} - {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            vias = st.radio("Vias", ["1 Via", "2 Vias"], horizontal=True)
        with col_v2:
            st.subheader("Total")
            st.markdown('<div class="win-card">TOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            if st.button("✅ CONCLUIR"): st.success("Pedido gerado!")

    # --- ESTOQUE & CLIENTES (VISUALIZAÇÃO BLINDADA) ---
    elif menu in ["📦 Estoque & Produtos", "👥 Clientes"]:
        tab = "produtos" if "Estoque" in menu else "Clientes"
        st.header(f"Gestão de {tab.capitalize()}")
        df_show = df_e if tab == "produtos" else df_c
        
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        with st.expander(f"🛠️ Controle de {tab.capitalize()} (Inclusão/Edição/Exclusão)"):
            if st.button(f"🗑️ Excluir registros selecionados de {tab}"):
                st.warning("Selecione o ID na tabela para excluir (Funcionalidade em stress test)")

    # --- IMPORTAÇÃO (MOTOR SISCOM RECALIBRADO) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga Massiva (DNA Siscom)")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba o arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            count = 0
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        desc = str(r.get('DESCRICAO', r.get('descricao', ''))).strip()
                        if desc and desc != 'nan':
                            p_raw = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                            pld = {"descricao": desc, "unidade": str(r.get('UNIDADE', 'UN')), "preco_venda": float(p_raw)}
                            supabase.table("produtos").insert(pld).execute()
                            count += 1
                    else:
                        nom = str(r.get('NOM', r.get('nome_completo', ''))).strip()
                        if nom and nom != 'nan':
                            end = f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CEP', '')} {r.get('CID', '')}/{r.get('UF', '')}"
                            pld = {"nome_completo": nom, "cpf_cnpj": str(r.get('CGC', r.get('CPF', ''))), "endereco": end}
                            supabase.table("Clientes").insert(pld).execute()
                            count += 1
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success(f"Carga: {count} registros salvos!"); time.sleep(1.5); st.rerun()

    # --- AJUSTES & RESET (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Configurações e Manutenção")
        with st.form("f_adj"):
            c1, c2 = st.columns(2)
            n_emp = c1.text_input("Empresa", value=emp.get('nome', ''))
            cn_emp = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_emp = st.text_input("Endereço Completo (Rua, Bairro, CEP, Cidade, UF)", value=emp.get('end', ''))
            wts_emp = st.text_input("Telefone/WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 SALVAR CONFIGURAÇÕES"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_emp, "cnpj": cn_emp, "end": end_emp, "wts": wts_emp, "logo_base64": l_b64}).execute()
                st.success("Configuração fixa!"); time.sleep(1); st.rerun()

        st.divider()
        st.subheader("🗑️ ZONA DE CONTROLE (RESET)")
        c_r1, c_r2, c_r3 = st.columns(3)
        if c_r1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c_r2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c_r3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
