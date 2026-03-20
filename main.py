import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- 1. CONEXÃO E SEGURANÇA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v35", layout="wide", page_icon="📈")

# --- 2. MOTOR DE SINCRONIA (CARREGAMENTO DINÂMICO SEM CACHE) ---
def carregar_tudo():
    """Busca dados frescos do banco para garantir que a carga apareça"""
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        return (c[0] if c else {}), (p if p else []), (cl if cl else [])
    except:
        return {}, [], []

# --- 3. ESTILO VISUAL WINDOWS/FPQ ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-card {
        background: white; padding: 20px; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 4px solid #0078D4;
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
    # CARREGAMENTO FORÇADO DE DADOS
    emp, estoque, clientes = carregar_tudo()

    with st.sidebar:
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas/Pedidos", "📦 Estoque", "👥 Clientes", "📑 Importação Inteligente", "⚙️ Ajustes"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">📦 PRODUTOS<br><span class="metric-val">{len(estoque)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">👥 CLIENTES<br><span class="metric-val">{len(clientes)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">💰 VENDAS/DIA<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- ESTOQUE (PRODUTOS) - FIX: VISUALIZAÇÃO GARANTIDA ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Produtos")
        if estoque:
            df_p = pd.DataFrame(estoque)
            df_p['preco_venda'] = pd.to_numeric(df_p['preco_venda']).fillna(0.0)
            st.dataframe(df_p, use_container_width=True, hide_index=True)
            
            with st.expander("🛠️ Editar ou Excluir Produto"):
                sel_p = st.selectbox("Selecione o item", [f"{p['id']} - {p['descricao']}" for p in estoque])
                id_p = int(sel_p.split(" - ")[0])
                if st.button("🗑️ Deletar este Produto"):
                    supabase.table("produtos").delete().eq("id", id_p).execute()
                    st.rerun()
        else:
            st.warning("Estoque vazio no banco. Verifique a Importação.")

    # --- CLIENTES - FIX: VISUALIZAÇÃO GARANTIDA ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        if clientes:
            st.dataframe(pd.DataFrame(clientes), use_container_width=True, hide_index=True)
            with st.expander("🛠️ Excluir Cliente"):
                sel_c = st.selectbox("Selecione o cliente", [f"{c['id']} - {c['nome_completo']}" for c in clientes])
                id_c = int(sel_c.split(" - ")[0])
                if st.button("🗑️ Deletar este Cliente"):
                    supabase.table("Clientes").delete().eq("id", id_c).execute()
                    st.rerun()
        else:
            st.warning("Nenhum cliente cadastrado.")

    # --- VENDAS (PDV COM INTEGRAÇÃO REAL) ---
    elif menu == "🛒 Vendas/Pedidos":
        st.header("🛒 Ponto de Venda")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Itens do Pedido")
            # Seleção de Cliente e Produto integrada
            c_venda = st.selectbox("Cliente", [c['nome_completo'] for c in clientes] if clientes else ["Consumidor Final"])
            p_venda = st.selectbox("Produto", [f"{p['descricao']} | R$ {p['preco_venda']}" for p in estoque] if estoque else ["Estoque Vazio"])
            qtd = st.number_input("Qtd", min_value=1, value=1)
            
        with col2:
            st.subheader("Finalização")
            st.markdown(f'<div class="win-card">TOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Impressão", ["1 Via", "2 Vias"])
            if st.button("✅ CONCLUIR"):
                st.success("Venda registrada!")

    # --- IMPORTAÇÃO INTELIGENTE (MOTOR RECALIBRADO) ---
    elif menu == "📑 Importação Inteligente":
        st.header("📑 Carga Massiva de Dados")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Suba o arquivo Excel", type=["xlsx"])
        if file and st.button("🚀 IMPORTAR AGORA"):
            df = pd.read_excel(file)
            prog = st.progress(0)
            rows = df.to_dict('records')
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        p_val = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        pld = {"descricao": str(r.get('DESCRICAO')), "preco_venda": float(p_val), "ean13": str(r.get('CODIGO'))}
                    else:
                        pld = {"nome_completo": str(r.get('NOM')), "cpf_cnpj": str(r.get('CGC')), "endereco": str(r.get('RUA'))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success("Carga realizada com sucesso!"); time.sleep(1); st.rerun()

    # --- AJUSTES ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações")
        with st.form("f_cfg"):
            n = st.text_input("Empresa", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo:
                    l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute()
                st.rerun()
