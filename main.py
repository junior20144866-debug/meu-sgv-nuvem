import streamlit as st
from supabase import create_client
import pandas as pd
import time
from datetime import datetime

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="SGV Evolution Pro", layout="wide", initial_sidebar_state="expanded")

# --- 2. DESIGN MODERNO (UI/UX) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .css-1d391kg { background-color: #1E1E1E; } /* Sidebar Dark */
    .stat-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        border-left: 5px solid #0078D4;
    }
    .product-row {
        background: white; padding: 10px; border-radius: 10px;
        margin-bottom: 5px; border: 1px solid #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CÉREBRO DO SISTEMA (PERSISTÊNCIA & BUSCA) ---
@st.cache_data(ttl=60)
def carregar_config():
    try:
        res = supabase.table("config").select("*").eq("id", 1).execute()
        return res.data[0] if res.data else {}
    except: return {}

def formato_br(v):
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 4. INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>Evolution Pro 🚀</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Chave Mestra", type="password") == "Naksu@6026":
            if st.button("ACESSAR SISTEMA", use_container_width=True):
                st.session_state.auth = True
                st.rerun()
else:
    # Sidebar Estilizada
    with st.sidebar:
        conf = carregar_config()
        st.subheader(conf.get('nome', 'SGV Evolution'))
        st.divider()
        menu = st.radio("MENU", ["📊 Painel Geral", "🛒 PDV (Vendas)", "📦 Estoque", "👥 Clientes", "💰 Financeiro", "⚙️ Configurações"])

    # --- PÁGINA: PDV (VENDAS INTELIGENTES) ---
    if menu == "🛒 PDV (Vendas)":
        st.title("🛒 Frente de Caixa")
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            busca = st.text_input("🔍 Digite o nome ou código do produto", placeholder="Ex: Polpa de Abacaxi...")
            prods = supabase.table("produtos").select("*").ilike("descricao", f"%{busca}%").limit(5).execute().data if busca else []
            
            for p in prods:
                col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                col_p1.write(p['descricao'])
                col_p2.write(formato_br(p['preco_venda']))
                if col_p3.button("➕", key=f"add_{p['id']}"):
                    st.session_state.carrinho.append(p)
                    st.toast(f"{p['descricao']} adicionado!")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.subheader("Carrinho")
            total = 0
            for i, item in enumerate(st.session_state.carrinho):
                st.write(f"· {item['descricao']} - {formato_br(item['preco_venda'])}")
                total += float(item['preco_venda'])
            
            st.divider()
            st.markdown(f"## Total: {formato_br(total)}")
            if st.button("FINALIZAR VENDA", type="primary", use_container_width=True):
                st.success("Venda processada com sucesso!")
                st.session_state.carrinho = []
                time.sleep(1)
                st.rerun()

    # --- PÁGINA: ESTOQUE & CLIENTES (CONTROLE TOTAL) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tabela = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.title(f"{menu} - Controle Total")
        
        dados = supabase.table(tabela).select("*").execute().data
        if dados:
            df = pd.DataFrame(dados)
            for idx, row in df.iterrows():
                with st.expander(f"📝 {row.get('descricao', row.get('nome_completo'))}"):
                    with st.form(f"form_{idx}"):
                        st.write("Edite as informações abaixo:")
                        # Aqui criamos campos dinâmicos baseados nas colunas
                        novos_dados = {}
                        for col in df.columns:
                            if col not in ['id', 'created_at']:
                                novos_dados[col] = st.text_input(col, value=str(row[col]))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.form_submit_button("💾 Salvar"):
                            supabase.table(tabela).update(novos_dados).eq("id", row['id']).execute()
                            st.success("Alterado!"); st.rerun()
                        if col_btn2.form_submit_button("🗑️ Excluir"):
                            supabase.table(tabela).delete().eq("id", row['id']).execute()
                            st.rerun()
        else: st.info("Nada cadastrado.")

    # --- PÁGINA: CONFIGURAÇÕES (RESOLVENDO GARGALOS) ---
    elif menu == "⚙️ Configurações":
        st.title("⚙️ Configurações Avançadas")
        
        with st.container():
            st.subheader("🏢 Dados da Empresa (Eternizar)")
            c1, c2 = st.columns(2)
            n_emp = c1.text_input("Nome Fantasia", conf.get('nome', ''))
            c_emp = c2.text_input("CNPJ", conf.get('cnpj', ''))
            e_emp = st.text_input("Endereço", conf.get('end', ''))
            
            if st.button("💾 SALVAR CONFIGURAÇÕES"):
                supabase.table("config").upsert({
                    "id": 1, "nome": n_emp, "cnpj": c_emp, "end": e_emp
                }).execute()
                st.cache_data.clear()
                st.success("Dados gravados no banco de dados!")

        st.divider()
        st.subheader("🧹 Limpeza por Sessão (Controle Total)")
        col_z1, col_z2, col_z3, col_z4 = st.columns(4)
        if col_z1.button("Zerar Clientes"):
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
        if col_z2.button("Zerar Estoque"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            st.rerun()
        if col_z3.button("Zerar Vendas"):
            st.info("Financeiro zerado!") # Simulação até criarmos a tabela de vendas
        if col_z4.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
