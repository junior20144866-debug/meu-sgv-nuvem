import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. CONFIGURAÇÃO DE TELA E ESTILO ---
st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.8rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-label { font-weight: bold; color: #555; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE DADOS SEM CACHE (TRAÇÃO DIRETA) ---
def db_read(tabela):
    """Busca dados reais no banco ignorando qualquer cache do navegador"""
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except:
        return []

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
    # LEITURA OBRIGATÓRIA EM CADA REFRESH (FIM DA SANFONA)
    config_list = db_read("config")
    emp = config_list[0] if config_list else {}
    estoque = db_read("produtos")
    clientes = db_read("Clientes")

    # BARRA LATERAL
    with st.sidebar:
        st.title(emp.get('nome', 'JMQJ SGV'))
        if emp.get('cnpj'): st.caption(f"CNPJ: {emp['cnpj']}")
        st.write("---")
        menu = st.radio("SISTEMAS", ["🏠 Painel Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- ABA: DASHBOARD (JANELAS VIVAS) ---
    if menu == "🏠 Painel Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome', 'SGV')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-tile"><p class="tile-label">Produtos</p><p class="tile-num">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-label">Clientes</p><p class="tile-num">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-label">Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="tile-label">Sistema</p><p class="tile-num" style="color:green">Ativo</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE E CLIENTES (CONTROLE DE EDIÇÃO) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Gestão de {menu}")
        
        with st.expander("📝 Inserir ou Editar Registro"):
            with st.form("form_edit"):
                id_edit = st.number_input("ID (0 para Novo)", min_value=0)
                if tab == "produtos":
                    desc = st.text_input("Descrição")
                    ean = st.text_input("Código")
                    pr = st.number_input("Preço", format="%.2f")
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pr}
                else:
                    nome = st.text_input("Nome/Razão Social")
                    doc = st.text_input("CPF/CNPJ")
                    end = st.text_input("Endereço")
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                
                if st.form_submit_button("💾 SALVAR NO BANCO"):
                    if id_edit == 0: supabase.table(tab).insert(pld).execute()
                    else: supabase.table(tab).update(pld).eq("id", id_edit).execute()
                    st.success("Gravado!")
                    time.sleep(1)
                    st.rerun()

        dados_lista = estoque if tab == "produtos" else clientes
        if dados_lista:
            st.dataframe(pd.DataFrame(dados_lista), use_container_width=True)
            id_del = st.number_input("ID para Excluir", min_value=0, key="del")
            if st.button("🗑️ Confirmar Exclusão"):
                supabase.table(tab).delete().eq("id", id_del).execute()
                st.rerun()

    # --- ABA: IMPORTAÇÃO (MOTOR DE ALTA PERFORMANCE) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga em Massa (XLSX)")
        target = st.selectbox("Para onde enviar?", ["produtos", "Clientes"])
        file = st.file_uploader("Selecione o arquivo", type=["xlsx"])
        
        if file and st.button("🚀 EXECUTAR IMPORTAÇÃO"):
            df_in = pd.read_excel(file)
            progress = st.progress(0)
            items = df_in.to_dict('records')
            
            for i, row in enumerate(items):
                if target == "produtos":
                    # Limpeza de preços: remove R$, pontos e ajusta vírgula
                    raw_p = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                    ready = {
                        "descricao": str(row.get('DESCRICAO', '')),
                        "preco_venda": float(raw_p) if raw_p else 0.0,
                        "ean13": str(row.get('CODIGO', ''))
                    }
                else:
                    ready = {
                        "nome_completo": str(row.get('NOM', '')),
                        "cpf_cnpj": str(row.get('CGC', '')),
                        "endereco": str(row.get('RUA', ''))
                    }
                supabase.table(target).insert(ready).execute()
                progress.progress((i + 1) / len(items))
            
            st.success(f"Sucesso! {len(items)} registros inseridos.")
            time.sleep(2)
            st.rerun()

    # --- ABA: CONFIGURAÇÕES (TRAVA DE PERSISTÊNCIA) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações e Identidade")
        
        with st.form("cfg"):
            n = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            st.info("Logomarca: Suporta PNG, GIF e JPG.")
            logo = st.file_uploader("Logomarca", type=["png", "gif", "jpg"])
            
            if st.form_submit_button("💾 SALVAR DEFINITIVAMENTE"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "end": e}).execute()
                st.success("Configurações salvas e travadas!")
                time.sleep(1)
                st.rerun()

        st.divider()
        st.subheader("🔥 RESET DO SISTEMA")
        col1, col2 = st.columns(2)
        if col1.button("🗑️ ZERAR ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            st.rerun()
        if col2.button("🗑️ ZERAR CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
