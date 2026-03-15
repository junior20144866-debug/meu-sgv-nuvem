import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE SINCRONIA (LEITURA REAL) ---
def db_read(tabela):
    """Busca dados reais ignorando o cache do navegador"""
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        # Se a tabela ainda estiver sendo propagada, retorna vazio em vez de erro
        return []

# --- 3. ESTILO WINDOWS MODERNO ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.8rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-label { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra de Ativação", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave Inválida")
else:
    # Carregamento das tabelas recém-criadas
    config_data = db_read("config")
    emp = config_data[0] if config_data else {}
    estoque = db_read("produtos")
    clientes = db_read("Clientes")

    # BARRA LATERAL (IDENTIDADE VIVA)
    with st.sidebar:
        st.title(emp.get('nome', 'JMQJ SGV'))
        if emp.get('cnpj'): st.caption(f"CNPJ: {emp['cnpj']}")
        st.write("---")
        menu = st.radio("SISTEMAS", ["🏠 Painel Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- ABA: DASHBOARD (JANELAS INTELIGENTES) ---
    if menu == "🏠 Painel Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile"><p class="tile-label">Produtos</p><p class="tile-num">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-label">Clientes</p><p class="tile-num">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-label">Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE E CLIENTES (EDIÇÃO MANUAL) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Gestão de {menu}")
        
        with st.expander("📝 Cadastro Direto"):
            with st.form("form_dados"):
                id_reg = st.number_input("ID (0 para Novo)", min_value=0)
                if tab == "produtos":
                    desc = st.text_input("Descrição")
                    ean = st.text_input("Código")
                    pr = st.number_input("Preço de Venda", format="%.2f")
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pr}
                else:
                    nome = st.text_input("Nome/Razão Social")
                    doc = st.text_input("CPF/CNPJ")
                    end = st.text_input("Endereço")
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                
                if st.form_submit_button("GRAVAR NO BANCO"):
                    try:
                        if id_reg == 0: supabase.table(tab).insert(pld).execute()
                        else: supabase.table(tab).update(pld).eq("id", id_reg).execute()
                        st.success("Operação realizada!"); time.sleep(1); st.rerun()
                    except Exception as e: st.error(f"Erro ao gravar: {e}")

        # Listagem
        dados = estoque if tab == "produtos" else clientes
        if dados:
            st.dataframe(pd.DataFrame(dados), use_container_width=True)
            id_del = st.number_input("ID para EXCLUIR", min_value=0, key="del")
            if st.button("🗑️ Deletar Permanentemente"):
                supabase.table(tab).delete().eq("id", id_del).execute()
                st.rerun()

    # --- ABA: IMPORTAÇÃO (MOTOR RECALIBRADO) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga em Massa via Excel")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba seu arquivo XLSX", type=["xlsx"])
        
        if arq and st.button("🚀 INICIAR CARGA"):
            df_ex = pd.read_excel(arq)
            prog = st.progress(0)
            lista_it = df_ex.to_dict('records')
            
            for i, row in enumerate(lista_it):
                try:
                    if alvo == "produtos":
                        p_limpo = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        ready = {"descricao": str(row.get('DESCRICAO', '')), "preco_venda": float(p_limpo), "ean13": str(row.get('CODIGO', ''))}
                    else:
                        ready = {"nome_completo": str(row.get('NOM', '')), "cpf_cnpj": str(row.get('CGC', '')), "endereco": str(row.get('RUA', ''))}
                    supabase.table(alvo).insert(ready).execute()
                except: pass
                prog.progress((i + 1) / len(lista_it))
            st.success("Importação Concluída!"); time.sleep(1); st.rerun()

    # --- ABA: CONFIGURAÇÕES (O TESTE DE FOGO) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Identidade da Empresa")
        with st.form("cfg"):
            n_f = st.text_input("Nome Fantasia", value=emp.get('nome', ''))
            c_f = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_f = st.text_input("Endereço", value=emp.get('end', ''))
            if st.form_submit_button("💾 SALVAR CONFIGURAÇÕES"):
                try:
                    supabase.table("config").upsert({"id": 1, "nome": n_f, "cnpj": c_f, "end": e_f}).execute()
                    st.success("Configurações fixadas!"); time.sleep(1); st.rerun()
                except Exception as e: st.error(f"Falha ao salvar: {e}")
