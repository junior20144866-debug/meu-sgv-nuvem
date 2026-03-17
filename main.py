import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE SINCRONIA ---
def carregar_dados(tabela):
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except: return []

# --- 3. ESTILO E CABEÇALHO DE RELATÓRIO ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .header-relatorio {
        background-color: white; padding: 15px; border: 1px solid #ddd;
        border-radius: 5px; margin-bottom: 20px;
    }
    .win-tile {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-top: 5px solid #0078D4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("ACESSAR 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # CARREGAMENTO GLOBAL
    config_db = carregar_dados("config")
    emp = config_db[0] if config_db else {}
    estoque = carregar_dados("produtos")
    clientes = carregar_dados("Clientes")

    with st.sidebar:
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        menu = st.radio("MENU", ["🏠 Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: ESTOQUE / CLIENTES (COM SELEÇÃO E CORREÇÃO) ---
    if menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Gestão Total de {menu}")
        
        dados_tabela = estoque if tab == "produtos" else clientes
        
        # Bloco de Edição Inteligente
        col_list, col_edit = st.columns([2, 1])
        
        with col_list:
            st.subheader("Registros no Banco")
            if dados_tabela:
                df = pd.DataFrame(dados_tabela)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum dado encontrado nesta tabela.")

        with col_edit:
            st.subheader("🛠️ Corrigir ou Inserir")
            # Selecionador para Edição
            opcoes = ["Novo Registro"] + [f"{d['id']} - {d.get('descricao') or d.get('nome_completo')}" for d in dados_tabela]
            selecionado = st.selectbox("Selecione para alterar", opcoes)
            
            # Preencher campos se for edição
            item_edit = next((d for d in dados_tabela if str(d['id']) in selecionado), None)
            
            with st.form("form_master", clear_on_submit=True):
                if tab == "produtos":
                    desc = st.text_input("Descrição", value=item_edit['descricao'] if item_edit else "")
                    ean = st.text_input("Código", value=item_edit['ean13'] if item_edit else "")
                    preco = st.number_input("Preço", value=float(item_edit['preco_venda'] or 0.0) if item_edit else 0.0)
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": preco}
                else:
                    nome = st.text_input("Nome", value=item_edit['nome_completo'] if item_edit else "")
                    doc = st.text_input("CPF/CNPJ", value=item_edit['cpf_cnpj'] if item_edit else "")
                    end = st.text_input("Endereço", value=item_edit['endereco'] if item_edit else "")
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                
                btn_txt = "💾 SALVAR ALTERAÇÃO" if item_edit else "➕ INSERIR NOVO"
                if st.form_submit_button(btn_txt):
                    if item_edit:
                        supabase.table(tab).update(pld).eq("id", item_edit['id']).execute()
                    else:
                        supabase.table(tab).insert(pld).execute()
                    st.success("Concluído!")
                    time.sleep(1)
                    st.rerun()

            if item_edit:
                if st.button("🗑️ EXCLUIR ESTE ITEM"):
                    supabase.table(tab).delete().eq("id", item_edit['id']).execute()
                    st.rerun()

    # --- ABA: AJUSTES (CABECALHO E IMPRESSAO) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações e Cabeçalho")
        with st.form("cfg"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome Empresa", value=emp.get('nome', ''))
            cn = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            tel = c1.text_input("Telefone", value=emp.get('tel', ''))
            em = c2.text_input("E-mail", value=emp.get('email', ''))
            end = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.text_input("Link URL da Logomarca", value=emp.get('logo_base64', ''))
            
            st.write("---")
            vias = st.selectbox("Padrão de Vias na Impressão", ["1 Via", "2 Vias"])
            
            if st.form_submit_button("💾 FIXAR TUDO"):
                pld_cfg = {"id": 1, "nome": n, "cnpj": cn, "tel": tel, "email": em, "end": end, "logo_base64": logo}
                supabase.table("config").upsert(pld_cfg).execute()
                st.success("Configuração Salva!"); time.sleep(1); st.rerun()

    # --- ABA: IMPORTAÇÃO (RECALIBRADA) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação Inteligente")
        alvo = st.selectbox("Escolha o destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba o XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR AGORA"):
            df = pd.read_excel(arq)
            prog = st.progress(0)
            for i, row in df.iterrows():
                try:
                    if alvo == "produtos":
                        p_limpo = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        pld = {"descricao": str(row.get('DESCRICAO', '')), "preco_venda": float(p_limpo), "ean13": str(row.get('CODIGO', ''))}
                    else:
                        pld = {"nome_completo": str(row.get('NOM', '')), "cpf_cnpj": str(row.get('CGC', '')), "endereco": str(row.get('RUA', ''))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
                prog.progress((i + 1) / len(df))
            st.success("Importação finalizada!"); time.sleep(1); st.rerun()

    # --- ABA: DASHBOARD ---
    elif menu == "🏠 Dashboard":
        st.header("Dashboard Operacional")
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="win-tile">PRODUTOS NO ESTOQUE<br><span style="font-size:25px">{len(estoque)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES CADASTRADOS<br><span style="font-size:25px">{len(clientes)}</span></div>', unsafe_allow_html=True)
