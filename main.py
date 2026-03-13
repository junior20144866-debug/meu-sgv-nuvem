import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

# --- 2. FUNÇÕES DE LIMPEZA (O Cérebro do Lema) ---
def tratar_preco(valor):
    try:
        if pd.isna(valor): return 0.0
        # Remove R$, pontos de milhar e troca vírgula por ponto
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except: return 0.0

def formato_br(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

# --- 3. INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Login SGV")
    if st.text_input("Senha", type="password") == "Naksu@6026":
        if st.button("Acessar"):
            st.session_state.auth = True
            st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação Inteligente", "⚙️ Sistema"])

    # --- ABA ESTOQUE (COM EDIÇÃO/EXCLUSÃO) ---
    if menu == "📦 Estoque":
        st.header("📦 Gestão de Estoque")
        
        prods = supabase.table("produtos").select("*").order("descricao").execute().data
        if prods:
            for p in prods:
                with st.container():
                    c1, c2, c3, c4 = st.columns([1, 3, 1, 1])
                    c1.write(f"`{p.get('ean13', 'S/C')}`")
                    c2.write(f"**{p['descricao']}**")
                    c3.write(formato_br(p.get('preco_venda', 0)))
                    if c4.button("🗑️", key=f"delp_{p['id']}"):
                        supabase.table("produtos").delete().eq("id", p['id']).execute()
                        st.rerun()
                st.divider()
        else: st.info("Estoque vazio.")

    # --- ABA IMPORTAÇÃO (INTELIGÊNCIA ANTI-ERRO) ---
    elif menu == "📑 Importação Inteligente":
        st.header("📑 Motor de Organização de Dados")
        tipo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba seu Excel (mesmo bagunçado)", type=["xlsx"])
        
        if arq:
            df = pd.read_excel(arq)
            st.write(f"🔍 Analisando {len(df)} linhas...")
            
            # Mapeamento com Sinônimos
            mapa = {
                "produtos": {"ean13": ["CODIGO", "EAN", "BARRA"], "descricao": ["DESCRICAO", "NOME"], "preco_venda": ["P_VENDA", "PRECO"]},
                "Clientes": {"nome_completo": ["NOM", "NOME"], "cpf_cnpj": ["CGC", "CPF", "CNPJ"]}
            }[tipo]
            
            dados_prontos = []
            for _, row in df.iterrows():
                item = {}
                for campo_bd, sinonimos in mapa.items():
                    for col_excel in df.columns:
                        if col_excel.upper().strip() in sinonimos:
                            val = row[col_excel]
                            # TRATAMENTO ESPECIAL PARA PREÇO
                            if campo_bd == "preco_venda":
                                item[campo_bd] = tratar_preco(val)
                            else:
                                item[campo_bd] = str(val).strip() if pd.notnull(val) else None
                if item: dados_prontos.append(item)

            if dados_prontos:
                st.success(f"Reconheci {len(dados_prontos)} registros!")
                if st.button("🚀 Organizar e Salvar no Banco"):
                    prog = st.progress(0)
                    for i, d in enumerate(dados_prontos):
                        try:
                            supabase.table(tipo).insert(d).execute()
                        except Exception as e:
                            st.error(f"Erro na linha {i}: {e}")
                        prog.progress((i + 1) / len(dados_prontos))
                    st.success("Tudo organizado!"); st.balloons()

    # --- ABA SISTEMA ---
    elif menu == "⚙️ Sistema":
        st.subheader("🛠️ Ferramentas de Manutenção")
        if st.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.success("Tabelas zeradas!"); st.rerun()
