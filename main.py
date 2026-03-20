import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- 1. NÚCLEO DE CONEXÃO E SEGURANÇA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS v33", layout="wide", page_icon="💼")

# --- 2. MOTOR DE SINCRONIA FORÇADA (O FIM DA SANFONA) ---
# Toda vez que o programa roda, ele lê TODAS as tabelas vitais para a memória.
def buscar_dados(tabela):
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except: return []

# --- 3. ARQUITETURA DE DESIGN (ESTILO FPQSYSTEM) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .win-card {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        margin-bottom: 20px; text-align: center;
    }
    .metric-value { font-size: 2.5rem; font-weight: 800; color: #0078D4; }
    .metric-title { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra de Ativação", type="password")
        if st.button("ATIVAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave incorreta")
else:
    # --- CARREGAMENTO GLOBAL E OBRIGATÓRIO (ÂNCORA DO SISTEMA) ---
    cfg_list = buscar_dados("config")
    emp = cfg_list[0] if cfg_list else {}
    estoque = buscar_dados("produtos")
    clientes = buscar_dados("Clientes")

    # BARRA LATERAL (IDENTIDADE VISUAL FIXA)
    with st.sidebar:
        # LOGO: Mostra a imagem Base64 que gravamos no banco
        if emp.get('logo_base64'):
            try:
                st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        
        st.title(emp.get('nome', 'JMQJ SGV'))
        if emp.get('cnpj'): st.caption(f"CNPJ: {emp['cnpj']}")
        st.write("---")
        menu = st.radio("SISTEMAS CADASTRADOS", ["🏠 Dashboard", "🛒 Vendas (PDV)", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Importação em Massa", "📊 Relatórios Gerenciais", "⚙️ Configurações"])

    # --- ABA: DASHBOARD (JANELAS INTELIGENTES) ---
    if menu == "🏠 Dashboard":
        st.header(f"Centro de Comando Gerencial | {emp.get('nome', 'SGV')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-card"><p class="metric-title">Produtos</p><p class="metric-value">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="metric-title">Clientes</p><p class="metric-value">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="metric-title">Vendas Hoje</p><p class="metric-value">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="metric-title">Financeiro</p><p class="metric-value">0,00</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE (PRODUTOS) - CONTROLE TOTAL ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão e Controle de Inventário")
        
        # 1. Formulário de Cadastro e Edição por ID
        with st.expander("📝 Novo Produto ou Alteração (Use ID para alterar)"):
            with st.form("form_p"):
                id_p = st.number_input("ID para Edição (0 para Novo)", min_value=0, step=1)
                desc = st.text_input("Descrição Completa")
                ean = st.text_input("Código EAN / Barras")
                pre = st.number_input("Preço de Venda", format="%.2f")
                st.form_submit_button("💾 CONSOLIDAR DADOS NO ESTOQUE")
        
        # 2. Relação de Produtos (Fixed NoneType error)
        if estoque:
            st.subheader("Relação Completa de Itens")
            df_p = pd.DataFrame(estoque)
            # Tratamento inteligente para evitar erro na visualização
            df_p['preco_venda'] = df_p['preco_venda'].fillna(0.0)
            st.dataframe(df_p, use_container_width=True, hide_index=True)
        else:
            st.warning("Estoque vazio.")

    # --- ABA: IMPORTAÇÃO EM MASSA (MOTOR RECALIBRADO) ---
    elif menu == "📑 Importação em Massa":
        st.header("📑 Carga de Dados Massiva Inteligente")
        alvo = st.selectbox("Destino da Carga", ["produtos", "Clientes"])
        st.info("O programa fará a captura inteligente, mesmo com colunas bagunçadas.")
        file = st.file_uploader("Suba sua planilha XLSX", type=["xlsx"])
        
        if file and st.button("🚀 EXECUTAR IMPORTAÇÃO AGORA"):
            df_in = pd.read_excel(file)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            
            for i, row in enumerate(rows):
                try:
                    if alvo == "produtos":
                        # Limpeza inteligente de preço (R$, pontos, vírgulas)
                        p_raw = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        pld = {"descricao": str(row.get('DESCRICAO', '')), "preco_venda": float(p_raw), "ean13": str(row.get('CODIGO', ''))}
                    else:
                        pld = {"nome_completo": str(row.get('NOM', '')), "cpf_cnpj": str(row.get('CGC', '')), "endereco": str(row.get('RUA', ''))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success("Importação Concluída!"); time.sleep(1); st.rerun()

    # --- ABA: CONFIGURAÇÕES (O CONTRAPESSO DO EFEITO SANFONA) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações e Manutenção da Identidade")
        
        # 1. Formulário de Identidade (Fixed: Adicionado Endereço e Logo via Upload)
        with st.form("form_config_total"):
            st.subheader("Identidade da JMQJ SGV")
            n = st.text_input("Nome Fantasia", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e = st.text_input("Endereço Completo", value=emp.get('end', ''))
            st.write("---")
            
            # Novo Sistema de Upload de Logo (Guardado no banco como Base64)
            st.write("A logomarca fixa deve ser PNG ou GIF.")
            up_logo = st.file_uploader("Upload da Logomarca", type=["png", "gif"])
            
            # Opção de Vias (Auditória)
            vias_conf = st.selectbox("Padrão de Impressão (Vendas)", ["1 Via", "2 Vias"])
            
            if st.form_submit_button("💾 SALVAR E FIXAR IDENTIDADE"):
                # Tratamento da Logo para Base64
                l_b64 = emp.get('logo_base64', '')
                if up_logo:
                    l_b64 = f"data:image/png;base64,{base64.b64encode(up_logo.read()).decode('utf-8')}"
                
                # Upsert força a gravação no ID 1, travando os dados no banco
                pld_cfg = {"id": 1, "nome": n, "cnpj": c, "end": e, "logo_base64": l_b64}
                supabase.table("config").upsert(pld_cfg).execute()
                st.success("Identidade Eternizada!"); time.sleep(1); st.rerun()

        # 2. Zona de Manutenção (RESETS - Reativado)
        st.divider()
        st.subheader("🔥 Central de Manutenção (Reset Total)")
        col_res1, col_res2 = st.columns(2)
        if col_res1.button("🗑️ ZERAR TODO O ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            st.rerun()
        if col_res2.button("🗑️ RESET TOTAL SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
