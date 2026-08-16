import streamlit as st
import pandas as pd
from PIL import Image
import io

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E IDENTIDADE VISUAL
# ==========================================
st.set_page_config(page_title="Saya Beads ERP", page_icon="🎨", layout="wide")

# CSS Personalizado com a Paleta da Saya Beads
st.markdown("""
    <style>
    /* Cores da Marca:
       Fundo Geral: #E6DFD5 (Creme)
       Cards/Containers: #FFF5E8 (Branco Quente)
       Destaques: #EAB890 (Pêssego), #E49872 (Coral), #CF605B (Coral Escuro)
    */
    .stApp {
        background-color: #E6DFD5;
        color: #4A3E3D;
    }
    
    /* Titulos e Cabeçalhos */
    h1, h2, h3 {
        color: #CF605B !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Cards de Produtos */
    .product-card {
        background-color: #FFF5E8;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        border: 2px solid #EAB890;
        margin-bottom: 20px;
    }
    
    .badge-size {
        background-color: #E49872;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Estilização dos Botões */
    .stButton>button {
        background-color: #CF605B !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #E49872 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
# ==========================================
if 'produtos' not in st.session_state:
    st.session_state.produtos = []

if 'insumos' not in st.session_state:
    st.session_state.insumos = [
        {"Item": "Argola para Chaveiro", "Categoria": "Ferragem", "Estoque (Unid.)": 200, "Custo Unid. (R$)": 0.25},
        {"Item": "Mã de Neodímio/Manta", "Categoria": "Ímã", "Estoque (Unid.)": 150, "Custo Unid. (R$)": 0.50},
        {"Item": "Saquinho Embalagem", "Categoria": "Embalagem", "Estoque (Unid.)": 300, "Custo Unid. (R$)": 0.15},
        {"Item": "Adesivo Mimo", "Categoria": "Mimos", "Estoque (Unid.)": 100, "Custo Unid. (R$)": 0.30},
    ]

# ==========================================
# TOPO COM LOGO E TÍTULO
# ==========================================
col_header1, col_header2 = st.columns([1, 5])
with col_header1:
    st.markdown("### 🎨 **saya beads**")
with col_header2:
    st.title("Sistema de Gestão & Estoque")

st.divider()

# ==========================================
# NAVEGAÇÃO
# ==========================================
menu = st.sidebar.radio(
    "📍 Menu Principal", 
    ["🖼️ Galeria de Produtos", "➕ Cadastrar Produto", "📦 Insumos Extras", "🧮 Calculadora & Ficha Técnica", "📊 Importar Vendas Shopee"]
)

# ------------------------------------------
# TELA 1: GALERIA DE PRODUTOS (COM FOTO)
# ------------------------------------------
if menu == "🖼️ Galeria de Produtos":
    st.subheader("🖼️ Catálogo & Estoque de Produtos Prontos")
    
    if not st.session_state.produtos:
        st.info("Nenhum produto cadastrado ainda! Vá no menu '➕ Cadastrar Produto' para adicionar o primeiro.")
    else:
        # Exibição em Grid de Cards Visuais (3 por linha)
        cols = st.columns(3)
        for idx, prod in enumerate(st.session_state.produtos):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <h4>{prod['nome']}</h4>
                    <span class="badge-size">{prod['tamanho']}</span> | <b>{prod['tipo']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                # Exibe a Foto do Produto se existir
                if prod['foto'] is not None:
                    st.image(prod['foto'], use_column_width=True)
                else:
                    st.caption("📷 *Sem foto cadastrada*")
                
                c1, c2 = st.columns(2)
                c1.metric("Estoque", f"{prod['estoque']} unid.")
                c2.metric("Preço Shopee", f"R$ {prod['preco']:.2f}")
                st.caption(f"Custo de produção: R$ {prod['custo']:.2f}")
                st.divider()

# ------------------------------------------
# TELA 2: CADASTRO DE PRODUTO COM FOTO
# ------------------------------------------
elif menu == "➕ Cadastrar Produto":
    st.subheader("➕ Novo Cadastro de Produto")
    
    with st.form("form_novo_produto", clear_on_submit=True):
        col_f1, col_f2 = st.columns([2, 1])
        
        with col_f1:
            nome = st.text_input("Nome do Produto / Arte", placeholder="Ex: Chaveiro Coração Pixel, Ímã Gato Pacman")
            tipo = st.selectbox("Tipo de Produto", ["Chaveiro", "Ímã", "Peça Individual (Sem montagem)"])
            tamanho = st.selectbox("Tamanho da Peça", ["Mini", "Pequeno", "Médio", "Grande"])
            
            c_a, c_b, c_c = st.columns(3)
            estoque = c_a.number_input("Estoque Inicial (Unidades)", min_value=0, value=10)
            custo = c_b.number_input("Custo Estimado (R$)", min_value=0.0, value=3.50, step=0.50)
            preco = c_c.number_input("Preço na Shopee (R$)", min_value=0.0, value=15.00, step=1.00)
            
        with col_f2:
            st.write("📷 **Foto do Produto**")
            foto_file = st.file_uploader("Escolha a imagem (JPG/PNG)", type=["jpg", "jpeg", "png"])
            foto_img = None
            if foto_file is not None:
                foto_img = Image.open(foto_file)
                st.image(foto_img, caption="Pré-visualização", use_column_width=True)
                
        submitted = st.form_submit_button("Salvar Produto no ERP")
        if submitted:
            if nome.strip() == "":
                st.error("Por favor, digite o nome do produto!")
            else:
                novo_prod = {
                    "nome": nome,
                    "tipo": tipo,
                    "tamanho": tamanho,
                    "estoque": estoque,
                    "custo": custo,
                    "preco": preco,
                    "foto": foto_img
                }
                st.session_state.produtos.append(novo_prod)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")

# ------------------------------------------
# TELA 3: INSUMOS EXTRAS (ARGOLAS, PACOTES)
# ------------------------------------------
elif menu == "📦 Insumos Extras":
    st.subheader("📦 Materiais Secundários (Ferragens, Embalagens, Mimos)")
    df_insumos = pd.DataFrame(st.session_state.insumos)
    st.dataframe(df_insumos, use_container_width=True)
    
    with st.expander("➕ Adicionar Novo Insumo"):
        with st.form("form_insumo"):
            item_nome = st.text_input("Nome do Insumo (Ex: Mosquetão Dourado)")
            cat = st.text_input("Categoria (Ex: Ferragem, Embalagem, Mimo)")
            qtd = st.number_input("Quantidade Comprada", min_value=1, value=100)
            custo_u = st.number_input("Custo por Unidade (R$)", min_value=0.0, value=0.20, step=0.05)
            
            if st.form_submit_button("Adicionar Insumo"):
                st.session_state.insumos.append({
                    "Item": item_nome, "Categoria": cat, "Estoque (Unid.)": qtd, "Custo Unid. (R$)": custo_u
                })
                st.success("Insumo adicionado!")
                st.rerun()

# ------------------------------------------
# TELA 4: CALCULADORA DE PREÇO & MARGEM
# ------------------------------------------
elif menu == "🧮 Calculadora & Ficha Técnica":
    st.subheader("🧮 Simulador de Precificação para a Shopee")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.markdown("##### 1. Custos de Produção")
        qtd_beads = st.number_input("Quantidade aproximada de Beads na arte", min_value=1, value=150)
        custo_bead_unitario = 0.015  # Média de R$ 0,015 por bead
        custo_beads_total = qtd_beads * custo_bead_unitario
        
        custo_extras = st.number_input("Custo de Insumos Extras (Argola, Embalagem, Mimo) R$", min_value=0.0, value=0.80)
        custo_total_peca = custo_beads_total + custo_extras
        
        st.info(f"💡 Custo Total Estimado da Peça: **R$ {custo_total_peca:.2f}**")
        
    with col_calc2:
        st.markdown("##### 2. Simulação Shopee")
        preco_venda_sim = st.number_input("Preço de Venda Pretendido (R$)", min_value=0.0, value=18.00)
        
        taxa_shopee_pct = st.slider("Comissão da Shopee (%)", min_value=0, max_value=30, value=20) / 100
        taxa_fixa = 4.00  # Taxa fixa por item vendido da Shopee
        
        taxa_total = (preco_venda_sim * taxa_shopee_pct) + taxa_fixa
        lucro_liquido = preco_venda_sim - custo_total_peca - taxa_total
        margem = (lucro_liquido / preco_venda_sim * 100) if preco_venda_sim > 0 else 0
        
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Taxas Totais Shopee", f"R$ {taxa_total:.2f}")
        m2.metric("Lucro Líquido", f"R$ {lucro_liquido:.2f}", delta=f"{margem:.1f}% Margem")

# ------------------------------------------
# TELA 5: IMPORTADOR SHOPEE
# ------------------------------------------
elif menu == "📊 Importar Vendas Shopee":
    st.subheader("📊 Importação da Planilha de Vendas da Shopee")
    st.write("Baixe a planilha de pedidos no *Painel do Vendedor da Shopee* (arquivo `.xlsx` ou `.csv`) e envie aqui para dar baixa automática no estoque.")
    
    file_shopee = st.file_uploader("Selecione o arquivo da Shopee", type=["csv", "xlsx"])
    if file_shopee is not None:
        st.success("Planilha carregada com sucesso! (Em breve integrado com atualização automática do inventário).")
