import streamlit as st
import pandas as pd
from PIL import Image
import os

# ==========================================
# 1. CONFIGURAÇÃO DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Saya Beads ERP",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DESIGN SYSTEM & CSS AVANÇADO (UX/UI)
# ==========================================
st.markdown("""
    <style>
    /* IMPORTAÇÃO DE FONTES GOOGLE */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300..800;1,300..800&family=Syne:wght@700;800&display=swap');

    /* PALETA SAYA BEADS:
       - Creme Fundo: #E6DFD5
       - Branco Quente: #FFF5E8
       - Pêssego: #EAB890
       - Coral Suave: #E49872
       - Terracota: #DB7F65
       - Coral Escuro: #CF605B
    */

    /* CONFIGURAÇÕES GERAIS DA PÁGINA */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        color: #3E3232;
    }

    .stApp {
        background-color: #E6DFD5;
    }

    /* TÍTULOS DESTAQUE (ESTILO BRASIKA / RETRO) */
    h1, h2, h3, .brand-title {
        font-family: 'Syne', 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        color: #CF605B !important;
        letter-spacing: -0.5px;
    }

    /* BARRA LATERAL (SIDEBAR) */
    section[data-testid="stSidebar"] {
        background-color: #FFF5E8 !important;
        border-right: 2px solid #EAB890;
    }

    section[data-testid="stSidebar"] .stRadio label {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        color: #5C4B49 !important;
        padding: 10px 14px;
        border-radius: 10px;
        transition: all 0.2s ease;
    }

    /* CARD CONTAINER PRINCIPAL */
    .saya-card {
        background-color: #FFF5E8;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 8px 20px rgba(207, 96, 91, 0.08);
        border: 1px solid #EAB890;
        margin-bottom: 25px;
    }

    /* PRODUCT CARDS (GALERIA) */
    .product-card-container {
        background-color: #FFF5E8;
        border-radius: 18px;
        padding: 16px;
        border: 2px solid #EAB890;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .product-card-container:hover {
        transform: translateY(-3px);
        box-shadow: 0px 8px 18px rgba(219, 127, 101, 0.15);
    }

    /* BADGES / TAGS DE TAMANHO E TIPO */
    .badge-tag {
        display: inline-block;
        background-color: #E49872;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-type {
        display: inline-block;
        background-color: #EAB890;
        color: #3E3232;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
    }

    /* ESTILIZAÇÃO DOS INPUTS E FORMULÁRIOS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        border-radius: 12px !important;
        border: 1.5px solid #EAB890 !important;
        background-color: #FFFFFF !important;
        color: #3E3232 !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #CF605B !important;
        box-shadow: 0 0 0 2px rgba(207, 96, 91, 0.2) !important;
    }

    /* BOTÕES CUSTOMIZADOS */
    .stButton>button {
        background: linear-gradient(135deg, #CF605B 0%, #DB7F65 100%) !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px 28px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0px 4px 10px rgba(207, 96, 91, 0.25) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #DB7F65 0%, #E49872 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0px 6px 14px rgba(207, 96, 91, 0.35) !important;
    }

    /* METRICS / INDICADORES */
    div[data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        color: #CF605B !important;
        font-weight: 800 !important;
    }

    div[data-testid="stMetricLabel"] {
        font-family: 'Montserrat', sans-serif !important;
        color: #5C4B49 !important;
        font-weight: 600 !important;
    }

    /* DIVISORES */
    hr {
        border-color: #EAB890 !important;
        opacity: 0.5;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BANCO DE DADOS EM MEMÓRIA
# ==========================================
if 'produtos' not in st.session_state:
    st.session_state.produtos = []

if 'insumos' not in st.session_state:
    st.session_state.insumos = [
        {"Item": "Argola de Chaveiro (Prata)", "Categoria": "Ferragem", "Estoque (Unid.)": 200, "Custo Unid. (R$)": 0.25},
        {"Item": "Manta Magnética / Ímã", "Categoria": "Ímã", "Estoque (Unid.)": 150, "Custo Unid. (R$)": 0.50},
        {"Item": "Saquinho PP Transparente", "Categoria": "Embalagem", "Estoque (Unid.)": 300, "Custo Unid. (R$)": 0.15},
        {"Item": "Adesivo Mimo Saya Beads", "Categoria": "Mimos", "Estoque (Unid.)": 100, "Custo Unid. (R$)": 0.30},
    ]

# ==========================================
# 4. CABEÇALHO / HEADER COM LOGO
# ==========================================
with st.container():
    col_logo, col_header = st.columns([1, 4])
    
    with col_logo:
        # Tenta carregar a imagem 'logo.png' se existir no diretório, senão usa ícone estilizado
        if os.path.exists("logo.png"):
            st.image("logo.png", width=130)
        else:
            st.markdown("""
                <div style="background-color: #FFF5E8; border: 2px solid #EAB890; border-radius: 18px; padding: 15px; text-align: center;">
                    <span style="font-size: 32px;">✨</span>
                    <div style="font-family: 'Syne', sans-serif; font-weight: 800; color: #CF605B; font-size: 14px; margin-top: 5px;">SAYA BEADS</div>
                </div>
            """, unsafe_allow_html=True)
            
    with col_header:
        st.markdown("<h1 style='margin-bottom: 0px;'>saya beads manager</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #7A6664; font-size: 15px; margin-top: -5px;'>Painel de Gestão, Produção & Estoque de Hama Beads</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 5. NAVEGAÇÃO LATERAL
# ==========================================
st.sidebar.markdown("### 📍 Navegação")
menu = st.sidebar.radio(
    "", 
    ["🖼️ Galeria de Produtos", "➕ Cadastrar Produto", "📦 Insumos Extras", "🧮 Calculadora & Ficha", "📊 Importar Shopee"]
)

st.sidebar.markdown("<br><hr>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center; color: #7A6664; font-size: 12px;'><b>Saya Beads</b> © 2025<br>Feito com amor & pixel art 🎨</div>", unsafe_allow_html=True)

# ------------------------------------------
# TELA 1: GALERIA DE PRODUTOS
# ------------------------------------------
if menu == "🖼️ Galeria de Produtos":
    st.markdown("<h2>🖼️ Galeria de Produtos Prontos</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5C4B49;'>Visão geral do seu estoque atual organizado visualmente.</p>", unsafe_allow_html=True)
    
    if not st.session_state.produtos:
        st.markdown("""
            <div class="saya-card" style="text-align: center; padding: 40px;">
                <span style="font-size: 48px;">📦</span>
                <h3 style="margin-top: 10px;">Nenhum produto cadastrado ainda</h3>
                <p style="color: #7A6664;">Vá no menu <b>'➕ Cadastrar Produto'</b> ao lado para adicionar a sua primeira arte de Hama Beads!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Filtros Rápidos
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            busca = st.text_input("🔍 Buscar produto pelo nome...", placeholder="Ex: Coração, Pacman, Gato")
        
        # Grid de Cards Visuais (3 por linha)
        prods_filtrados = [p for p in st.session_state.produtos if busca.lower() in p['nome'].lower()]
        
        cols = st.columns(3)
        for idx, prod in enumerate(prods_filtrados):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="product-card-container">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="badge-tag">{prod['tamanho']}</span>
                        <span class="badge-type">{prod['tipo']}</span>
                    </div>
                    <h4 style="margin: 8px 0px; font-family: 'Syne', sans-serif; color: #CF605B;">{prod['nome']}</h4>
                """, unsafe_allow_html=True)
                
                if prod['foto'] is not None:
                    st.image(prod['foto'], use_column_width=True)
                else:
                    st.markdown("""
                        <div style="background-color: #E6DFD5; height: 160px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #7A6664; font-size: 13px;">
                            📷 Sem foto cadastrada
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="margin-top: 12px; background-color: #FFFFFF; padding: 10px; border-radius: 12px; border: 1px solid #EAB890;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-size: 12px; color: #7A6664;">Estoque:</span>
                            <b style="color: #3E3232;">{prod['estoque']} unid.</b>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                            <span style="font-size: 12px; color: #7A6664;">Preço Shopee:</span>
                            <b style="color: #CF605B; font-size: 15px;">R$ {prod['preco']:.2f}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write("") # Espaçamento

# ------------------------------------------
# TELA 2: CADASTRO DE PRODUTO (UX REDESENHADA)
# ------------------------------------------
elif menu == "➕ Cadastrar Produto":
    st.markdown("<h2>➕ Novo Cadastro de Produto</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5C4B49;'>Preencha os detalhes abaixo para catalogar uma nova arte ou item na Saya Beads.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    
    with st.form("form_novo_produto", clear_on_submit=True):
        col_form_left, col_form_right = st.columns([1.4, 1])
        
        with col_form_left:
            st.markdown("<h4 style='color: #DB7F65; font-size: 16px;'>1. Informações Básicas</h4>", unsafe_allow_html=True)
            nome = st.text_input("Nome da Arte / Produto *", placeholder="Ex: Chaveiro Coração Pixel 8-bit")
            
            c_t1, c_t2 = st.columns(2)
            tipo = c_t1.selectbox("Tipo de Produto", ["Chaveiro", "Ímã", "Peça Individual (Sem montagem)"])
            tamanho = c_t2.selectbox("Tamanho da Peça", ["Mini", "Pequeno", "Médio", "Grande"])
            
            st.markdown("<h4 style='color: #DB7F65; font-size: 16px; margin-top: 15px;'>2. Estoque e Valores</h4>", unsafe_allow_html=True)
            c_v1, c_v2, c_v3 = st.columns(3)
            estoque = c_v1.number_input("Estoque Inicial", min_value=0, value=1)
            custo = c_v2.number_input("Custo Material (R$)", min_value=0.0, value=3.50, step=0.50)
            preco = c_v3.number_input("Preço Shopee (R$)", min_value=0.0, value=15.00, step=1.00)
            
        with col_form_right:
            st.markdown("<h4 style='color: #DB7F65; font-size: 16px;'>3. Foto do Produto</h4>", unsafe_allow_html=True)
            foto_file = st.file_uploader("Selecione uma imagem (JPG ou PNG)", type=["jpg", "jpeg", "png"])
            foto_img = None
            
            if foto_file is not None:
                foto_img = Image.open(foto_file)
                st.image(foto_img, caption="Pré-visualização da Foto", use_column_width=True)
            else:
                st.markdown("""
                    <div style="border: 2px dashed #EAB890; border-radius: 14px; padding: 30px; text-align: center; background-color: #FFFFFF; color: #7A6664;">
                        <span style="font-size: 32px;">📷</span><br>
                        <span style="font-size: 13px;">Envie uma foto clara da sua arte pronta</span>
                    </div>
                """, unsafe_allow_html=True)
                
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✨ Salvar Produto no ERP Saya Beads")
        
        if submitted:
            if nome.strip() == "":
                st.error("⚠️ Por favor, digite o nome do produto antes de salvar!")
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
                st.success(f"🎉 Produto **'{nome}'** cadastrado com sucesso!")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TELA 3: INSUMOS EXTRAS
# ------------------------------------------
elif menu == "📦 Insumos Extras":
    st.markdown("<h2>📦 Estoque de Insumos Extras</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5C4B49;'>Controle de ferragens, embalagens e mimos enviados aos clientes.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    df_insumos = pd.DataFrame(st.session_state.insumos)
    st.dataframe(df_insumos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Adicionar Novo Material / Insumo"):
        with st.form("form_insumo"):
            c_i1, c_i2 = st.columns(2)
            item_nome = c_i1.text_input("Nome do Material (Ex: Mosquetão Dourado)")
            cat = c_i2.selectbox("Categoria", ["Ferragem", "Ímã", "Embalagem", "Mimos", "Outros"])
            
            c_i3, c_i4 = st.columns(2)
            qtd = c_i3.number_input("Quantidade em Estoque", min_value=1, value=100)
            custo_u = c_i4.number_input("Custo Unitário (R$)", min_value=0.0, value=0.20, step=0.05)
            
            if st.form_submit_button("Salvar Insumo"):
                st.session_state.insumos.append({
                    "Item": item_nome, "Categoria": cat, "Estoque (Unid.)": qtd, "Custo Unid. (R$)": custo_u
                })
                st.success("Material cadastrado com sucesso!")
                st.rerun()

# ------------------------------------------
# TELA 4: CALCULADORA DE PREÇO & MARGEM
# ------------------------------------------
elif menu == "🧮 Calculadora & Ficha":
    st.markdown("<h2>🧮 Calculadora de Preço & Lucro Shopee</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5C4B49;'>Simule o preço de venda ideal considerando custos de fabricação e comissões da plataforma.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.markdown("<h4 style='color: #DB7F65;'>1. Custos da Peça</h4>", unsafe_allow_html=True)
        qtd_beads = st.number_input("Quantidade aproximada de Beads", min_value=1, value=180)
        custo_bead_unitario = 0.015 # Estimativa por bead
        custo_beads_total = qtd_beads * custo_bead_unitario
        
        custo_extras = st.number_input("Insumos Extras (Argola, Saquinho, Mimo) R$", min_value=0.0, value=0.80)
        custo_total_peca = custo_beads_total + custo_extras
        
        st.markdown(f"""
            <div style="background-color: #FFFFFF; border: 1.5px solid #EAB890; padding: 15px; border-radius: 12px; margin-top: 15px;">
                <span style="color: #7A6664; font-size: 13px;">Custo de Fabricação Estimado:</span><br>
                <b style="font-size: 20px; color: #CF605B;">R$ {custo_total_peca:.2f}</b>
            </div>
        """, unsafe_allow_html=True)
        
    with col_calc2:
        st.markdown("<h4 style='color: #DB7F65;'>2. Simulação Shopee</h4>", unsafe_allow_html=True)
        preco_venda_sim = st.number_input("Preço de Venda Desejado (R$)", min_value=0.0, value=20.00)
        
        taxa_shopee_pct = st.slider("Comissão Shopee (%)", min_value=0, max_value=30, value=20) / 100
        taxa_fixa = 4.00 # Taxa padrão da Shopee
        
        taxa_total = (preco_venda_sim * taxa_shopee_pct) + taxa_fixa
        lucro_liquido = preco_venda_sim - custo_total_peca - taxa_total
        margem = (lucro_liquido / preco_venda_sim * 100) if preco_venda_sim > 0 else 0
        
        st.markdown("<hr>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Taxa Total Shopee", f"R$ {taxa_total:.2f}")
        m2.metric("Lucro Líquido", f"R$ {lucro_liquido:.2f}", delta=f"{margem:.1f}% Margem")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TELA 5: IMPORTADOR SHOPEE
# ------------------------------------------
elif menu == "📊 Importar Shopee":
    st.markdown("<h2>📊 Importação de Vendas Shopee</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5C4B49;'>Carregue a planilha de relatórios da Shopee para dar baixa automática no seu estoque.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card" style="text-align: center; padding: 40px;">', unsafe_allow_html=True)
    st.markdown("<span style='font-size: 48px;'>📑</span>", unsafe_allow_html=True)
    st.markdown("<h4>Selecione o arquivo exportado da Shopee</h4>", unsafe_allow_html=True)
    
    file_shopee = st.file_uploader("", type=["csv", "xlsx"])
    if file_shopee is not None:
        st.success("🎉 Arquivo recebido com sucesso! Processando pedidos...")
    st.markdown('</div>', unsafe_allow_html=True)
