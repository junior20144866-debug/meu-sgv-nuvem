import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# 1. Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO REFORMULADA (BASEADA NO SEU PDF) ---
def gerar_recibo_pdf(empresa, cliente_nome, itens, condicao, vencimento, n_pedido, taxa=0.0, desc_taxa="", vias=1):
    pdf = FPDF(format='A4')
    total_produtos = sum(item['total'] for item in itens)
    total_geral = total_produtos + taxa
    
    def desenhar_via(y_offset):
        # Cabeçalho Conforme PDF
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 6, empresa['nome_empresa'], ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(90, 6, f"Fone: {empresa['telefone']}", ln=1, align="R") # [cite: 9]
        
        pdf.set_x(10)
        pdf.cell(100, 5, empresa.get('endereco', ''), ln=0)
        pdf.cell(90, 5, f"CNPJ: {empresa.get('cnpj', '')}", ln=1, align="R") # [cite: 10]
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, f"PEDIDO DE VENDA Nº {n_pedido:04d}", border="TB", ln=1, align="C") # [cite: 8, 11]
        
        # Dados Cliente e Data
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(120, 5, f"CLIENTE: {cliente_nome}", ln=0) # [cite: 3]
        pdf.cell(70, 5, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align="R") # [cite: 12]
        
        # Tabela de Itens
        pdf.ln(2)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(85, 6, "Descricao", 1, 0, "L", True)
        pdf.cell(20, 6, "Qtd", 1, 0, "C", True)
        pdf.cell(20, 6, "Unid", 1, 0, "C", True)
        pdf.cell(30, 6, "Val. Unit", 1, 0, "C", True)
        pdf.cell(35, 6, "Total", 1, 1, "C", True)
        
        pdf.set_font("Arial", "", 8)
        for item in itens:
            pdf.cell(85, 6, item['descricao'], 1)
            pdf.cell(20, 6, str(item['quantidade']), 1, 0, "C")
            pdf.cell(20, 6, item['unidade'], 1, 0, "C")
            pdf.cell(30, 6, f"R$ {item['preco_venda']:.2f}", 1, 0, "R")
            pdf.cell(35, 6, f"R$ {item['total']:.2f}", 1, 1, "R")
        
        # Rodapé Financeiro [cite: 13, 17, 24]
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(130, 5, f"Pagamento: {condicao} {'(Venc: ' + vencimento.strftime('%d/%m/%Y') + ')' if condicao == 'À Prazo' else ''}", 0)
        pdf.cell(60, 5, f"Total Produtos: R$ {total_produtos:.2f}", 0, ln=1, align="R")
        
        if taxa > 0:
            pdf.cell(130, 5, f"Observação: {desc_taxa}", 0)
            pdf.cell(60, 5, f"(+) Taxas: R$ {taxa:.2f}", 0, ln=1, align="R")
            
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, f"VALOR TOTAL: R$ {total_geral:.2f}", 0, ln=1, align="R")
        
        # Assinaturas [cite: 25]
        pdf.ln(10)
        pdf.cell(90, 0.1, "", border="T")
        pdf.cell(10, 0.1, "")
        pdf.cell(90, 0.1, "", border="T", ln=1)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(90, 5, "Visto da Empresa", 0, 0, "C")
        pdf.cell(10, 5, "")
        pdf.cell(90, 5, "Visto do Cliente", 0, 1, "C")

        if vias == 2 and y_offset == 0:
            pdf.dashed_line(10, 148, 200, 148, 1, 1)

    pdf.add_page()
    desenhar_via(0)
    if vias == 2: desenhar_via(148)
    return bytes(pdf.output())

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("JMQJR - SGV - Sales system")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True
        st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "📥 Reposição de Estoque", "👥 Clientes", "📦 Estoque", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA CLIENTES (REIMPLANTADO EDIÇÃO/INCLUSÃO) ---
    if menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        aba1, aba2 = st.tabs(["Listar e Editar", "➕ Novo Cadastro"])
        
        with aba2:
            with st.form("add_cli"):
                n_c = st.text_input("Nome Completo")
                doc_c = st.text_input("CPF/CNPJ")
                if st.form_submit_button("Salvar Cliente"):
                    supabase.table("Clientes").insert({"nome_completo": n_c, "cpf_cnpj": doc_c}).execute()
                    st.success("Cadastrado!")
        
        with aba1:
            res_c = supabase.table("Clientes").select("*").execute()
            df_c = pd.DataFrame(res_c.data)
            if not df_c.empty:
                sel = st.selectbox("Selecione para alterar", df_c['nome_completo'])
                item = df_c[df_c['nome_completo'] == sel].iloc[0]
                with st.expander(f"Editar {sel}"):
                    novo_n = st.text_input("Nome", value=item['nome_completo'])
                    if st.button("Salvar Alterações"):
                        supabase.table("Clientes").update({"nome_completo": novo_n}).eq("id", item['id']).execute()
                        st.rerun()
                    if st.button("❌ EXCLUIR"):
                        supabase.table("Clientes").delete().eq("id", item['id']).execute()
                        st.rerun()
                st.dataframe(df_c)

    # --- ABA REPOSIÇÃO (NOVA FUNÇÃO) ---
    elif menu == "📥 Reposição de Estoque":
        st.header("📥 Entrada de Mercadorias")
        res_p = supabase.table("produtos").select("*").execute()
        p_list = {p['descricao']: p for p in res_p.data}
        
        with st.form("entrada"):
            prod_ent = st.selectbox("Escolha o Produto", list(p_list.keys()))
            qtd_ent = st.number_input("Quantidade de Entrada", min_value=0.1)
            if st.form_submit_button("Confirmar Entrada"):
                nova_qtd = p_list[prod_ent]['estoque_atual'] + qtd_ent
                supabase.table("produtos").update({"estoque_atual": nova_qtd}).eq("descricao", prod_ent).execute()
                st.success(f"Estoque de {prod_ent} atualizado para {nova_qtd}!")

    # --- ABA PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        # (Lógica de seleção de cliente e produto permanece a mesma...)
        # Na finalização:
        st.divider()
        col_t1, col_t2 = st.columns(2)
        taxa_v = col_t1.number_input("Taxas Adicionais (Entrega, etc)", min_value=0.0) # [cite: 17, 22]
        taxa_d = col_t2.text_input("Descrição da Taxa") # [cite: 16]
        
        if st.button("✅ FINALIZAR E GERAR PEDIDO"):
            # Incrementar número do pedido 
            ctrl = supabase.table("controle_pedidos").select("*").eq("id", 1).execute().data[0]
            novo_n = ctrl['ultimo_numero'] + 1
            supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
            
            emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
            pdf = gerar_recibo_pdf(emp, "NOME_CLIENTE", st.session_state.carrinho, "Condicao", date.today(), novo_n, taxa_v, taxa_d, 2)
            st.download_button("📄 Baixar Pedido", pdf, f"Pedido_{novo_n}.pdf")

    # --- ABA RELATÓRIOS ---
    elif menu == "📊 Relatórios":
        st.header("📊 Relatórios Gerenciais")
        if st.button("📦 Lista de Preços e Estoque"):
            res = supabase.table("produtos").select("descricao, unidade, preco_venda, estoque_atual").execute()
            st.dataframe(pd.DataFrame(res.data))
            # Aqui poderíamos gerar um PDF com a lista
        if st.button("👥 Relatório de Clientes"):
            res = supabase.table("Clientes").select("*").execute()
            st.dataframe(pd.DataFrame(res.data))
