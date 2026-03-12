import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# 1. CONEXÃO E IDIOMAS
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "config": "Configurações", "import": "Importar"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "config": "Settings", "import": "Import"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "config": "Ajustes", "import": "Importar"}
}
if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# 2. FUNÇÕES DE BLINDAGEM E LOGICA
def safe_query(table):
    try: return supabase.table(table).select("*").execute().data or []
    except: return []

def baixar_estoque(item_id, qtd_vendida):
    prod = supabase.table("produtos").select("estoque_atual").eq("id", item_id).execute().data[0]
    novo_estoque = float(prod['estoque_atual'] or 0) - float(qtd_vendida)
    supabase.table("produtos").update({"estoque_atual": novo_estoque}).eq("id", item_id).execute()

# --- INTERFACE ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("🚀 Login Sistema Profissional")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- 🛒 PDV COM BAIXA AUTOMÁTICA ---
    if menu == f"🛒 {T['vendas']}":
        st.header(f"🛒 PDV - {T['vendas']}")
        col_cli, col_venda = st.columns([1, 2])
        
        clis = safe_query("Clientes")
        prods = safe_query("produtos")
        
        with col_cli:
            cli_sel = st.selectbox("Cliente", [c['nome_completo'] for c in clis] if clis else ["Consumidor Padrão"])
            condicao = st.selectbox("Pagamento", ["À Vista", "À Prazo"])
            ajuste = st.number_input("Ajuste Final R$ (Desconto/Taxa)", value=0.0)

        with col_venda:
            if not prods: st.warning("Importe os produtos primeiro!")
            else:
                p_nome = st.selectbox("Adicionar Produto", [p['descricao'] for p in prods])
                qtd = st.number_input("Quantidade", min_value=0.1, value=1.0)
                if st.button("➕ Adicionar ao Carrinho"):
                    p_data = next(item for item in prods if item["descricao"] == p_nome)
                    if 'carrinho' not in st.session_state: st.session_state.carrinho = []
                    st.session_state.carrinho.append({
                        "id": p_data['id'], "descricao": p_nome, "quantidade": qtd, 
                        "preco": p_data['preco_venda'], "total": qtd * p_data['preco_venda']
                    })
        
        if st.session_state.get('carrinho'):
            df_car = pd.DataFrame(st.session_state.carrinho)
            st.table(df_car[['descricao', 'quantidade', 'preco', 'total']])
            if st.button("✅ FINALIZAR VENDA E BAIXAR ESTOQUE"):
                for item in st.session_state.carrinho:
                    baixar_estoque(item['id'], item['quantidade'])
                st.success("Venda realizada! Estoque atualizado.")
                st.session_state.carrinho = []
                st.rerun()

    # --- 📦 ESTOQUE (EDIÇÃO E EXCLUSÃO) ---
    elif menu == f"📦 {T['estoque']}":
        st.header(f"📦 Gestão de Inventário")
        prods = safe_query("produtos")
        if prods:
            df = pd.DataFrame(prods)
            st.dataframe(df[['ean13', 'descricao', 'unidade', 'preco_venda', 'estoque_atual']], use_container_width=True)
            
            with st.expander("✏️ Alterar ou 🗑️ Excluir Produto"):
                sel_p = st.selectbox("Escolha o produto", df['descricao'])
                p_edit = df[df['descricao'] == sel_p].iloc[0]
                new_price = st.number_input("Novo Preço", value=float(p_edit['preco_venda']))
                if st.button("Salvar Alteração"):
                    supabase.table("produtos").update({"preco_venda": new_price}).eq("id", p_edit['id']).execute()
                    st.rerun()
                if st.button("❌ EXCLUIR PRODUTO"):
                    supabase.table("produtos").delete().eq("id", p_edit['id']).execute()
                    st.rerun()

    # --- 📑 IMPORTAÇÃO COMPLETA (Mapeada do seu PDF) ---
    elif menu == f"📑 {T['import']}":
        st.header("📑 Importação de Catálogo")
        if st.button("🚀 Importar Todos os Produtos do PDF (Derlyana Alimentos)"):
            lista = [
                {"ean13": "00027", "descricao": "CAJUÍNA 200 ML (24 UN)", "unidade": "CX", "preco_venda": 60.00, "estoque_atual": 30.0},
                {"ean13": "00001", "descricao": "POLPA DE ABACAXI (KG)", "unidade": "KG", "preco_venda": 14.00, "estoque_atual": 11.0},
                # ... (Aqui entram todos os outros itens mapeados anteriormente)
            ]
            for p in lista: supabase.table("produtos").upsert(p).execute()
            st.success("Produtos Importados!")
