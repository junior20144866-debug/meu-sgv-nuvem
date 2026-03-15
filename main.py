import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO E SEGURANÇA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE SINCRONIA COM VALIDAÇÃO (O FIM DA DÚVIDA) ---
def db_read_verified(tabela):
    """Busca dados e avisa se houver erro de conexão ou permissão"""
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data
    except Exception as e:
        st.error(f"Erro ao ler {tabela}: {e}")
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
    .tile-label { font-weight: bold; color: #555; text-transform: uppercase; letter-spacing: 1px; }
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
            else: st.error("Chave Inválida!")
else:
    # Leitura forçada para garantir que a lateral e dashboard tenham dados reais
    empresa_data = db_read_verified("config")
    emp = empresa_data[0] if empresa_data else {}
    estoque = db_read_verified("produtos")
    clientes = db_read_verified("Clientes")

    # BARRA LATERAL FIXA
    with st.sidebar:
        st.title(emp.get('nome', 'SISTEMA JMQJ'))
        if emp.get('cnpj'): st.write(f"CNPJ: {emp['cnpj']}")
        st.write("---")
        menu = st.radio("SISTEMAS", ["🏠 Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile"><p class="tile-label">Produtos</p><p class="tile-num">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-label">Clientes</p><p class="tile-num">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-label">Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)

    # --- ABA: AJUSTES (CONTROLE DE IDENTIDADE) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações de Identidade")
        with st.form("form_ajustes"):
            nome_f = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cnpj_f = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_f = st.text_input("Endereço", value=emp.get('end', ''))
            if st.form_submit_button("💾 SALVAR E FIXAR DADOS"):
                try:
                    # O Upsert força a gravação no ID 1 para persistência
                    resp = supabase.table("config").upsert({"id": 1, "nome": nome_f, "cnpj": cnpj_f, "end": end_f}).execute()
                    if resp.data:
                        st.success("BANCO DE DADOS ATUALIZADO COM SUCESSO!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro crítico ao salvar: {e}")

        st.divider()
        st.subheader("🔥 ZONA DE RESET")
        if st.button("🗑️ ZERAR DADOS DO SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.success("Tabelas limpas!"); time.sleep(1); st.rerun()

    # --- ABA: IMPORTAÇÃO (COM VALIDAÇÃO DE LINHA) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação de Planilha XLSX")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
        
        if arquivo and st.button("🚀 EXECUTAR CARGA"):
            df = pd.read_excel(arquivo)
            sucessos = 0
            erros_lista = []
            barra = st.progress(0)
            
            for i, row in df.iterrows():
                try:
                    if alvo == "produtos":
                        # Tratamento de preço: Remove R$ e ajusta separadores
                        p_limpo = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        pld = {
                            "descricao": str(row.get('DESCRICAO', '')),
                            "preco_venda": float(p_limpo) if p_limpo else 0.0,
                            "ean13": str(row.get('CODIGO', ''))
                        }
                    else:
                        pld = {
                            "nome_completo": str(row.get('NOM', '')),
                            "cpf_cnpj": str(row.get('CGC', '')),
                            "endereco": str(row.get('RUA', ''))
                        }
                    
                    check = supabase.table(alvo).insert(pld).execute()
                    if check.data: sucessos += 1
                except Exception as e:
                    erros_lista.append(f"Linha {i+2}: {str(e)}")
                barra.progress((i + 1) / len(df))
            
            st.write(f"✅ Processados: {sucessos} | ❌ Erros: {len(erros_lista)}")
            if erros_lista:
                with st.expander("Ver detalhes dos erros"):
                    for err in erros_lista: st.write(err)
            
            if sucessos > 0:
                st.success("Carga finalizada! Atualizando Dashboard...")
                time.sleep(2)
                st.rerun()

    # --- ABA: ESTOQUE / CLIENTES (LISTAGEM) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Listagem de {menu}")
        dados_ver = estoque if tab == "produtos" else clientes
        if dados_ver:
            st.dataframe(pd.DataFrame(dados_ver), use_container_width=True)
        else:
            st.warning("O banco de dados está vazio. Vá em Importação.")
