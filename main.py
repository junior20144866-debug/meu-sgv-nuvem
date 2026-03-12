# --- FUNÇÃO COM TODOS OS PRODUTOS DO PDF ---
def importar_todos_produtos_pdf():
    # Mapeamento completo baseado no seu documento PDF
    lista_produtos = [
        {"ean13": "00027", "descricao": "CAJUÍNA 200 ML (FARDO 24 UN)", "unidade": "CX", "preco_venda": 60.00, "estoque_atual": 30.0},
        {"ean13": "00028", "descricao": "CAJUINA 480 ML (FARDO 12 UN)", "unidade": "PC", "preco_venda": 55.00, "estoque_atual": 0.0},
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
    
    sucesso = 0
    erro = 0
    for prod in lista_produtos:
        try:
            # Upsert garante que se o código existir, ele apenas atualiza
            supabase.table("produtos").upsert(prod).execute()
            sucesso += 1
        except Exception as e:
            erro += 1
    
    st.success(f"🚀 Importação concluída: {sucesso} produtos inseridos/atualizados!")
    if erro > 0: st.warning(f"⚠️ {erro} produtos falharam na importação.")

# --- NA INTERFACE (ABA IMPORTAR) ---
elif menu == f"📑 {T['import']}":
    st.header(f"📑 {T['import']}")
    st.subheader("Importar Catálogo Derlyana Alimentos")
    st.write("Clique no botão abaixo para carregar todos os produtos do PDF automaticamente para o sistema.")
    
    if st.button("🚀 Executar Importação Completa"):
        importar_todos_produtos_pdf()
