import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v39", layout="wide", page_icon="💼")

# --- 2. MOTOR DE BUSCA (FORÇA BRUTA - SEM CACHE) ---
def buscar_dados_vivos():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        # Blindagem de Dataframe
        df_e = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_e['preco_venda'] = pd.to_numeric(df_e['preco_venda'], errors='coerce').fillna(0.0)
        
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        
        return (conf[0] if conf else {}), df_e, df_c
    except Exception as e:
        return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .paper { background: white; padding: 30px; border: 1px solid #ddd; font-family: monospace; }
    .win-tile { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-top: 4px solid #0078D4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ACESSO ---
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

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile">PRODUTOS NO BANCO<br><b style="font-size:25px">{len(df_e)}</b></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES NO BANCO<br><b style="font-size:25px">{len(df_c)}</b></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile">PEDIDOS GERAIS<br><b style="font-size:25px">0</b></div>', unsafe_allow_html=True)

    # --- ABA: PEDIDO DE VENDA (LAYOUT SISCOM) ---
    elif menu == "🛒 Pedido de Venda":
        st.header("🛒 Lançamento de Pedido")
        col_v1, col_v2 = st.columns([1, 1])
        with col_v1:
            with st.form("venda_f"):
                c_sel = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
                p_sel = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Estoque Vazio"])
                qtd = st.number_input("Qtd", min_value=1, value=1)
                vias = st.radio("Vias", ["1 Via", "2 Vias"], horizontal=True)
                if st.form_submit_button("📄 GERAR PRÉVIA DO PEDIDO"):
                    st.session_state.venda_preview = {"c": c_sel, "p": p_sel, "q": qtd, "v": vias}

        if 'venda_preview' in st.session_state:
            with col_v2:
                vp = st.session_state.venda_preview
                st.markdown(f"""
                <div class="paper">
                    <div style="display: flex; justify-content: space-between;">
                        <img src="{emp.get('logo_base64', '')}" width="60">
                        <div style="text-align: center;"><b>{emp.get('nome', '')}</b><br>{emp.get('end', '')}</div>
                        <div style="border: 1px solid #000; padding: 5px;">PEDIDO 001<br>VIA: {vp['v']}</div>
                    </div>
                    <hr>
                    <p><b>CLIENTE:</b> {vp['c']}</p>
                    <table style="width:100%">
                        <tr><th>DESCRIÇÃO</th><th>QTD</th><th>TOTAL</th></tr>
                        <tr><td>{vp['p'].split('|')[0]}</td><td style="text-align:center">{vp['q']}</td><td style="text-align:right">{vp['p'].split('R$')[1]}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

    # --- ABA: ESTOQUE (PRODUTOS) ---
    elif menu == "📦 Estoque":
        st.header("📦 Relação de Itens")
        if not df_e.empty:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
            sel = st.selectbox("Ação por ID", ["Selecione..."] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')])
            if sel != "Selecione..." and st.button("🗑️ DELETAR"):
                supabase.table("produtos").delete().eq("id", int(sel.split(" - ")[0])).execute(); st.rerun()
        else: st.info("Estoque vazio. Aguardando Importação.")

    # --- ABA: IMPORTAÇÃO (RECALIBRADA ANTI-ERRO) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga Massiva Inteligente")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 INICIAR CARGA"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        # LIMPEZA AGRESSIVA: Remove R$, espaços, pontos de milhar e troca vírgula por ponto
                        p_limpo = str(r.get('P_VENDA', 0)).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
                        pld = {"descricao": str(r.get('DESCRICAO')), "preco_venda": float(p_limpo), "ean13": str(r.get('CODIGO'))}
                    else:
                        pld = {"nome_completo": str(r.get('NOM')), "cpf_cnpj": str(r.get('CGC')), "endereco": str(r.get('RUA'))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
            st.success("Carga Finalizada!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES (RESETS) ---
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
