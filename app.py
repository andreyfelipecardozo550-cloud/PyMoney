
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DE PÁGINA E ESTILO
# ==============================================================================
st.set_page_config(
    page_title="Controle Financeiro Pessoal",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada (Opcional, para refinar o Dark Mode)
st.markdown("""
    <style>
    /* Ajustes globais para um visual mais limpo */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Estilo dos Cards de KPI */
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #4f4f4f;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }

    /* Cores específicas para métricas */
    div[data-testid="metric-container"] label {
        color: #b0b0b0; /* Cor do rótulo */
    }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# GERENCIAMENTO DE DADOS (SESSION STATE)
# ==============================================================================
# AQUI CONECTAREMOS O GOOGLE SHEETS DEPOIS
if 'data' not in st.session_state:
    # Dados fictícios para inicialização e teste
    data_ficticia = [
        {"Data": datetime(2023, 10, 1), "Descrição": "Salário Mensal", "Categoria": "Receita", "Tipo": "Entrada", "Valor": 5000.00, "Pagamento": "Pix"},
        {"Data": datetime(2023, 10, 5), "Descrição": "Aluguel", "Categoria": "Habitação", "Tipo": "Saída", "Valor": 1500.00, "Pagamento": "Boleto"},
        {"Data": datetime(2023, 10, 10), "Descrição": "Supermercado", "Categoria": "Alimentação", "Tipo": "Saída", "Valor": 600.00, "Pagamento": "Crédito"},
        {"Data": datetime(2023, 10, 15), "Descrição": "Gasolina", "Categoria": "Transporte", "Tipo": "Saída", "Valor": 250.00, "Pagamento": "Débito"},
        {"Data": datetime(2023, 10, 20), "Descrição": "Cinema e Jantar", "Categoria": "Lazer", "Tipo": "Saída", "Valor": 300.00, "Pagamento": "Crédito"},
        {"Data": datetime(2023, 11, 1), "Descrição": "Salário Mensal", "Categoria": "Receita", "Tipo": "Entrada", "Valor": 5000.00, "Pagamento": "Pix"},
        {"Data": datetime(2023, 11, 5), "Descrição": "Aluguel", "Categoria": "Habitação", "Tipo": "Saída", "Valor": 1500.00, "Pagamento": "Boleto"},
    ]
    st.session_state['data'] = pd.DataFrame(data_ficticia)

# Função auxiliar para salvar (neste caso, apenas no session_state)
def save_data(new_entry):
    new_df = pd.DataFrame([new_entry])
    st.session_state['data'] = pd.concat([st.session_state['data'], new_df], ignore_index=True)


# ==============================================================================
# BARRA LATERAL (NAVEGAÇÃO E FILTROS)
# ==============================================================================
st.sidebar.title("💰 Finanças App")
st.sidebar.markdown("---")

# Menu de Navegação
menu_options = ["Dashboard", "Lançamentos", "Tabela de Dados"]
choice = st.sidebar.radio("Navegação", menu_options)

st.sidebar.markdown("---")

# ==============================================================================
# LÓGICA DAS PÁGINAS
# ==============================================================================

# DF Principal
df = st.session_state['data']
df['Data'] = pd.to_datetime(df['Data']) # Garantir formato data
df['Mês'] = df['Data'].dt.month
df['Ano'] = df['Data'].dt.year

# ------------------------------------------------------------------------------
# PÁGINA 1: DASHBOARD
# ------------------------------------------------------------------------------
if choice == "Dashboard":
    st.title("📊 Visão Geral Financeira")

    # Filtros da Sidebar (Apenas para Dashboard)
    st.sidebar.subheader("Filtros do Dashboard")
    
    # Filtro de Ano
    years = sorted(df['Ano'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Selecione o Ano", years, index=0)
    
    # Filtro de Mês
    months_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
                  7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    month_options = ["Todos"] + list(months_map.values())
    selected_month_name = st.sidebar.selectbox("Selecione o Mês", month_options, index=0)

    # Aplicando Filtros
    df_filtered = df[df['Ano'] == selected_year]
    if selected_month_name != "Todos":
        # Encontrar número do mês
        selected_month_num = [k for k, v in months_map.items() if v == selected_month_name][0]
        df_filtered = df_filtered[df_filtered['Mês'] == selected_month_num]

    # --- KPIs ---
    if not df_filtered.empty:
        receitas = df_filtered[df_filtered['Tipo'] == 'Entrada']['Valor'].sum()
        despesas = df_filtered[df_filtered['Tipo'] == 'Saída']['Valor'].sum()
        saldo = receitas - despesas
        
        # Evitar divisão por zero
        economia_percent = ((receitas - despesas) / receitas * 100) if receitas > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta_color="normal")
        col2.metric("Receitas", f"R$ {receitas:,.2f}", delta=f"R$ {receitas:,.2f}", delta_color="normal") # Delta verde se positivo
        col3.metric("Despesas", f"R$ {despesas:,.2f}", delta=f"- R$ {despesas:,.2f}", delta_color="inverse") # Delta vermelho se subir
        col4.metric("Economia", f"{economia_percent:.1f}%")
    else:
        st.warning("Sem dados para o período selecionado.")

    st.markdown("---")

    # --- GRÁFICOS ---
    if not df_filtered.empty:
        col_g1, col_g2 = st.columns([1, 1])

        # Gráfico 1: Despesas por Categoria (Rosca)
        with col_g1:
            st.subheader("Gastos por Categoria")
            df_despesas = df_filtered[df_filtered['Tipo'] == 'Saída']
            if not df_despesas.empty:
                fig_rosca = px.pie(
                    df_despesas, 
                    values='Valor', 
                    names='Categoria', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_rosca, use_container_width=True)
            else:
                st.info("Sem despesas neste período.")

        # Gráfico 2: Receita vs Despesa (Barras)
        # Nota: Se filtrar por "Todos" os meses, mostra a evolução. Se for 1 mês, mostra apenas ele.
        with col_g2:
            st.subheader("Receitas vs Despesas")
            # Agrupar por Mês e Tipo
            df_bar_chart = df_filtered.groupby(['Mês', 'Tipo'])['Valor'].sum().reset_index()
            # Mapear número do mês para nome para melhor visualização no eixo X
            df_bar_chart['Nome Mês'] = df_bar_chart['Mês'].map(months_map)
            
            fig_barras = px.bar(
                df_bar_chart, 
                x="Nome Mês", 
                y="Valor", 
                color="Tipo", 
                barmode="group",
                color_discrete_map={"Entrada": "#00CC96", "Saída": "#EF553B"}, # Verde e Vermelho
                text_auto='.2s'
            )
            st.plotly_chart(fig_barras, use_container_width=True)

        # Gráfico 3: Linha do Tempo de Saldo Acumulado
        st.subheader("Evolução do Saldo")
        # Para saldo acumulado, idealmente pegamos tudo até a data atual, mas vamos mostrar a evolução dentro do filtro
        df_line = df_filtered.sort_values(by="Data")
        # Criar coluna de valor com sinal (Despesa negativa)
        df_line['Valor_Real'] = df_line.apply(lambda x: x['Valor'] if x['Tipo'] == 'Entrada' else -x['Valor'], axis=1)
        df_line['Saldo Acumulado'] = df_line['Valor_Real'].cumsum()
        
        fig_line = px.line(
            df_line, 
            x="Data", 
            y="Saldo Acumulado", 
            markers=True,
            line_shape='spline' # Linha suavizada
        )
        # Pintar a linha de azul
        fig_line.update_traces(line_color='#636EFA') 
        st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------------------------------------------
# PÁGINA 2: LANÇAMENTOS
# ------------------------------------------------------------------------------
elif choice == "Lançamentos":
    st.title("📝 Novo Lançamento")
    
    with st.form("form_lancamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            data = st.date_input("Data do Lançamento", datetime.now())
            descricao = st.text_input("Descrição", placeholder="Ex: Mercado, Salário...")
            tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
        
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
            categoria = st.selectbox("Categoria", [
                "Alimentação", "Transporte", "Habitação", "Lazer", 
                "Saúde", "Educação", "Receita", "Investimento", "Outros"
            ])
            pagamento = st.selectbox("Forma de Pagamento", ["Crédito", "Débito", "Dinheiro", "Pix", "Boleto"])
        
        submitted = st.form_submit_button("💾 Salvar Lançamento")
        
        if submitted:
            if not descricao:
                st.error("Por favor, insira uma descrição.")
            else:
                novo_lancamento = {
                    "Data": pd.to_datetime(data),
                    "Descrição": descricao,
                    "Categoria": categoria,
                    "Tipo": tipo,
                    "Valor": valor,
                    "Pagamento": pagamento
                }
                save_data(novo_lancamento)
                st.success("Lançamento salvo com sucesso!")

# ------------------------------------------------------------------------------
# PÁGINA 3: TABELA DE DADOS
# ------------------------------------------------------------------------------
elif choice == "Tabela de Dados":
    st.title("📂 Base de Dados Detalhada")
    
    # Opção de download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name='financas_pessoais.csv',
        mime='text/csv',
    )
    
    # Editor de dados (permite edição básica na tabela visual)
    st.markdown("Visualização completa dos registros:")
    st.dataframe(
        df.sort_values(by="Data", ascending=False), # Mostrar mais recentes primeiro
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
        }
    )
