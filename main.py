import streamlit as st
from supabase import create_client
import pandas as pd
import time
import io

# --- 1. CONEXÃO BAZUCA (SEM FALHAS) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE INTELIGÊNCIA DE DADOS (ANTI-BAGUNÇA) ---
def mapear_e_limpar(df, tipo):
    # Dicionário de sinônimos baseado nos seus arquivos reais
    mapas = {
        "produtos": {
            "ean13": ["BARRA", "CODIGO", "REFERENCIA"],
            "descricao": ["DESCRICAO", "NOME", "ITEM"],
            "preco_venda": ["P_VENDA", "PRECO", "VALOR"],
            "unidade": ["UNIDADE", "UN"]
        },
        "Clientes": {
            "nome_completo": ["NOM", "NOME", "CLIENTE"],
            "cpf_cnpj": ["CGC", "CPF", "CNPJ"],
            "endereco": ["RUA", "LOGRADOURO", "ENDERECO"],
            "bairro": ["BAI", "BAIRRO"],
            "cidade": ["CID", "CIDADE"],
            "uf": ["UF"],
            "telefone": ["TEL1", "CEL", "TELEFONE"]
        }
    }
    
    df_final = pd.DataFrame()
    for campo_bd, sinonimos in mapas[tipo].items():
        # Tenta achar a coluna no seu Excel bagunçado
        col_excel = next((c for c in df.columns if str(c).upper().strip() in sinonimos), None)
        if col_excel:
            df_final[campo_bd] = df[col_excel]
            
    return df_final.dropna(subset=[df_final.columns[0]]) # Remove linhas totalmente vazias

# --- 3. UI STYLE: WINDOWS TILES ---
st.markdown("""
    <style>
    .stApp { background-color: #F3F4F7; }
    .win-tile {
        background: white; padding: 25px; border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-bottom: 4px solid #0078D4; text-align: center;
        transition: 0.3s;
    }
    .win-tile:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SISTEMA PRINCIPAL ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Acesso Biométrico/Senha", type="password") == "Naksu@6026":
            if st.button("DESBLOQUEAR"): st.session_state.auth = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🏠 Início", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação Inteligente", "📊 Relatórios", "💰 Financeiro", "⚙️ Configurações"])

    # --- ABA INÍCIO (ESTILO JANELAS) ---
    if menu == "🏠 Início":
        st.title("Painel JMQJ SGV")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown('<div class="win-tile"><p>🛒 Vendas de Hoje</p><h3>R$ 0,00</h3></div>', unsafe_allow_html=True)
        c2.markdown('<div class="win-tile"><p>📦 Itens no Estoque</p><h3>Consultar</h3></div>', unsafe_allow_html=True)
        c3.markdown('<div class="win-tile"><p>👥 Novos Clientes</p><h3>Acessar</h3></div>', unsafe_allow_html=True)
        c4.markdown('<div class="win-tile"><p>💰 Saldo em Caixa</p><h3>Relatório</h3></div>', unsafe_allow_html=True)

    # --- ABA VENDAS (PDV POLIDO) ---
    elif menu == "🛒 Vendas":
        st.header("🛒 Ponto de Venda")
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            busca = st.text_input("🔍 Buscar por nome ou código...")
            if busca:
                res = supabase.table("produtos").select("*").ilike("descricao", f"%{busca}%").execute().data
                for r in res:
                    c_p1, c_p2, c_p3 = st.columns([3, 1, 1])
                    c_p1.write(r['descricao'])
                    c_p2.write(f"R$ {r['preco_venda']}")
                    if c_p3.button("➕", key=f"venda_{r['id']}"): st.success("Adicionado!")
        with col_v2:
            st.subheader("Checkout")
            st.write("---")
            st.markdown("### Total: R$ 0,00")
            st.button("Finalizar e Emitir Cupom", type="primary")

    # --- ABA CLIENTES (CONTROLE TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        with st.expander("➕ Inclusão Manual"):
            with st.form("manual_cli"):
                n = st.text_input("Nome/Razão Social")
                d = st.text_input("CPF/CNPJ")
                end = st.text_input("Rua e Número")
                c1, c2, c3 = st.columns([2, 2, 1])
                b, ci, uf = c1.text_input("Bairro"), c2.text_input("Cidade"), c3.text_input("UF")
                if st.form_submit_button("Salvar Cadastro"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d, "endereco": end, "bairro": b, "cidade": ci, "uf": uf}).execute()
                    st.rerun()
        
        # Lista com edição
        clis = supabase.table("Clientes").select("*").execute().data
        if clis: st.dataframe(pd.DataFrame(clis), use_container_width=True)

    # --- ABA IMPORTAÇÃO (MASSA BAGUNÇADA) ---
    elif menu == "📑 Importação Inteligente":
        st.header("📑 Motor de Inteligência de Dados")
        tipo = st.selectbox("Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Suba sua planilha bagunçada", type=["xlsx"])
        if file:
            df_raw = pd.read_excel(file)
            df_limpo = mapear_e_limpar(df_raw, tipo)
            st.write("✅ Sistema organizou os dados assim:")
            st.dataframe(df_limpo.head())
            if st.button("🚀 Confirmar Inserção em Massa"):
                for _, row in df_limpo.iterrows():
                    supabase.table(tipo).insert(row.to_dict()).execute()
                st.success("Tudo carregado com sucesso!")

    # --- ABA CONFIGURAÇÕES (BLINDAGEM) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações do Sistema")
        # Busca no banco para não perder ao fechar
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        emp = conf[0] if conf else {}

        with st.form("empresa"):
            st.subheader("🏢 Dados da JMQJ SGV SISTEMAS")
            n_f = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c_f = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_f = st.text_input("Endereço Completo", value=emp.get('end', ''))
            # Logomarca
            upload_logo = st.file_uploader("Upload da Logomarca (PNG/JPG)", type=["png", "jpg"])
            if st.form_submit_button("💾 SALVAR E FIXAR"):
                supabase.table("config").upsert({"id": 1, "nome": n_f, "cnpj": c_f, "end": e_f}).execute()
                st.success("Configurações salvas permanentemente!")
        
        if st.button("🗑️ ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
