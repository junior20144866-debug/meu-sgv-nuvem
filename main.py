import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO DIRETA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ Sistemas", layout="wide")

# --- 2. ACESSO RESTRITO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 JMQJ Sistemas</h2>", unsafe_allow_html=True)
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("LIGAR MOTOR", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Acesso negado.")
    st.stop()

# --- 3. MOTOR DE DADOS ---
def carregar_tudo():
    try:
        e = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("NOM").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(cl)
    except:
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_tudo()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Operação:** {emp.get('nome', 'Padrão')}")
    st.write("---")
    menu = st.radio("MÓDULOS", ["📊 Painel", "🧾 Pedido/Venda", "👥 Clientes", "📦 Produtos", "⚙️ Ajustes"])

# --- MODULO CLIENTES (INSERÇÃO MANUAL PURA) ---
if menu == "👥 Clientes":
    st.header("👥 Gestão Manual de Clientes")
    with st.form("f_cli", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome/Razão Social (NOM)")
        cpf = c2.text_input("CPF/CNPJ")
        rua = st.text_input("Rua/Logradouro")
        c3, c4, c5 = st.columns([2,2,1])
        bai = c3.text_input("Bairro")
        cep = c4.text_input("CEP")
        cid = st.text_input("Cidade")
        uf = c5.text_input("UF", max_chars=2)
        tel = st.text_input("Telefone/WhatsApp")
        email = st.text_input("E-mail")
        
        if st.form_submit_button("💾 SALVAR NO BANCO"):
            try:
                # Tentamos gravar exatamente o que você digitou
                payload = {
                    "NOM": nome, "CPF": cpf, "RUA": rua, "BAI": bai,
                    "CEP": cep, "CIDADE": cid, "UF": uf, "TEL": tel, "EMAIL": email
                }
                supabase.table("Clientes").insert(payload).execute()
                st.success("✅ Gravado com sucesso!")
                time.sleep(1); st.rerun()
            except Exception as e:
                st.error(f"❌ Erro na gravação: {e}")

# --- MODULO PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Gestão Manual de Produtos")
    with st.form("f_prod", clear_on_submit=True):
        desc = st.text_input("Descrição do Produto")
        c1, c2, c3 = st.columns(3)
        uni = c1.text_input("Unidade (UN/KG)")
        est = c2.number_input("Estoque", value=0)
        prc = c3.number_input("Preço de Venda (R$)", value=0.0)
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            try:
                supabase.table("produtos").insert({
                    "descricao": desc, "unidade": uni, "estoque": est, "p_venda": prc
                }).execute()
                st.success("✅ Produto Salvo!")
                time.sleep(1); st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

# --- MODULO PEDIDO (IMPRESSÃO A5) ---
elif menu == "🧾 Pedido/Venda":
    st.header("🧾 Emissão de Documento")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre dados manualmente primeiro.")
    else:
        with st.form("venda"):
            c_sel = st.selectbox("Cliente", df_c['NOM'].tolist())
            p_sel = st.selectbox("Produto", df_p['descricao'].tolist())
            qtd = st.number_input("Qtd", min_value=1)
            desc = st.number_input("Desconto R$", value=0.0)
            acre = st.number_input("Acréscimo R$", value=0.0)
            if st.form_submit_button("GERAR PEDIDO"):
                cli_d = df_c[df_c['NOM'] == c_sel].iloc[0]
                pro_d = df_p[df_p['descricao'] == p_sel].iloc[0]
                total = (pro_d['p_venda'] * qtd) - desc + acre
                
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                    <h3 style="text-align:center;">JMQJ SISTEMAS - PEDIDO</h3>
                    <hr>
                    <p><b>EMPRESA:</b> {emp.get('nome', 'JMQJ')}</p>
                    <p><b>CLIENTE:</b> {cli_d['NOM']} | Tel: {cli_d.get('TEL','')}</p>
                    <p>End: {cli_d.get('RUA','')}, {cli_d.get('BAI','')}</p>
                    <hr>
                    <p>{pro_d['descricao']} | {qtd} x {pro_d['p_venda']} = R$ {pro_d['p_venda']*qtd:.2f}</p>
                    <p style="text-align:right">DESC: R$ {desc:.2f} | ACRE: R$ {acre:.2f}</p>
                    <h2 style="text-align:right">TOTAL: R$ {total:.2f}</h2>
                    <br><br><p style="text-align:center">________________________<br>Assinatura</p>
                </div>
                """, unsafe_allow_html=True)

# --- AJUSTES ---
elif menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações da sua Empresa")
    with st.form("f_conf"):
        nome_e = st.text_input("Nome da sua Empresa", value=emp.get('nome',''))
        cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj',''))
        tel_e = st.text_input("Telefone de Contato", value=emp.get('tel',''))
        logo = st.file_uploader("Sua Logo (PNG)", type=["png"])
        if st.form_submit_button("💾 FIXAR CONFIGURAÇÕES"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({
                "id": 1, "nome": nome_e, "cnpj": cnpj_e, "tel": tel_e, "logo_base64": l64
            }).execute()
            st.success("Configuração Fixada!"); st.rerun()
    st.divider()
    if st.button("🔥 ZERAR TUDO (RESET)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

elif menu == "📊 Painel":
    st.metric("Clientes", len(df_c))
    st.metric("Produtos", len(df_p))
