import sqlite3
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão Financeira Familiar", page_icon="💰", layout="centered"
)


# Função para criar o banco de dados e atualizar a tabela com categoria
def init_db():
  conn = sqlite3.connect("financeiro.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            membro TEXT,
            tipo TEXT,
            valor REAL,
            categoria TEXT,
            descricao TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

st.title("💰 Gestão Financeira Familiar")
st.write(
    "Controle inteligente do orçamento da família para a nossa Atividade"
    " Extensionista."
)

# Formulário de Cadastro
with st.form("form_transacao", clear_on_submit=True):
  st.subheader("Adicionar Nova Movimentação")

  col1, col2 = st.columns(2)
  with col1:
    membro = st.selectbox(
        "Membro da Família", ["Pai", "Mãe", "Filho(a)", "Outro"]
    )
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
  with col2:
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    # Lista de categorias inteligentes
    categoria = st.selectbox(
        "Categoria",
        [
            "Salário/Renda",
            "Alimentação",
            "Moradia",
            "Transporte",
            "Lazer",
            "Saúde",
            "Outros",
        ],
    )

  descricao = st.text_input("Descrição (Ex: Supermercado, Conta de Luz)")

  submitted = st.form_submit_button("Salvar Movimentação")

  if submitted:
    if valor > 0 and descricao:
      conn = sqlite3.connect("financeiro.db")
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO transacoes (membro, tipo, valor, categoria, descricao)"
          " VALUES (?, ?, ?, ?, ?)",
          (membro, tipo, valor, categoria, descricao),
      )
      conn.commit()
      conn.close()
      st.success(
          f"Transação de R$ {valor:.2f} ({tipo} - {categoria}) salva com"
          f" sucesso!"
      )
      st.rerun()
    else:
      st.error("Por favor, insira um valor válido e a descrição.")

# Buscar dados do banco
conn = sqlite3.connect("financeiro.db")
cursor = conn.cursor()
cursor.execute(
    "SELECT id, membro, tipo, valor, categoria, descricao FROM transacoes"
)
dados = cursor.fetchall()
conn.close()

# Cálculos financeiros
total_receitas = sum(item[3] for item in dados if item[2] == "Receita")
total_despesas = sum(item[3] for item in dados if item[2] == "Despesa")
saldo_final = total_receitas - total_despesas

st.divider()

# Painel de Resumo
st.subheader("📊 Resumo do Orçamento Familiar")

col_r, col_d, col_s = st.columns(3)
col_r.metric(label="🟢 Total de Receitas", value=f"R$ {total_receitas:.2f}")
col_d.metric(label="🔴 Total de Despesas", value=f"R$ {total_despesas:.2f}")

if saldo_final > 0:
  col_s.metric(
      label="💰 Vai Sobrar", value=f"R$ {saldo_final:.2f}", delta="Positivo"
  )
elif saldo_final < 0:
  col_s.metric(
      label="⚠️ Vai Faltar",
      value=f"R$ {abs(saldo_final):.2f}",
      delta="Negativo",
      delta_color="inverse",
  )
else:
  col_s.metric(label="⚖️ Saldo Zerado", value="R$ 0.00", delta="Neutro")

st.divider()

# Exibição detalhada com categorias e botão de excluir
st.subheader("📋 Detalhamento e Correção de Movimentações")

col_tab1, col_tab2 = st.columns(2)

with col_tab1:
  st.markdown("### 🟢 Entradas (Receitas)")
  receitas_lista = [item for item in dados if item[2] == "Receita"]
  if receitas_lista:
    for item in receitas_lista:
      id_transacao, membro, tipo, valor, cat, desc = item
      c_texto, c_btn = st.columns([4, 1])
      c_texto.write(
          f"**{membro}** ({cat}): R$ {valor:.2f} (*{desc}*)"
      )
      if c_btn.button("❌", key=f"del_{id_transacao}", help="Excluir item"):
        conn = sqlite3.connect("financeiro.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
        conn.commit()
        conn.close()
        st.rerun()
  else:
    st.info("Nenhuma receita cadastrada.")

with col_tab2:
  st.markdown("### 🔴 Saídas (Despesas)")
  despesas_lista = [item for item in dados if item[2] == "Despesa"]
  if despesas_lista:
    for item in despesas_lista:
      id_transacao, membro, tipo, valor, cat, desc = item
      c_texto, c_btn = st.columns([4, 1])
      c_texto.write(
          f"**{membro}** ({cat}): R$ {valor:.2f} (*{desc}*)"
      )
      if c_btn.button("❌", key=f"del_{id_transacao}", help="Excluir item"):
        conn = sqlite3.connect("financeiro.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
        conn.commit()
        conn.close()
        st.rerun()
  else:
    st.info("Nenhuma despesa cadastrada.")