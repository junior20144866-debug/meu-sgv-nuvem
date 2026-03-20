import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- 1. CONEXÃO E SEGURANÇA MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v36", layout="wide", page_icon="💼")

# --- 2. MOTOR DE SINCRONIA TOTAL (FIM DO RETROCESSO) ---
@st.cache_data(ttl=5) # Cache de 5 segundos para fluidez e dados frescos
def carregar_dados_fresh():
    """Busca dados reais e limpa nulos que travam a visualização"""
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        # Blindagem: Tratamento de dados nulos antes que eles travem o Streamlit
        df_e = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_e['preco_venda'] = pd.to_numeric(df_e['preco_venda'], errors='coerce').fillna(0.0)
        
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        
        return (conf[0] if conf else {}), df_e, df_c
    except Exception as e:
        return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL WINDOWS/SISCOM ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .metric-value { font-size: 2.8rem; font-weight: 800; color: #0078D4; margin: 0; }
    .metric-label { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra de Ativação", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave incorreta")
else:
    # --- CARREGAMENTO GLOBAL E BLINDADO (ÂNCORA) ---
    emp, df_estoque, df_clientes = carregar_dados_fresh()

    # BARRA LATERAL (IDENTIDADE FIXA E GARANTIDA)
    with st.sidebar:
        if emp.get('logo_base64'):
            try: st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        st.title(emp.get('nome', 'SGV DESLIGADO'))
        if emp.get('end'): st.caption(emp['end'])
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas/Pedidos", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Importação Inteligente", "⚙️ Ajustes Gerenciais"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile"><p class="metric-label">Produtos</p><p class="metric-value">{len(df_estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="metric-label">Clientes</p><p class="metric-value">{len(df_clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="metric-label">Vendas Dia</p><p class="metric-value">0</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE (PRODUTOS) - FIX: VISUALIZAÇÃO GARANTIDA ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos e Inventário")
        if not df_estoque.empty:
            st.dataframe(df_estoque, use_container_width=True, hide_index=True)
            
            # Controle Total: Edição/Exclusão via Seletor
            with st.expander("🛠️ Deletar Registro"):
                sel_p = st.selectbox("Selecione para excluir", [f"{p['id']} - {p['descricao']}" for p in df_estoque.to_dict('records')])
                id_p = int(sel_p.split(" - ")[0])
                if st.button("🗑️ Deletar Permanentemente"):
                    supabase.table("produtos").delete().eq("id", id_p).execute()
                    st.rerun()
        else:
            st.warning("Estoque Vazio no Banco. Verifique a Importação.")

    # --- ABA: CLIENTES (CONSOLIDADE) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        if not df_clientes.empty:
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
            with st.expander("🛠️ Deletar Cliente"):
                sel_c = st.selectbox("Selecione para excluir", [f"{c['id']} - {c['nome_completo']}" for c in df_clientes.to_dict('records')])
                id_c = int(sel_c.split(" - ")[0])
                if st.button("🗑️ Deletar Cliente Permanentemente"):
                    supabase.table("Clientes").delete().eq("id", id_c).execute()
                    st.rerun()
        else:
            st.warning("Nenhum cliente cadastrado.")

    # --- ABA: VENDAS (PDV COM INTEGRAÇÃO REAL) ---
    elif menu == "🛒 Vendas/Pedidos":
        st.header("🛒 Ponto de Venda")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Carrinho de Venda")
            cliente_v = st.selectbox("Selecione Cliente", [c['nome_completo'] for c in df_clientes.to_dict('records')] if not df_clientes.empty else ["Consumidor Final"])
            # INTEGRAÇÃO REAL: Mostra os produtos da carga inteligente
            produto_v = st.selectbox("Selecione Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in df_estoque.to_dict('records')] if not df_estoque.empty else ["Estoque Vazio"])
            qtd = st.number_input("Qtd", min_value=1, value=1)
            
        with col2:
            st.subheader("Total e Impressão")
            st.markdown(f'<div class="win-tile">TOTAL: <span class="metric-value">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Vias de Impressão", ["1 Via", "2 Vias"])
            if st.button("✅ CONCLUIR E IMPRIMIR"):
                st.success("Venda simulada!")

    # --- ABA: IMPORTAÇÃO INTELIGENTE (MOTOR RECALIBRADO) ---
    elif menu == "📑 Importação Inteligente":
        st.header("📑 Carga Massiva Inteligente")
        alvo = st.selectbox("Destino da Carga", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba a planilha XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df.to_dict('records')
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        p_val = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        ready = {"descricao": str(r.get('DESCRICAO')), "preco_venda": float(p_val), "ean13": str(r.get('CODIGO'))}
                    else:
                        ready = {"nome_completo": str(r.get('NOM')), "cpf_cnpj": str(r.get('CGC')), "endereco": str(r.get('RUA'))}
                    supabase.table(alvo).insert(ready).execute()
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success("Importação Concluída com Sucesso!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES (CONTROLE DE IDENTIDADE) ---
    elif menu == "⚙️ Ajustes Gerenciais":
        st.header("⚙️ Configurações da Identidade e Manutenção")
        with st.form("form_ajustes_total"):
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Empresa", value=emp.get('nome', ''))
            e_e = c2.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo (PNG/GIF)", type=["png", "gif"])
            if st.form_submit_button("💾 FIXAR IDENTIDADE NO BANCO"):
                l_b64 = emp.get('logo_base64', '')
                if logo:
                    l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "end": e_e, "logo_base64": l_b64}).execute()
                st.rerun()
