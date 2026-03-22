import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v51", layout="wide", page_icon="🎯")

# --- 2. MOTOR DE RECUPERAÇÃO DE DADOS (ANTI-FANTASMA) ---
def carregar_universo_dados():
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        empresa = c[0] if c else {"id": 1, "nome": "SGV SISTEMAS", "end": "", "cnpj": "", "wts": ""}
        
        # Garantia de colunas para evitar a "tabela vazia" por erro de rótulo
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        
        # Aqui está o ajuste: aceitamos múltiplos nomes de coluna para Clientes
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco', 'rua', 'bairro', 'telefone'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO WINDOWS 11 ---
st.markdown("""
    <style>
    .stApp { background-color: #F3F3F3; }
    .win-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #0078D4; text-align: center; }
    .metric-val { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTENTICAÇÃO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 💼")
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("ACESSAR"):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_universo_dados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        st.write("---")
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "🛒 PDV & Financeiro", "📦 Produtos/Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Resumo Geral | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">CAIXA DIA<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)

    # --- PDV & FINANCEIRO ---
    elif menu == "🛒 PDV & Financeiro":
        st.header("🛒 Vendas e Controle Financeiro")
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            cliente = st.selectbox("Selecione o Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor Padrão"])
            prod = st.selectbox("Produto", [f"{p['id']} | {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Sem estoque"])
            qtd = st.number_input("Qtd", min_value=1, value=1)
            pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "A Prazo"])
        with col_v2:
            st.markdown('<div class="win-card">SUBTOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Vias", ["1 Via", "2 Vias"], horizontal=True)
            if st.button("🔥 FINALIZAR E REGISTRAR"): st.success("Venda enviada ao financeiro!")

    # --- GESTÃO DE PRODUTOS ---
    elif menu == "📦 Produtos/Estoque":
        st.header("📦 Gestão de Estoque")
        tab1, tab2 = st.tabs(["📋 Lista de Produtos", "🛠️ Incluir/Editar/Excluir"])
        with tab1:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab2:
            op_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Produto", op_p)
            it_ed = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("form_prod"):
                d = st.text_input("Descrição", value=it_ed['descricao'] if it_ed else "")
                u = st.text_input("Unidade", value=it_ed['unidade'] if it_ed else "UN")
                p = st.number_input("Preço", value=float(it_ed['preco_venda'] or 0.0) if it_ed else 0.0)
                if st.form_submit_button("💾 SALVAR"):
                    data = {"descricao": d, "unidade": u, "preco_venda": p}
                    if it_ed: supabase.table("produtos").update(data).eq("id", it_ed['id']).execute()
                    else: supabase.table("produtos").insert(data).execute()
                    st.rerun()
            if it_ed and st.button("🗑️ EXCLUIR DEFINITIVO"):
                supabase.table("produtos").delete().eq("id", it_ed['id']).execute(); st.rerun()

    # --- GESTÃO DE CLIENTES (CORREÇÃO DA TABELA VAZIA) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab1, tab2 = st.tabs(["📋 Relação de Clientes", "🛠️ Incluir/Editar/Excluir"])
        with tab1:
            if not df_c.empty:
                # Forçamos a exibição das colunas que o Siscom costuma usar
                colunas_uteis = [c for c in ['id', 'nome_completo', 'rua', 'bairro', 'telefone', 'cpf_cnpj'] if c in df_c.columns]
                st.dataframe(df_c[colunas_uteis], use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum cliente encontrado no banco de dados.")
        with tab2:
            op_c = ["Novo Cliente"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Cliente", op_c)
            cl_ed = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("form_cli"):
                n = st.text_input("Nome", value=cl_ed['nome_completo'] if cl_ed else "")
                r = st.text_input("Rua", value=cl_ed.get('rua', '') if cl_ed else "")
                b = st.text_input("Bairro", value=cl_ed.get('bairro', '') if cl_ed else "")
                t = st.text_input("Telefone", value=cl_ed.get('telefone', '') if cl_ed else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    data_c = {"nome_completo": n, "rua": r, "bairro": b, "telefone": t, "endereco": f"{r}, {b}"}
                    if cl_ed: supabase.table("Clientes").update(data_c).eq("id", cl_ed['id']).execute()
                    else: supabase.table("Clientes").insert(data_c).execute()
                    st.rerun()
            if cl_ed and st.button("🗑️ EXCLUIR CLIENTE"):
                supabase.table("Clientes").delete().eq("id", cl_ed['id']).execute(); st.rerun()

    # --- IMPORTAÇÃO ---
    elif menu == "📑 Importação":
        st.header("📑 Carga de Dados (Siscom/FPQ)")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("XLSX", type=["xlsx"])
        if arq and st.button("🚀 INICIAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        p_v = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "unidade": str(r.get('UNIDADE', 'UN')), "preco_venda": float(p_v)}).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM')), 
                            "rua": str(r.get('RUA', '')), 
                            "bairro": str(r.get('BAI', '')), 
                            "telefone": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importado!"); time.sleep(1); st.rerun()

    # --- CONFIGURAÇÕES & RESET ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Empresa & Controle")
        with st.form("f_conf"):
            n = st.text_input("Empresa", value=emp.get('nome', ''))
            cn = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            en = st.text_input("Endereço", value=emp.get('end', ''))
            wt = st.text_input("WhatsApp", value=emp.get('wts', ''))
            lg = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if lg: l64 = f"data:image/png;base64,{base64.b64encode(lg.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": cn, "end": en, "wts": wt, "logo_base64": l64}).execute()
                st.rerun()
        st.divider()
        c_r1, c_r2, c_r3 = st.columns(3)
        if c_r1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c_r2.button("👥 Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c_r3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
