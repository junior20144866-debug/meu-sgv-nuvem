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

# --- FUNÇÃO DE IMPRESSÃO REFORMULADA (PEDIDO 4) ---
def gerar_recibo_pdf(empresa, cliente, itens, condicao, vencimento, n_pedido, taxa=0.0, desc_taxa="", vias=2):
    pdf = FPDF(format='A4')
    total_produtos = sum(item['total'] for item in itens)
    total_geral = total_produtos + taxa
    
    def desenhar_via(y_offset):
        # Cabeçalho
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(120, 6, empresa.get('nome_empresa', 'NOME DA EMPRESA'), ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(70, 6, f"Fone: {empresa.get('telefone', '')}", ln=1, align="R")
        pdf.set_x(10)
        pdf.cell(120, 5, empresa.get('endereco', ''), ln=0)
        pdf.cell(70, 5, f"CNPJ: {empresa.get('cnpj', '')}", ln=1, align="R")
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, f"PEDIDO DE VENDA Nº {n_pedido:04d}", border="TB", ln=1, align="C")
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(120, 6, f"CLIENTE: {cliente}", ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(70, 6, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align="R")
        
        # Tabela
        pdf.ln(2)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(85, 7, "Descricao", 1, 0, "L", True)
        pdf.cell(20, 7, "Qtd", 1, 0, "C", True)
        pdf.cell(20, 7, "Unid", 1, 0, "C", True)
        pdf.cell(30, 7, "Val. Unit", 1, 0, "C", True)
        pdf.cell(35, 7, "Total", 1, 1, "C", True)
        
        pdf.set_font("Arial", "", 9)
        for i in itens:
            pdf.cell(85, 7, i['descricao'], 1)
            pdf.cell(20, 7, str(i['quantidade']), 1, 0, "C")
            pdf.cell(20, 7, i['unidade'], 1, 0, "C")
            pdf.cell(30, 7, f"R$ {i['preco_venda']:.2f}", 1, 0, "R")
            pdf.cell(35, 7, f"R$ {i['total']:.2f}", 1, 1, "R")
        
        # Rodapé Financeiro conforme Pedido 4
        pdf.ln(2)
        txt_pgto = "À Vista" if condicao == "À Vista" else f"À Prazo - Venc: {vencimento.strftime('%d/%m/%Y')}"
        pdf.set_font("Arial", "B", 10)
        pdf.cell(130, 6, f"Pagamento: {txt_pgto}", 0)
        pdf.cell(60, 6, f"Total Produtos: R$ {total_produtos:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "", 9)
        obs_texto = f"Obs.: {desc_taxa}" if desc_taxa else "Obs.:"
        pdf.cell(130, 6, obs_texto, 0)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, f"(+) Taxas: R$ {taxa:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, f"VALOR TOTAL: R$ {total_geral:.2f}", 0, ln=1, align="R")
        
        # Assinatura (Apenas Cliente conforme Pedido 4)
        pdf.ln(10)
        pdf.set_x(60)
        pdf.cell(90, 0, "", border="T", ln=1)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(190, 5, "Visto do Cliente", 0, 1, "C")

        if vias == 2 and y_offset == 0:
            pdf.dashed_line(10, 148, 200, 148, 1, 1)

    pdf.add_page()
    desenhar_via(0)
    if vias == 2: desenhar_via(148)
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="JMQJR - SGV", layout="wide")

if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("JMQJR - SGV - Sales system")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True
        st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "📥 Reposição", "👥 Clientes", "📦 Estoque", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA CLIENTES ---
    if menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        t1, t2 = st.tabs(["Lista", "Novo Cadastro"])
        with t2:
            with st.form("c_f"):
                n = st.text_input("Nome")
                d = st.text_input("CPF/CNPJ")
                if st.form_submit_button("Salvar"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d}).execute()
                    st.success("Cliente cadastrado!")
                    st.rerun()
        with t1:
            res_c = supabase.table("Clientes").select("*").execute().data
            if res_c:
                df_c = pd.DataFrame(res_c)
                st.dataframe(df_c, use_container_width=True)
                sel_c = st.selectbox("Selecione para excluir", df_c['nome_completo'])
                if st.button("🗑️ Excluir Selecionado"):
                    id_c = df_c[df_c['nome_completo'] == sel_c]['id'].values[0]
                    supabase.table("Clientes").delete().eq("id", id_c).execute()
                    st.rerun()
            else: st.info("Nenhum cliente cadastrado.")

    # --- ABA ESTOQUE ---
    elif menu == "📦 Estoque":
        st.header("📦 Gerenciar Produtos")
        t1, t2 = st.tabs(["Lista", "Novo Produto"])
        with t2:
            with st.form("p_f"):
                desc = st.text_input("Descrição")
                prc = st.number_input("Preço de Venda", min_value=0.0)
                und = st.selectbox("Unidade", ["KG", "UNI", "CX", "PC"])
                if st.form_submit_button("Cadastrar"):
                    supabase.table("produtos").insert({"descricao": desc, "preco_venda": prc, "unidade": und, "estoque_atual": 0}).execute()
                    st.success("Produto cadastrado!")
                    st.rerun()
        with t1:
            res_p = supabase.table("produtos").select("*").execute().data
            if res_p:
                df_p = pd.DataFrame(res_p)
                st.dataframe(df_p, use_container_width=True)
                sel_p = st.selectbox("Selecionar Produto para excluir", df_p['descricao'])
                if st.button("🗑️ Excluir Produto"):
                    id_p = df_p[df_p['descricao'] == sel_p]['id'].values[0]
                    supabase.table("produtos").delete().eq("id", id_p).execute()
                    st.rerun()
            else: st.info("Nenhum produto em estoque.")

    # --- ABA REPOSIÇÃO (CORRIGIDA) ---
    elif menu == "📥 Reposição":
        st.header("📥 Entrada de Estoque")
        prods_res = supabase.table("produtos").select("*").execute().data
        if prods_res:
            p_dict = {p['descricao']: p for p in prods_res}
            with st.form("repo"):
                p_nome = st.selectbox("Selecione o Produto", list(p_dict.keys()))
                qtd_add = st.number_input("Quantidade de Entrada", min_value=0.1)
                if st.form_submit_button("Confirmar Entrada"):
                    nova_qtd = p_dict[p_nome]['estoque_atual'] + qtd_add
                    supabase.table("produtos").update({"estoque_atual": nova_qtd}).eq("descricao", p_nome).execute()
                    st.success(f"Estoque de {p_nome} atualizado!")
                    st.rerun()
        else: st.warning("Cadastre produtos primeiro.")

    # --- ABA PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        clis = [c['nome_completo'] for c in supabase.table("Clientes").select("nome_completo").execute().data]
        pros = {p['descricao']: p for p in supabase.table("produtos").select("*").execute().data}
        
        c1, c2 = st.columns([3, 1])
        cli_v = c1.selectbox("Cliente", [""] + clis)
        
        st.divider()
        cp, cq, cb = st.columns([3, 1, 1])
        p_sel = cp.selectbox("Produto", [""] + list(pros.keys()))
        q_sel = cq.number_input("Qtd", min_value=0.1, step=0.1)
        if cb.button("➕"):
            if p_sel:
                p_inf = pros[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": q_sel, "unidade": p_inf['unidade'], "preco_venda": p_inf['preco_venda'], "total": q_sel * p_inf['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar Carrinho"): st.session_state.carrinho = []; st.rerun()
            
            st.divider()
            f1, f2, f3 = st.columns(3)
            cond_v = f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc_v = f2.date_input("Vencimento") if cond_v == "À Prazo" else date.today()
            tax_v = f3.number_input("Taxa/Entrega", min_value=0.0)
            obs_v = st.text_input("Observações (Aparecerá no campo Obs.:)")
            
            if st.button("✅ FINALIZAR PEDIDO"):
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data[0]
                    novo_n = res_n['ultimo_numero'] + 1
                    supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
                except: novo_n = 1
                
                try: emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                except: emp = {}
                
                pdf = gerar_recibo_pdf(emp, cli_v, st.session_state.carrinho, cond_v, venc_v, novo_n, tax_v, obs_v)
                st.download_button("📄 Baixar Pedido", pdf, f"Pedido_{novo_n}.pdf", "application/pdf")
                st.session_state.carrinho = [] # Limpa após finalizar

    # --- ABA CONFIGURAÇÕES (COM RESET FINANCEIRO) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações e Reset")
        try: emp_d = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
        except: emp_d = {"nome_empresa":"","endereco":"","telefone":"","cnpj":""}
        
        with st.form("e_f"):
            n_e = st.text_input("Nome Empresa", value=emp_d['nome_empresa'])
            e_e = st.text_input("Endereço", value=emp_d['endereco'])
            t_e = st.text_input("Telefone", value=emp_d['telefone'])
            c_e = st.text_input("CNPJ", value=emp_d['cnpj'])
            if st.form_submit_button("Salvar Dados"):
                supabase.table("config_empresa").upsert({"id":1, "nome_empresa":n_e, "endereco":e_e, "telefone":t_e, "cnpj":c_e}).execute()
                st.success("Dados salvos!")

        st.divider()
        st.subheader("⚠️ Zona de Perigo")
        if st.button("🛑 ZERAR TODOS OS PEDIDOS E REINICIAR DO 01"):
            # Reseta o contador para 0 para que o próximo seja 1
            supabase.table("controle_pedidos").update({"ultimo_numero": 0}).eq("id", 1).execute()
            # Opcional: Aqui você poderia deletar a tabela de histórico de vendas se tivesse uma
            st.warning("O contador de pedidos foi reiniciado. O próximo pedido será o Nº 0001.")
