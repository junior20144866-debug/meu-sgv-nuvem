import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- 1. NÚCLEO DE CONEXÃO (O CORAÇÃO) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v34", layout="wide", page_icon="📈")

# --- 2. MOTOR DE SINCRONIZAÇÃO (ANTI-SANFONA) ---
def carregar_dados_globais():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("id", desc=True).execute().data
        cli = supabase.table("Clientes").select("*").order("id", desc=True).execute().data
        return (conf[0] if conf else {}), (est if est else []), (cli if cli else [])
    except:
        return {}, [], []

# --- 3. DESIGN E INTERFACE (ESTILO WINDOWS) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .win-card {
        background: white; padding: 20px; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR SISTEMA 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # CARREGAMENTO OBRIGATÓRIO (ÂNCORA)
    emp, estoque, clientes = carregar_dados_globais()

    # BARRA LATERAL (IDENTIDADE SISCOM)
    with st.sidebar:
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas/Pedidos", "📦 Estoque", "👥 Clientes", "📑 Importação Inteligente", "⚙️ Ajustes do Sistema"])

    # --- ABA: DASHBOARD (TILES) ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">📦 PRODUTOS<br><span class="metric-val">{len(estoque)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">👥 CLIENTES<br><span class="metric-val">{len(clientes)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">💰 VENDAS/DIA<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- ABA: VENDAS (PDV COM 1/2 VIAS) ---
    elif menu == "🛒 Vendas/Pedidos":
        st.header("🛒 Lançamento de Pedidos e Vendas")
        col_v1, col_v2 = st.columns([2, 1])
        
        with col_v1:
            st.subheader("Dados da Venda")
            cli_v = st.selectbox("Selecione o Cliente", [f"{c['id']} - {c['nome_completo']}" for c in clientes] if clientes else ["Novo Cliente"])
            prod_v = st.selectbox("Adicionar Produto", [f"{p['id']} - {p['descricao']} (R$ {p['preco_venda']})" for p in estoque] if estoque else ["Estoque Vazio"])
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            
        with col_v2:
            st.subheader("Resumo e Impressão")
            st.markdown(f'<div class="win-card">TOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Vias de Impressão", ["1 Via", "2 Vias"], index=0)
            if st.button("✅ FINALIZAR VENDA"):
                st.success(f"Venda concluída com {vias}!")

    # --- ABA: ESTOQUE (CONTROLE TOTAL) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Produtos")
        
        # Seleção para Edição (O segredo do controle total)
        opcoes_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in estoque]
        selecionado = st.selectbox("Pesquisar/Editar Produto", opcoes_p)
        p_edit = next((p for p in estoque if str(p['id']) in selecionado), None)
        
        with st.form("form_p"):
            c_p1, c_p2 = st.columns([3, 1])
            desc = c_p1.text_input("Descrição", value=p_edit['descricao'] if p_edit else "")
            ean = c_p2.text_input("Código/EAN", value=p_edit['ean13'] if p_edit else "")
            preco = st.number_input("Preço de Venda", value=float(p_edit['preco_venda'] or 0.0) if p_edit else 0.0)
            if st.form_submit_button("💾 SALVAR PRODUTO"):
                pld = {"descricao": desc, "ean13": ean, "preco_venda": preco}
                if p_edit: supabase.table("produtos").update(pld).eq("id", p_edit['id']).execute()
                else: supabase.table("produtos").insert(pld).execute()
                st.rerun()

        if estoque:
            st.dataframe(pd.DataFrame(estoque), use_container_width=True)

    # --- ABA: IMPORTAÇÃO INTELIGENTE (FIM DA BAGUNÇA) ---
    elif menu == "📑 Importação Inteligente":
        st.header("📑 Carga Massiva de Dados")
        alvo = st.selectbox("Enviar para:", ["produtos", "Clientes"])
        file = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if file and st.button("🚀 EXECUTAR CARGA"):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                try:
                    if alvo == "produtos":
                        p_limpo = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        ready = {"descricao": str(row.get('DESCRICAO')), "preco_venda": float(p_limpo), "ean13": str(row.get('CODIGO'))}
                    else:
                        ready = {"nome_completo": str(row.get('NOM')), "cpf_cnpj": str(row.get('CGC')), "endereco": str(row.get('RUA'))}
                    supabase.table(alvo).insert(ready).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES (CONTROLE DE IDENTIDADE) ---
    elif menu == "⚙️ Ajustes do Sistema":
        st.header("⚙️ Configurações de Identidade e Relatórios")
        with st.form("form_cfg"):
            n = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e = st.text_input("Endereço Completo", value=emp.get('end', ''))
            logo = st.file_uploader("Trocar Logomarca (PNG/GIF)", type=["png", "gif"])
            
            if st.form_submit_button("💾 FIXAR CONFIGURAÇÕES"):
                l_b64 = emp.get('logo_base64', '')
                if logo:
                    l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "end": e, "logo_base64": l_b64}).execute()
                st.rerun()
        
        st.divider()
        st.subheader("🔥 MANUTENÇÃO (RESETS)")
        col1, col2 = st.columns(2)
        if col1.button("🗑️ ZERAR ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if col2.button("🗑️ ZERAR CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
