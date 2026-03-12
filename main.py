import streamlit as st
import pandas as pd

# --- LISTA COMPLETA EXTRAÍDA DO SEU PDF (MAPEADA) ---
PRODUTOS_PDF = [
    {"ean13": "00027", "descricao": "CAJUÍNA 200 ML (24 UN)", "unidade": "CX", "preco_venda": 60.00, "estoque_atual": 30.0},
    {"ean13": "00028", "descricao": "CAJUINA 480 ML (12 UN)", "unidade": "PC", "preco_venda": 55.00, "estoque_atual": 0.0},
    {"ean13": "00025", "descricao": "POLPA ABACAXI C/HORTELA (500G)", "unidade": "PC", "preco_venda": 8.00, "estoque_atual": 0.0},
    {"ean13": "00001", "descricao": "POLPA DE ABACAXI (KG)", "unidade": "KG", "preco_venda": 14.00, "estoque_atual": 11.0},
    {"ean13": "00009", "descricao": "POLPA DE ABACAXI (500G)", "unidade": "PC", "preco_venda": 7.00, "estoque_atual": 0.0},
    {"ean13": "00002", "descricao": "POLPA DE ACEROLA (KG)", "unidade": "KG", "preco_venda": 12.00, "estoque_atual": 19.0},
    {"ean13": "00010", "descricao": "POLPA DE ACEROLA (500G)", "unidade": "PC", "preco_venda": 6.00, "estoque_atual": 0.0},
    {"ean13": "00011", "descricao": "POLPA DE AMEIXA (500G)", "unidade": "PC", "preco_venda": 7.50, "estoque_atual": 0.0},
    {"ean13": "00012", "descricao": "POLPA DE AÇAÍ (500G)", "unidade": "PC", "preco_venda": 10.90, "estoque_atual": 0.0},
    {"ean13": "00003", "descricao": "POLPA DE CAJU (KG)", "unidade": "KG", "preco_venda": 9.50, "estoque_atual": 20.0},
    {"ean13": "00014", "descricao": "POLPA DE CAJU (500G)", "unidade": "PC", "preco_venda": 4.75, "estoque_atual": 0.0},
    {"ean13": "00004", "descricao": "POLPA DE CAJÁ (KG)", "unidade": "KG", "preco_venda": 15.00, "estoque_atual": 20.0},
    {"ean13": "00013", "descricao": "POLPA DE CAJÁ (500G)", "unidade": "PC", "preco_venda": 7.50, "estoque_atual": 0.0},
    {"ean13": "00015", "descricao": "POLPA DE CUPUAÇU (500G)", "unidade": "PC", "preco_venda": 8.00, "estoque_atual": 0.0},
    {"ean13": "00005", "descricao": "POLPA DE GOIABA (KG)", "unidade": "KG", "preco_venda": 12.00, "estoque_atual": 16.0},
    {"ean13": "00016", "descricao": "POLPA DE GOIABA (500G)", "unidade": "PC", "preco_venda": 6.00, "estoque_atual": 0.0},
    {"ean13": "00006", "descricao": "POLPA DE GRAVIOLA (KG)", "unidade": "KG", "preco_venda": 15.00, "estoque_atual": 8.0},
    {"ean13": "00017", "descricao": "POLPA DE GRAVIOLA (500G)", "unidade": "PC", "preco_venda": 7.50, "estoque_atual": 0.0},
    {"ean13": "00007", "descricao": "POLPA DE MANGA (KG)", "unidade": "KG", "preco_venda": 11.00, "estoque_atual": 15.0},
    {"ean13": "00018", "descricao": "POLPA DE MANGA (500G)", "unidade": "PC", "preco_venda": 5.50, "estoque_atual": 0.0},
    {"ean13": "00008", "descricao": "POLPA DE MARACUJÁ (KG)", "unidade": "KG", "preco_venda": 22.00, "estoque_atual": 2.0},
    {"ean13": "00019", "descricao": "POLPA DE MARACUJÁ (500G)", "unidade": "PC", "preco_venda": 11.00, "estoque_atual": 0.0},
    {"ean13": "00021", "descricao": "POLPA DE MORANGO (500G)", "unidade": "PC", "preco_venda": 8.50, "estoque_atual": 0.0},
    {"ean13": "00020", "descricao": "POLPA DE TAMARINDO (500G)", "unidade": "PC", "preco_venda": 6.50, "estoque_atual": 0.0},
    {"ean13": "00022", "descricao": "POLPA DE UMBU (500G)", "unidade": "PC", "preco_venda": 6.50, "estoque_atual": 0.0}
]

# --- ABA DE IMPORTAÇÃO (SUBSTITUA ESTA PARTE NO SEU CÓDIGO) ---
elif menu == f"📑 {T['import']}":
    st.header("📑 Central de Importação")
    
    st.info("Os dados do PDF 'Derlyana Alimentos' já foram mapeados e estão prontos para serem inseridos no seu banco de dados.")
    
    # Mostra uma prévia para o usuário não ficar no escuro
    with st.expander("🔍 Ver produtos que serão importados"):
        st.table(pd.DataFrame(PRODUTOS_PDF))
    
    if st.button("🚀 EXECUTAR IMPORTAÇÃO COMPLETA"):
        progresso = st.progress(0)
        total = len(PRODUTOS_PDF)
        
        for i, produto in enumerate(PRODUTOS_PDF):
            # Upsert evita duplicados se o EAN13 for o mesmo
            supabase.table("produtos").upsert(produto).execute()
            progresso.progress((i + 1) / total)
            
        st.success(f"✅ Sucesso! {total} produtos estão agora no seu estoque.")
        st.balloons()
