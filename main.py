import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE LEITURA (VERDADE ÚNICA DO BANCO) ---
def db_read(tabela):
    """Busca dados reais no banco ignorando qualquer cache"""
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        return []

# --- 3. ESTILO VISUAL DASHBOARD ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.8rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-label { font-weight: bold; color: #555; text-transform: uppercase; letter-spacing: 1px; }
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
            else: st.error("Chave Inválida")
else:
    # CARREGAMENTO GLOBAL (FORÇA A SINCRONIA ENTRE ABAS)
    config_db = db_read("config")
    emp = config_db[0] if config_db else {}
    estoque = db_read("produtos")
    clientes = db_read("Clientes")

    with st.sidebar:
        # LOGO: Só funciona com URL da internet ou Base64. Caminho de pasta local (C:/) não abre em navegadores.
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        if emp.get('cnpj'): st.caption(f"CNPJ: {emp['cnpj']}")
        st.write("---")
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile"><p class="tile-label">Produtos</p><p class="tile-num">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-label">Clientes</p><p class="tile-num">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-label">Vendas/Dia</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE E CLIENTES (CONTROLE TOTAL) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Controle de {menu}")
        
        with st.expander("➕ Inserir Novo / Alterar Registro"):
            with st.form("form_master"):
                st.write("Dica: Informe o ID de um registro existente para alterá-lo.")
                id_reg = st.number_input("ID do Registro (0 para novo)", min_value=0)
                if tab == "produtos":
                    desc = st.text_input("Descrição do Produto")
                    ean = st.text_input("Código EAN")
                    pr = st.number_input("Preço de Venda", format="%.2f")
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pr}
                else:
                    nome = st.text_input("Nome / Razão Social")
                    doc = st.text_input("CPF / CNPJ")
                    end = st.text_input("Endereço")
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                
                if st.form_submit_button("CONSOLIDAR NO BANCO"):
                    try:
                        if id_reg == 0: supabase.table(tab).insert(pld).execute()
                        else: supabase.table(tab).update(pld).eq("id", id_reg).execute()
                        st.success("Dados Gravados!"); time.sleep(0.5); st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")

        # TABELA E EXCLUSÃO
        dados_lista = estoque if tab == "produtos" else clientes
        if dados_lista:
            df = pd.DataFrame(dados_lista)
            st.dataframe(df, use_container_width=True)
            
            c1, c2 = st.columns([1,3])
            id_del = c1.number_input("ID para EXCLUIR", min_value=0, key="del_final")
            if c1.button("🗑️ Deletar Registro", use_container_width=True):
                supabase.table(tab).delete().eq("id", id_del).execute()
                st.success(f"ID {id_del} removido."); time.sleep(0.5); st.rerun()

    # --- ABA: IMPORTAÇÃO ---
    elif menu == "📑 Importação":
        st.header("Carga em Massa via Excel")
        alvo = st.selectbox("Destino dos dados", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 INICIAR CARGA"):
            df_in = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            for i, row in enumerate(rows):
                try:
                    if alvo == "produtos":
                        p_val = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        item = {"descricao": str(row.get('DESCRICAO')), "preco_venda": float(p_val), "ean13": str(row.get('CODIGO'))}
                    else:
                        item = {"nome_completo": str(row.get('NOM')), "cpf_cnpj": str(row.get('CGC')), "endereco": str(row.get('RUA'))}
                    supabase.table(alvo).insert(item).execute()
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES (RESETS E LOGO) ---
    elif menu == "⚙️ Ajustes":
        st.header("Configurações do Sistema")
        with st.form("cfg_final"):
            n = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            l = st.text_input("Link da Logomarca (URL)", value=emp.get('logo_base64', ''))
            st.caption("Atenção: A logo deve ser um link da internet (ex: imgbb.com)")
            if st.form_submit_button("💾 SALVAR CONFIGURAÇÃO"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "logo_base64": l}).execute()
                st.success("Configuração Fixada!"); time.sleep(1); st.rerun()
        
        st.divider()
        st.subheader("🗑️ MANUTENÇÃO (RESETS)")
        col1, col2 = st.columns(2)
        if col1.button("🗑️ ZERAR ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if col2.button("🗑️ ZERAR CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
