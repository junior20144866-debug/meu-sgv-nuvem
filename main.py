import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO DIRETA (SEM CACHE PARA EVITAR SANFONA) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v89", layout="wide", page_icon="🎯")

# --- 2. SEGURANÇA (BLOQUEIO DE ACESSO) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        senha = st.text_input("Digite a Senha Mestra", type="password")
        if st.button("LIGAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Acesso Negado.")
    st.stop()

# --- 3. CARREGAMENTO EM TEMPO REAL ---
def carregar_tudo():
    try:
        e = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        c = supabase.table("Clientes").select("*").order("NOM").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except:
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_tudo()

# --- 4. BARRA LATERAL (IDENTIDADE FIXA) ---
with st.sidebar:
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.title(emp.get('nome', 'JMQJ SGV'))
    st.info(f"📍 {emp.get('cidade', 'Cidade')}/{emp.get('uf', 'UF')}\n\n📞 {emp.get('tel', 'Telefone')}")
    st.write("---")
    menu = st.radio("MÓDULOS", ["📊 Dashboard", "🧾 Emitir Pedido", "👥 Cadastro Clientes", "📦 Cadastro Produtos", "⚙️ Configurações"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Resumo da Operação")
    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Ativos", len(df_c))
    c2.metric("Itens no Estoque", len(df_p))
    c3.metric("Faturamento Hoje", "R$ 0,00")

# --- EMISSÃO DE PEDIDO (A5) ---
elif menu == "🧾 Emitir Pedido":
    st.header("📝 Novo Pedido de Venda")
    if df_p.empty or df_c.empty:
        st.warning("Cadastre clientes e produtos antes de iniciar.")
    else:
        col1, col2 = st.columns([1, 1.3])
        with col1:
            with st.form("venda_form"):
                sel_cli = st.selectbox("Selecione o Cliente", df_c['NOM'].tolist())
                sel_prod = st.selectbox("Selecione o Produto", df_p['descricao'].tolist())
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                desc = st.number_input("Desconto (R$)", min_value=0.0, value=0.0)
                acre = st.number_input("Acréscimo (R$)", min_value=0.0, value=0.0)
                if st.form_submit_button("GERAR PRÉVIA"):
                    st.session_state.preview = True
                    st.session_state.cli_data = df_c[df_c['NOM'] == sel_cli].iloc[0]
                    st.session_state.pro_data = df_p[df_p['descricao'] == sel_prod].iloc[0]
                    st.session_state.valores = {'qtd': qtd, 'desc': desc, 'acre': acre}

        if st.session_state.get('preview'):
            with col2:
                c = st.session_state.cli_data
                p = st.session_state.pro_data
                v = st.session_state.valores
                subtotal = p['p_venda'] * v['qtd']
                total = subtotal - v['desc'] + v['acre']
                
                html_pedido = f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: 'Courier New'; background: white; color: black;">
                    <table style="width:100%"><tr>
                        <td width="20%"><img src="{emp.get('logo_base64','')}" width="100"></td>
                        <td style="text-align:center"><b>{emp.get('nome','')}</b><br>CNPJ: {emp.get('cnpj','')}<br>{emp.get('end','')}<br>{emp.get('tel','')}</td>
                        <td style="text-align:right">PEDIDO #001<br>{datetime.now().strftime('%d/%m/%Y')}</td>
                    </tr></table>
                    <hr>
                    <p><b>CLIENTE:</b> {c['NOM']} | <b>CPF/CNPJ:</b> {c.get('CPF','')}</p>
                    <p><b>ENDEREÇO:</b> {c.get('RUA','')}, {c.get('BAI','')}, {c.get('CIDADE','')}/{c.get('UF','')}</p>
                    <table style="width:100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #000;"><th>ITEM</th><th>QTD</th><th>UN</th><th>VALOR</th><th>TOTAL</th></tr>
                        <tr><td>{p['descricao']}</td><td align="center">{v['qtd']}</td><td align="center">{p.get('unidade','UN')}</td><td align="right">{p['p_venda']:.2f}</td><td align="right">{subtotal:.2f}</td></tr>
                    </table>
                    <div style="text-align:right; margin-top:20px;">
                        <p>SUBTOTAL: R$ {subtotal:.2f}</p>
                        <p style="color:red">(-) DESCONTO: R$ {v['desc']:.2f}</p>
                        <p style="color:green">(+) ACRÉSCIMO: R$ {v['acre']:.2f}</p>
                        <h3>TOTAL DO PEDIDO: R$ {total:.2f}</h3>
                    </div>
                </div>
                """
                st.markdown(html_pedido, unsafe_allow_html=True)

# --- CADASTRO DE CLIENTES ---
elif menu == "👥 Cadastro Clientes":
    st.header("👥 Inclusão de Clientes")
    with st.form("cli_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome/Razão Social")
        doc = c2.text_input("CNPJ/CPF")
        rua = st.text_input("Endereço (Rua)")
        c3, c4, c5 = st.columns([2,2,1])
        bairro = c3.text_input("Bairro")
        cidade = c4.text_input("Cidade", value="Cascavel")
        uf = c5.selectbox("UF", ["CE","RN","PB","PE"])
        c6, c7 = st.columns(2)
        tel = c6.text_input("Telefone/WhatsApp")
        email = c7.text_input("E-mail")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            supabase.table("Clientes").insert({
                "NOM": nome, "CPF": doc, "RUA": rua, "BAI": bairro, 
                "CIDADE": cidade, "UF": uf, "TEL": tel, "EMAIL": email
            }).execute()
            st.success("Cliente salvo!"); time.sleep(1); st.rerun()
    st.divider()
    st.dataframe(df_c, use_container_width=True)

# --- CADASTRO DE PRODUTOS ---
elif menu == "📦 Cadastro Produtos":
    st.header("📦 Inclusão de Produtos")
    with st.form("pro_form", clear_on_submit=True):
        desc = st.text_input("Descrição do Produto")
        c1, c2, c3 = st.columns(3)
        uni = c1.text_input("Unidade (UN, PC, KG)", value="UN")
        est = c2.number_input("Estoque Inicial", value=0)
        prc = c3.number_input("Preço de Venda (R$)", value=0.0, step=1.0)
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            supabase.table("produtos").insert({"descricao": desc, "unidade": uni, "estoque": est, "p_venda": prc}).execute()
            st.success("Produto salvo!"); time.sleep(1); st.rerun()
    st.divider()
    st.dataframe(df_p, use_container_width=True)

# --- CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    st.header("⚙️ Dados da Empresa")
    with st.form("conf_form"):
        st.subheader("Dados da Derlyana")
        nome_e = st.text_input("Nome da Empresa", value=emp.get('nome',''))
        cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj',''))
        logo_e = st.file_uploader("Logo (PNG)", type=["png"])
        st.subheader("Endereço e Contato")
        rua_e = st.text_input("Endereço/Rua", value=emp.get('end',''))
        c1, c2, c3 = st.columns(3)
        cid_e = c1.text_input("Cidade", value=emp.get('cidade',''))
        uf_e = c2.text_input("UF", value=emp.get('uf','CE'))
        tel_e = c3.text_input("Telefone", value=emp.get('tel',''))
        if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
            l64 = emp.get('logo_base64', '')
            if logo_e:
                l64 = f"data:image/png;base64,{base64.b64encode(logo_e.read()).decode('utf-8')}"
            supabase.table("config").upsert({
                "id": 1, "nome": nome_e, "cnpj": cnpj_e, "logo_base64": l64,
                "end": rua_e, "cidade": cid_e, "uf": uf_e, "tel": tel_e
            }).execute()
            st.success("Configuração salva!"); time.sleep(1); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO SISTEMA"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        supabase.table("config").delete().eq("id", 1).execute()
        st.rerun()
