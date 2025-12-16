import streamlit as st
import pandas as pd
from datetime import date

# --- Configuração da Página ---
st.set_page_config(page_title="Meu Financeiro", page_icon="💰", layout="centered")

# --- Título e Cabeçalho ---
st.title("💰 Controle Financeiro")
st.write(f"Hoje é dia: **{date.today().strftime('%d/%m/%Y')}**")

# --- Formulário de Entrada ---
with st.container(border=True):
    st.header("Adicionar Novo Gasto")
    
    with st.form("meu_form"):
        nome = st.text_input("Descrição (Ex: Padaria)")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Contas Fixas", "Outros"])
        data = st.date_input("Data do Gasto", date.today())
        
        # Botão de salvar
        submit_button = st.form_submit_button("✅ Salvar Despesa")

        if submit_button:
            # Por enquanto, apenas mostra na tela que funcionou
            st.success(f"Gasto de R$ {valor:.2f} em {categoria} salvo com sucesso!")
            st.info("No próximo passo conectaremos isso ao Google Sheets!")

# --- Visualização Rápida (Exemplo) ---
st.divider()
st.subheader("📊 Histórico Recente (Exemplo)")

# Criando dados falsos só para você ver como fica a tabela
dados_exemplo = {
    "Data": ["10/12/2023", "11/12/2023"],
    "Descrição": ["Supermercado", "Uber"],
    "Valor": [150.00, 24.90],
    "Categoria": ["Alimentação", "Transporte"]
}
df = pd.DataFrame(dados_exemplo)
st.dataframe(df, use_container_width=True)
