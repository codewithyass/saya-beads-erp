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
# 2. DESIGN SYSTEM & CSS (CLAUDE MENU STYLE)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');

    /* TIPOGRAFIA GLOBAL */
    html, body, div, span, p, h1, h2, h3, h4, label, input, button {
        font-family: 'Montserrat', sans-serif !important;
    }

    .stApp {
        background-color: #E6DFD5;
        color: #3E3232;
    }

    /* BARRA LATERAL CORAL */
    section[data-testid="stSidebar"] {
        background-color: #CF605B !important;
        border-right: none !important;
    }

    /* ------------------------------------------
       OCULTAR CÍRCULO / CHECKBOX DO RADIO
    ------------------------------------------ */
    div[data-testid="stRadio"] label > div:first-child,
    div[data-testid="stRadio"] label input {
        display: none !important;
    }

    /* ESTILIZAÇÃO DAS OPÇÕES DO MENU (ESTILO CLAUDE) */
    div[data-testid="stRadio"] > div {
        gap: 6px !important;
    }

    div[data-testid="stRadio"] label {
        background-color: transparent !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
    }

    /* HOVER NOS ITENS NÃO SELECIONADOS */
    div[data-testid="stRadio"] label:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
    }

    /* TEXTO DOS ITENS NÃO SELECIONADOS */
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        color: #FFF5E8 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* ITEM SELECIONADO (DESTAQUE CREME) */
    div[data-testid="stRadio"] label[data-checked="true"] {
        background-color: #FFF5E8 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label[data-checked="true"] span {
        color: #CF605B !important;
        font-weight: 800 !important;
    }

    /* ÍCONES VETORIAIS NO MENU LATERAL */
    div[data-testid="stRadio"] label::before {
        font-family: 'Material Symbols Outlined' !important;
        font-size: 22px !important;
        margin-right: 12px !important;
        display: inline-block !important;
        vertical-align: middle !important;
        color: #FFF5E8 !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"]::before {
        color: #CF605B !important;
    }

    /* MAPEAMENTO DOS ÍCONES VETORIAIS DO MENU */
    div[data-testid="stRadio"] > div > label:nth-child(1)::before { content: 'grid_view'; }
    div[data-testid="stRadio"] > div > label:nth-child(2)::before { content: 'add_circle'; }
    div[data-testid="stRadio"] > div > label:nth-child(3)::before { content: 'inventory_2'; }
    div[data-testid="stRadio"] > div > label:nth-child(4)::before { content: 'calculate'; }
    div[data-testid="stRadio"] > div > label:nth-child(5)::before { content: 'cloud_upload'; }

    /* CARDS DA TELA PRINCIPAL */
    .saya-card {
        background-color: #FFF5E8;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 8px 20px rgba(207, 96, 91, 0.08);
        border: 1px solid #EAB890;
        margin-bottom: 25px;
    }

    .product-card-container {
        background-color: #FFF5E8;
        border-radius: 18px;
        padding: 18px;
        border: 2px solid #EAB890;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }

    .badge-tag {
        display: inline-block;
        background-color: #E49872;
        color: #FFFFFF !important;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
    }

    .badge-type {
        display: inline-block;
        background-color: #EAB890;
        color: #3E3232 !important;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        border-radius: 12px !important;
        border: 1.5px solid #EAB890 !important;
        background-color: #FFFFFF !important;
        color: #3E3232 !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #CF605B 0%, #DB7F65 100%) !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100%;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #CF605B !important;
    }

    hr {
        border-color: #EAB890 !important;
        opacity: 0.5;
    }
    </style>
""", unsafe_allow_html=True)

# Helper para renderizar títulos de página com ícone vetorial
def page_title(icon, text):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span class="material-symbols-outlined" style="font-size: 32px; color: #CF605B; font-weight: bold;">{icon}</span>
            <h2 style="margin: 0 !important; color: #CF605B !important; font-size: 26px; font-weight: 800;">{text}</h2>
        </div>
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
# 4. CABEÇALHO DA TELA
# ==========================================
with st.container():
    col_logo, col_header = st.columns([1, 4])
    
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=130)
        else:
            st.markdown("""
                <div style="background-color: #FFF5E8; border: 2px solid #EAB890; border-radius: 18px; padding: 15px; text-align: center;">
                    <div style="font-weight: 800; color: #CF605B; font-size: 13px;">SAYA BEADS</div>
                </div>
            """, unsafe_allow_html=True)
            
    with col_header:
        st.markdown("<h1 style='margin-bottom: 0px; color: #CF605B; font-weight: 800;'>saya beads manager</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #7A6664; font-size: 15px; margin-top: -5px;'>Painel de Gestão, Produção & Estoque de Hama Beads</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 5. NAVEGAÇÃO LATERAL
# ==========================================
st.sidebar.markdown("""
    <div style='font-size: 13px; font-weight: 800; letter-spacing: 1px; color: #FFF5E8; margin-bottom: 14px; opacity: 0.9;'>
        NAVEGAÇÃO
    </div>
""", unsafe_allow_html=True)

menu_options = [
    "Galeria de Produtos",
    "Cadastrar Produto",
    "Insumos Extras",
    "Calculadora & Ficha",
    "Importar Shopee"
]

menu = st.sidebar.radio("", menu_options, label_visibility="collapsed")

st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.2) !important;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style='text-align: center; color: #FFF5E8; font-size: 12px; opacity: 0.8;'>
        <b>Saya Beads ERP</b><br>Pixel Art & Gestão
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------
# TELA 1: GALERIA DE PRODUTOS
# ------------------------------------------
if menu == "Galeria de Produtos":
    page_title("grid_view", "Galeria de Produtos Prontos")
    st.markdown("Visão geral do seu estoque atual catalogado.")
    
    if not st.session_state.produtos:
        st.markdown("""
            <div class="saya-card" style="text-align: center; padding: 40px;">
                <h3 style="margin-top: 15px; color: #CF605B;">Nenhum produto cadastrado ainda</h3>
                <p style="color: #7A6664;">Acesse <b>'Cadastrar Produto'</b> no menu lateral para adicionar suas peças!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        col_f1, _ = st.columns([2, 1])
        with col_f1:
            busca = st.text_input("Buscar produto pelo nome...", placeholder="Ex: Coração, Pacman, Gato")
        
        prods_filtrados = [(idx, p) for idx, p in enumerate(st.session_state.produtos) if busca.lower() in p['nome'].lower()]
        
        cols = st.columns(3)
        for i, (real_idx, prod) in enumerate(prods_filtrados):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="product-card-container">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="badge-tag">{prod['tamanho']}</span>
                        <span class="badge-type">{prod['tipo']}</span>
                    </div>
                    <h4 style="margin: 8px 0px 12px 0px; color: #CF605B; font-size: 20px; font-weight: 800;">{prod['nome']}</h4>
                    <div style="background-color: #FFFFFF; padding: 10px 14px; border-radius: 12px; border: 1.5px solid #EAB890;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px; color: #7A6664;">Estoque:</span>
                            <b style="color: #3E3232; font-size: 14px;">{prod['estoque']} unid.</b>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                            <span style="font-size: 13px; color: #7A6664;">Preço Shopee:</span>
                            <b style="color: #CF605B; font-size: 16px;">R$ {prod['preco']:.2f}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['foto'] is not None:
                    st.image(prod['foto'], use_container_width=True)
                else:
                    st.markdown("""
                        <div style="background-color: #FFF5E8; border: 1.5px solid #EAB890; height: 180px; border-radius: 14px; display: flex; align-items: center; justify-content: center; color: #7A6664; font-size: 13px; margin-bottom: 10px;">
                            Sem foto cadastrada
                        </div>
                    """, unsafe_allow_html=True)
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    with st.popover("Editar"):
                        st.markdown(f"**Editar: {prod['nome']}**")
                        novo_nome = st.text_input("Nome", value=prod['nome'], key=f"edit_nome_{real_idx}")
                        novo_tipo = st.selectbox("Tipo", ["Chaveiro", "Ímã", "Peça Individual (Sem montagem)"], 
                                                 index=["Chaveiro", "Ímã", "Peça Individual (Sem montagem)"].index(prod['tipo']), key=f"edit_tipo_{real_idx}")
                        novo_tam = st.selectbox("Tamanho", ["Mini", "Pequeno", "Médio", "Grande"], 
                                                index=["Mini", "Pequeno", "Médio", "Grande"].index(prod['tamanho']), key=f"edit_tam_{real_idx}")
                        novo_est = st.number_input("Estoque", min_value=0, value=prod['estoque'], key=f"edit_est_{real_idx}")
                        novo_custo = st.number_input("Custo (R$)", min_value=0.0, value=prod['custo'], key=f"edit_custo_{real_idx}")
                        novo_preco = st.number_input("Preço (R$)", min_value=0.0, value=prod['preco'], key=f"edit_preco_{real_idx}")
                        nova_foto_file = st.file_uploader("Trocar Foto", type=["jpg", "jpeg", "png"], key=f"edit_foto_{real_idx}")
                        
                        if st.button("Salvar Alterações", key=f"save_btn_{real_idx}"):
                            st.session_state.produtos[real_idx]['nome'] = novo_nome
                            st.session_state.produtos[real_idx]['tipo'] = novo_tipo
                            st.session_state.produtos[real_idx]['tamanho'] = novo_tam
                            st.session_state.produtos[real_idx]['estoque'] = novo_est
                            st.session_state.produtos[real_idx]['custo'] = novo_custo
                            st.session_state.produtos[real_idx]['preco'] = novo_preco
                            if nova_foto_file is not None:
                                st.session_state.produtos[real_idx]['foto'] = Image.open(nova_foto_file)
                            st.success("Salvo!")
                            st.rerun()

                with c_act2:
                    if st.button("Excluir", key=f"del_btn_{real_idx}"):
                        st.session_state.produtos.pop(real_idx)
                        st.rerun()

                st.write("")

# ------------------------------------------
# TELA 2: CADASTRO DE PRODUTO
# ------------------------------------------
elif menu == "Cadastrar Produto":
    page_title("add_circle", "Cadastrar Novo Produto")
    st.markdown("Adicione novos itens ao catálogo de artes da Saya Beads.")
    
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
                st.image(foto_img, caption="Pré-visualização da Foto", use_container_width=True)
            else:
                st.markdown("""
                    <div style="border: 2px dashed #EAB890; border-radius: 14px; padding: 30px; text-align: center; background-color: #FFFFFF; color: #7A6664;">
                        <span style="font-size: 13px;">Envie uma foto clara da sua arte pronta</span>
                    </div>
                """, unsafe_allow_html=True)
                
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Salvar Produto no ERP Saya Beads")
        
        if submitted:
            if nome.strip() == "":
                st.error("Por favor, digite o nome do produto antes de salvar!")
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
                st.success(f"Produto **'{nome}'** cadastrado com sucesso!")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TELA 3: INSUMOS EXTRAS
# ------------------------------------------
elif menu == "Insumos Extras":
    page_title("inventory_2", "Estoque de Insumos Extras")
    st.markdown("Controle de ferragens, embalagens e mimos enviados aos clientes.")
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    
    for idx_ins, ins in enumerate(st.session_state.insumos):
        c_i1, c_i2, c_i3, c_i4, c_i5 = st.columns([2.5, 1.5, 1.5, 1.5, 1])
        c_i1.write(f"**{ins['Item']}**")
        c_i2.write(f"{ins['Categoria']}")
        c_i3.write(f"{ins['Estoque (Unid.)']} unid.")
        c_i4.write(f"R$ {ins['Custo Unid. (R$)']:.2f}")
        if c_i5.button("Remover", key=f"del_ins_{idx_ins}"):
            st.session_state.insumos.pop(idx_ins)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TELA 4: CALCULADORA
# ------------------------------------------
elif menu == "Calculadora & Ficha":
    page_title("calculate", "Calculadora de Preço & Lucro Shopee")
    st.markdown("Simule o preço de venda ideal considerando custos de fabricação e comissões.")
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.markdown("<h4 style='color: #DB7F65;'>1. Custos da Peça</h4>", unsafe_allow_html=True)
        qtd_beads = st.number_input("Quantidade aproximada de Beads", min_value=1, value=180)
        custo_beads_total = qtd_beads * 0.015
        
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
        taxa_fixa = 4.00
        
        taxa_total = (preco_venda_sim * taxa_shopee_pct) + taxa_fixa
        lucro_liquido = preco_venda_sim - custo_total_peca - taxa_total
        margem = (lucro_liquido / preco_venda_sim * 100) if preco_venda_sim > 0 else 0
        
        st.markdown("<hr>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Taxa Total Shopee", f"R$ {taxa_total:.2f}")
        m2.metric("Lucro Líquido", f"R$ {lucro_liquido:.2f}", delta=f"{margem:.1f}% Margem")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TELA 5: IMPORTADOR
# ------------------------------------------
elif menu == "Importar Shopee":
    page_title("cloud_upload", "Importação de Vendas Shopee")
    st.markdown("Carregue a planilha de relatórios da Shopee para dar baixa automática no estoque.")
    
    st.markdown('<div class="saya-card" style="text-align: center; padding: 40px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='color: #CF605B;'>Selecione o arquivo exportado da Shopee</h4>", unsafe_allow_html=True)
    
    file_shopee = st.file_uploader("", type=["csv", "xlsx"])
    if file_shopee is not None:
        st.success("Arquivo recebido com sucesso! Processando pedidos...")
    st.markdown('</div>', unsafe_allow_html=True)
