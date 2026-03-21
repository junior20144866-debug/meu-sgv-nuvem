import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime
import re

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v40", layout="wide", page_icon="💼")

# --- 2. MOTOR DE LIMPEZA DE PREÇOS (O FIM DA INCOMPATIBILIDADE) ---
def limpar_valor_monetario(valor):
    if pd.isna(valor) or valor == "": return 0.0
    # Remove R$, espaços e pontos de milhar, troca vírgula por ponto
    texto = str(valor).replace('R$', '').replace(' ', '').strip()
    if ',' in texto and '.' in texto: # Caso como 1.250,00
        texto = texto.replace('.', '').replace(',', '.')
    elif ',' in texto: # Caso como 10,00
        texto = texto.replace(',', '.')
    # Mantém apenas números e o ponto decimal
    texto = re.sub(r'[^0-9.]', '', texto)
    try: return float(texto)
    except: return 0.0

# --- 3. SINCRONIA TOTAL SEM CACHE ---
def buscar_dados_vivos():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_e = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_e['preco_venda'] = pd.to_numeric(df_e['preco_venda'], errors='coerce').fillna(0.0)
        
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        return (conf[0] if conf else {}), df_e, df_c
    except: return {}, pd.DataFrame(), pd.DataFrame()

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-top: 4px solid #0078D4; text-align: center; }
    .paper { background: white; padding: 30px; border: 1px solid #ddd; font-family: monospace; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("ATIVAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = buscar_dados_vivos()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Pedido de Venda", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile">PRODUTOS NO BANCO<br><b style="font-size:25px">{len(df_e)}</b></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES NO BANCO<br><b style="font-size:25px">{len(df_c)}</b></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile">PEDIDOS GERAIS<br><b style="font-size:25px">0</b></div>', unsafe_allow_html=True)

    # --- IMPORTAÇÃO (MOTOR ULTRA-LIMPEZA) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga Massiva Inteligente")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 INICIAR CARGA"):
            df_in = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        p_limpo = limpar_valor_monetario(r.get('P_VENDA', 0))
                        pld = {"descricao": str(r.get('DESCRICAO')), "preco_venda": p_limpo, "ean13": str(r.get('CODIGO'))}
                    else:
                        pld = {"nome_completo": str(r.get('NOM')), "cpf_cnpj": str(r.get('CGC')), "endereco": str(r.get('RUA'))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success("Carga Finalizada!"); time.sleep(1); st.rerun()

    # --- ESTOQUE (PRODUTOS) ---
    elif menu == "📦 Estoque":
        st.header("📦 Relação de Itens")
        if not df_e.empty:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
            sel = st.selectbox("Excluir por ID", ["Selecione..."] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')])
            if sel != "Selecione..." and st.button("🗑️ DELETAR"):
                supabase.table("produtos").delete().eq("id", int(sel.split(" - ")[0])).execute(); st.rerun()
        else: st.info("Estoque vazio ou em branco.")

    # --- CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        if not df_c.empty:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        else: st.info("Nenhum cliente cadastrado.")

    # --- AJUSTES (RESETS) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações e Manutenção")
        with st.form("f_adj"):
            n = st.text_input("Nome", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute(); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE RESET (Limpeza Total)")
        c1, c2, c3 = st.columns(3)
        if c1.button("🗑️ ZERAR ESTOQUE"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("👥 ZERAR CLIENTES"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
