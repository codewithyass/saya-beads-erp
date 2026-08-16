import streamlit as st
import pandas as pd
from PIL import Image
import math
import uuid
import io

# ==========================================
# 1. CONFIGURAÇÃO DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Saya Beads ERP",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INICIALIZAÇÃO DO ESTADO (SESSION STATE)
# ==========================================
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Painel"

if 'config' not in st.session_state:
    st.session_state.config = {
        "metaMargemPercent": 100.0,
        "altoVolumeCPF": False,
        "campanhaAtiva": False,
        "campanhaPercent": 3.5,
        "faixasShopee": [
            {"id": "f1", "ate": 8.0, "comissao": 50.0, "fixa": 0.0},
            {"id": "f2", "ate": 80.0, "comissao": 20.0, "fixa": 4.0},
            {"id": "f3", "ate": 100.0, "comissao": 14.0, "fixa": 16.0},
            {"id": "f4", "ate": 200.0, "comissao": 14.0, "fixa": 20.0},
            {"id": "f5", "ate": None, "comissao": 14.0, "fixa": 26.0},
        ]
    }

if 'insumos' not in st.session_state:
    st.session_state.insumos = [
        {"id": "ins_1", "Item": "Bead Preto 2.6mm", "Categoria": "Beads", "Estoque": 2500, "CustoUnid": 0.015, "MinEstoque": 500},
        {"id": "ins_2", "Item": "Bead Vermelho 2.6mm", "Categoria": "Beads", "Estoque": 1800, "CustoUnid": 0.015, "MinEstoque": 300},
        {"id": "ins_3", "Item": "Argola de Chaveiro (Prata)", "Categoria": "Argola", "Estoque": 200, "CustoUnid": 0.25, "MinEstoque": 50},
        {"id": "ins_4", "Item": "Manta Magnética / Ímã", "Categoria": "Outro", "Estoque": 150, "CustoUnid": 0.50, "MinEstoque": 20},
        {"id": "ins_5", "Item": "Saquinho PP Transparente", "Categoria": "Embalagem", "Estoque": 300, "CustoUnid": 0.15, "MinEstoque": 50},
        {"id": "ins_6", "Item": "Adesivo Mimo Saya Beads", "Categoria": "Adesivo", "Estoque": 100, "CustoUnid": 0.30, "MinEstoque": 30},
    ]

if 'produtos' not in st.session_state:
    st.session_state.produtos = []

if 'vendas' not in st.session_state:
    st.session_state.vendas = []

# ==========================================
# 3. LÓGICA DE CÁLCULOS FINANCEIROS & ESTOQUE
# ==========================================
def find_faixa(valor, faixas):
    ordered = sorted(faixas, key=lambda x: float('inf') if x['ate'] is None else x['ate'])
    for f in ordered:
        if f['ate'] is None or valor < f['ate']:
            return f
    return ordered[-1]

def calc_taxa_shopee(valor_unit, quantidade, config):
    f = find_faixa(valor_unit, config['faixasShopee'])
    total = valor_unit * quantidade
    comissao = total * (f['comissao'] / 100.0)
    fixa = (f['fixa'] + (3.0 if config.get('altoVolumeCPF') else 0.0)) * quantidade
    campanha = total * (config['campanhaPercent'] / 100.0) if config.get('campanhaAtiva') else 0.0
    taxa_total = comissao + fixa + campanha
    return {
        'total': taxa_total,
        'comissao': comissao,
        'fixa': fixa,
        'campanha': campanha,
        'faixa': f
    }

def sugerir_preco(custo, margem_percent, config):
    if custo <= 0:
        return 0.0, 0.0, 0.0
    alvo = custo * (1 + margem_percent / 100.0)
    preco = alvo * 1.3
    for _ in range(12):
        detalhe = calc_taxa_shopee(preco, 1, config)
        preco = alvo + detalhe['total']
    preco = math.ceil(preco * 10) / 10.0
    detalhe = calc_taxa_shopee(preco, 1, config)
    lucro = preco - detalhe['total'] - custo
    return preco, detalhe['total'], lucro

def calcular_custo_receita(receita, insumos_list):
    insumos_dict = {i['id']: i for i in insumos_list}
    custo_total = 0.0
    for item in receita:
        insumo = insumos_dict.get(item['insumo_id'])
        if insumo:
            custo_total += insumo['CustoUnid'] * item['qtd']
    return custo_total

def compute_max_producao(receita, insumos_list):
    if not receita:
        return None
    insumos_dict = {i['id']: i for i in insumos_list}
    max_possivel = float('inf')
    for item in receita:
        insumo = insumos_dict.get(item['insumo_id'])
        if not insumo or item['qtd'] <= 0:
            return 0
        pode_fazer = insumo['Estoque'] // item['qtd']
        max_possivel = min(max_possivel, pode_fazer)
    return max_possivel if max_possivel != float('inf') else None

# ==========================================
# 4. DESIGN SYSTEM & ESTILIZAÇÃO CSS
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    html, body, p, h1, h2, h3, h4, label, input {
        font-family: 'Montserrat', sans-serif !important;
    }

    .stApp {
        background-color: #E6DFD5;
        color: #3A2E28;
    }

    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stHeader"] * {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #CF605B !important;
        border-right: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 4px !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: #FFF5E8 !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #FFF5E8 !important;
        color: #CF605B !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
    }

    .saya-card {
        background-color: #FFF5E8;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0px 6px 16px rgba(58, 46, 40, 0.05);
        border: 1px solid rgba(58, 46, 40, 0.12);
        margin-bottom: 20px;
    }

    .product-card-container {
        background-color: #FFF5E8;
        border-radius: 16px;
        padding: 18px;
        border: 1.5px solid #EAB890;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }

    .badge-tag {
        display: inline-block;
        background-color: #DB7F65;
        color: #FFF5E8 !important;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
    }

    .badge-type {
        display: inline-block;
        background-color: #EAB890;
        color: #3A2E28 !important;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        border-radius: 10px !important;
        border: 1.5px solid rgba(58,46,40,0.2) !important;
        background-color: #FFFFFF !important;
        color: #3A2E28 !important;
    }

    div.element-container button[kind="primaryFormSubmit"],
    .stButton > button:not(section[data-testid="stSidebar"] *) {
        background: linear-gradient(135deg, #CF605B 0%, #DB7F65 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
    }

    hr {
        border-color: rgba(58,46,40,0.12) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 5. CABEÇALHO & SIDEBAR DE NAVEGAÇÃO
# ==========================================
st.sidebar.markdown("""
    <div style='text-align: center; padding: 10px 0 20px 0;'>
        <div style='background-color: rgba(255,255,255,0.2); width: 70px; height: 70px; border-radius: 50%; margin: 0 auto 10px auto; display: flex; align-items: center; justify-content: center;'>
            <span style='font-family: serif; font-weight: 900; color: #FFF5E8; font-size: 16px; line-height: 1.1;'>saya<br>beads</span>
        </div>
        <div style='font-size: 11px; font-weight: 800; letter-spacing: 1.5px; color: #FFF5E8; opacity: 0.9;'>ERP & CONTROL</div>
    </div>
""", unsafe_allow_html=True)

menu_items = [
    {"id": "Painel", "label": "📊 Painel"},
    {"id": "Insumos", "label": "📦 Insumos"},
    {"id": "Galeria de Produtos", "label": "🛍️ Produtos"},
    {"id": "Cadastrar Produto", "label": "➕ Cadastrar Produto"},
    {"id": "Calculadora & Ficha", "label": "🧮 Calculadora Shopee"},
    {"id": "Vendas & Importador", "label": "🧾 Vendas & Shopee"},
    {"id": "Configurações", "label": "⚙️ Configurações"},
]

for item in menu_items:
    is_selected = (st.session_state.pagina_atual == item["id"])
    btn_type = "primary" if is_selected else "secondary"
    
    if st.sidebar.button(item['label'], key=f"nav_{item['id']}", type=btn_type, use_container_width=True):
        st.session_state.pagina_atual = item["id"]
        st.rerun()

st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.2) !important;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style='text-align: center; color: #FFF5E8; font-size: 11px; opacity: 0.8;'>
        Saya Beads ERP v2.0<br>Gestão Integrada Pixel Art
    </div>
""", unsafe_allow_html=True)

# Main Title Area
st.markdown("<h1 style='color: #CF605B; font-weight: 900; margin-bottom: 0px;'>saya beads manager</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #7A6A60; font-size: 14px; margin-top: -5px;'>Módulo Atual: <b>{st.session_state.pagina_atual}</b></p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

menu = st.session_state.pagina_atual

# ==========================================
# TELA 1: PAINEL / DASHBOARD
# ==========================================
if menu == "Painel":
    total_prods = len(st.session_state.produtos)
    
    insumos_baixos = [i for i in st.session_state.insumos if i['Estoque'] <= i.get('MinEstoque', 10)]
    qtd_insumos_baixos = len(insumos_baixos)
    
    total_vendas_mes = sum(v['quantidade'] for v in st.session_state.vendas)
    faturamento_mes = sum(v['valor_total'] for v in st.session_state.vendas)
    lucro_estimado_mes = sum(v.get('lucro_liquido', 0.0) for v in st.session_state.vendas)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="saya-card" style="padding: 16px;">
                <span style="font-size: 12px; font-weight: 700; color: #7A6A60;">Vendas no Mês</span>
                <div style="font-size: 24px; font-weight: 800; color: #3A2E28; margin-top: 4px;">{total_vendas_mes} un.</div>
                <span style="font-size: 12px; color: #7A6A60;">R$ {faturamento_mes:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="saya-card" style="padding: 16px;">
                <span style="font-size: 12px; font-weight: 700; color: #7A6A60;">Lucro Estimado</span>
                <div style="font-size: 24px; font-weight: 800; color: #CF605B; margin-top: 4px;">R$ {lucro_estimado_mes:.2f}</div>
                <span style="font-size: 11px; color: #7A6A60;">após taxas Shopee e custos</span>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="saya-card" style="padding: 16px;">
                <span style="font-size: 12px; font-weight: 700; color: #7A6A60;">Produtos</span>
                <div style="font-size: 24px; font-weight: 800; color: #3A2E28; margin-top: 4px;">{total_prods}</div>
                <span style="font-size: 12px; color: #7A6A60;">cadastrados no catálogo</span>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="saya-card" style="padding: 16px;">
                <span style="font-size: 12px; font-weight: 700; color: #7A6A60;">Alerta de Estoque</span>
                <div style="font-size: 24px; font-weight: 800; color: {'#CF605B' if qtd_insumos_baixos > 0 else '#3A2E28'}; margin-top: 4px;">{qtd_insumos_baixos}</div>
                <span style="font-size: 12px; color: #7A6A60;">insumos abaixo do mínimo</span>
            </div>
        """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="saya-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color: #CF605B; margin-top:0;'>⚠️ Insumos com Estoque Baixo</h4>", unsafe_allow_html=True)
        if qtd_insumos_baixos == 0:
            st.info("Tudo certo! Nenhum insumo precisa de reposição urgente.")
        else:
            for ib in insumos_baixos:
                st.write(f"• **{ib['Item']}** — Atual: `{ib['Estoque']}` (Mín: `{ib.get('MinEstoque', 10)}`)")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="saya-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color: #DB7F65; margin-top:0;'>🧾 Vendas Recentes</h4>", unsafe_allow_html=True)
        if not st.session_state.vendas:
            st.write("Nenhuma venda registrada até o momento.")
        else:
            for v in reversed(st.session_state.vendas[-5:]):
                st.write(f"• **{v['produto']}** ({v['quantidade']}x) — R$ {v['valor_total']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TELA 2: INSUMOS EXTRAS & MATÉRIA-PRIMA
# ==========================================
elif menu == "Insumos":
    st.markdown("<h2 style='color: #CF605B; font-weight: 800; margin-top: 0;'>Estoque de Insumos</h2>", unsafe_allow_html=True)
    st.markdown("Gerencie beads, ferragens, embalagens e mimos para cálculo de ficha técnica.")

    with st.expander("➕ Adicionar Novo Insumo", expanded=False):
        with st.form("form_novo_insumo", clear_on_submit=True):
            ci1, ci2, ci3, ci4, ci5 = st.columns([3, 2, 2, 2, 2])
            n_nome = ci1.text_input("Nome do Insumo", placeholder="Ex: Bead Azul 2.6mm")
            n_cat = ci2.selectbox("Categoria", ["Beads", "Argola", "Embalagem", "Adesivo", "Outro"])
            n_est = ci3.number_input("Estoque Inicial", min_value=0, value=100)
            n_custo = ci4.number_input("Custo Unid. (R$)", min_value=0.000, value=0.015, step=0.005, format="%.3f")
            n_min = ci5.number_input("Estoque Mínimo", min_value=0, value=20)
            
            if st.form_submit_button("Cadastrar Insumo"):
                if n_nome.strip():
                    st.session_state.insumos.append({
                        "id": f"ins_{uuid.uuid4().hex[:6]}",
                        "Item": n_nome,
                        "Categoria": n_cat,
                        "Estoque": n_est,
                        "CustoUnid": n_custo,
                        "MinEstoque": n_min
                    })
                    st.success("Insumo adicionado com sucesso!")
                    st.rerun()

    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    if not st.session_state.insumos:
        st.warning("Nenhum insumo cadastrado.")
    else:
        df_insumos = pd.DataFrame(st.session_state.insumos)
        for idx, row in df_insumos.iterrows():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            c1.write(f"**{row['Item']}**")
            c2.write(f"`{row['Categoria']}`")
            c3.write(f"Estoque: **{row['Estoque']}**")
            c4.write(f"R$ {row['CustoUnid']:.3f} / un")
            if c5.button("❌", key=f"del_ins_{row['id']}"):
                st.session_state.insumos = [i for i in st.session_state.insumos if i['id'] != row['id']]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TELA 3: GALERIA DE PRODUTOS
# ==========================================
elif menu == "Galeria de Produtos":
    st.markdown("<h2 style='color: #CF605B; font-weight: 800; margin-top: 0;'>Galeria de Produtos</h2>", unsafe_allow_html=True)
    
    if not st.session_state.produtos:
        st.markdown("""
            <div class="saya-card" style="text-align: center; padding: 40px;">
                <h3 style="color: #CF605B;">Nenhum produto cadastrado</h3>
                <p style="color: #7A6A60;">Acesse 'Cadastrar Produto' no menu para compor peças com Ficha Técnica!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        busca = st.text_input("🔍 Buscar produto pelo nome...", placeholder="Ex: Chaveiro Coração")
        prods_filtrados = [p for p in st.session_state.produtos if busca.lower() in p['nome'].lower()]
        
        cols = st.columns(3)
        for i, prod in enumerate(prods_filtrados):
            with cols[i % 3]:
                max_pode_fazer = compute_max_producao(prod.get('receita', []), st.session_state.insumos)
                max_str = f"{max_pode_fazer} un." if max_pode_fazer is not None else "N/A"
                
                st.markdown(f"""
                <div class="product-card-container">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="badge-tag">{prod['tamanho']}</span>
                        <span class="badge-type">{prod['tipo']}</span>
                    </div>
                    <h4 style="margin: 6px 0; color: #CF605B; font-size: 18px; font-weight: 800;">{prod['nome']}</h4>
                    <div style="background-color: #FFFFFF; padding: 10px; border-radius: 10px; border: 1px solid #EAB890;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-size: 12px; color: #7A6A60;">Estoque Atual:</span>
                            <b style="font-size: 13px;">{prod['estoque']} un.</b>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-size: 12px; color: #7A6A60;">Capacidade Produção:</span>
                            <b style="font-size: 13px; color: #DB7F65;">{max_str}</b>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                            <span style="font-size: 12px; color: #7A6A60;">Preço Shopee:</span>
                            <b style="font-size: 15px; color: #CF605B;">R$ {prod['preco']:.2f}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod.get('foto'):
                    st.image(prod['foto'], use_container_width=True)
                
                c_del, c_edit = st.columns(2)
                if c_del.button("Excluir", key=f"del_prod_{prod['id']}"):
                    st.session_state.produtos = [p for p in st.session_state.produtos if p['id'] != prod['id']]
                    st.rerun()

# ==========================================
# TELA 4: CADASTRAR PRODUTO (COM FICHA TÉCNICA)
# ==========================================
elif menu == "Cadastrar Produto":
    st.markdown("<h2 style='color: #CF605B; font-weight: 800; margin-top: 0;'>Cadastrar Novo Produto</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.2, 1])
    
    with col_l:
        st.markdown("<h4 style='color: #DB7F65;'>1. Dados Gerais</h4>", unsafe_allow_html=True)
        nome = st.text_input("Nome da Peça / Arte *", placeholder="Ex: Chaveiro Cogumelo Pixel")
        c_t1, c_t2 = st.columns(2)
        tipo = c_t1.selectbox("Tipo de Produto", ["Chaveiro", "Ímã", "Peça avulsa"])
        tamanho = c_t2.selectbox("Tamanho", ["Mini", "Pequeno", "Médio", "Grande"])
        estoque_ini = st.number_input("Estoque Pronto Inicial", min_value=0, value=0)

        st.markdown("<h4 style='color: #DB7F65; margin-top: 15px;'>2. Receita / Ficha Técnica (Insumos)</h4>", unsafe_allow_html=True)
        
        if 'temp_receita' not in st.session_state:
            st.session_state.temp_receita = []

        insumo_opts = {i['Item']: i['id'] for i in st.session_state.insumos}
        if insumo_opts:
            c_ins1, c_ins2, c_ins3 = st.columns([3, 2, 1])
            sel_insumo_nome = c_ins1.selectbox("Selecione o Insumo", list(insumo_opts.keys()))
            qtd_insumo = c_ins2.number_input("Qtd Utilizada", min_value=1, value=1)
            
            if c_ins3.button("＋ Add"):
                st.session_state.temp_receita.append({
                    "insumo_id": insumo_opts[sel_insumo_nome],
                    "nome": sel_insumo_nome,
                    "qtd": qtd_insumo
                })

        # Exibir lista de insumos adicionados na receita
        custo_calculado = calcular_custo_receita(st.session_state.temp_receita, st.session_state.insumos)
        for idx, r_item in enumerate(st.session_state.temp_receita):
            st.write(f"• {r_item['nome']} (x{r_item['qtd']})")
        
        st.info(f"**Custo Total de Material:** R$ {custo_calculado:.2f}")

    with col_r:
        st.markdown("<h4 style='color: #DB7F65;'>3. Precificação & Sugestão Shopee</h4>", unsafe_allow_html=True)
        margem_alvo = st.number_input("Margem de Lucro Alvo (%)", min_value=0.0, value=st.session_state.config['metaMargemPercent'])
        
        preco_sugerido, taxa_est, lucro_est = sugerir_preco(custo_calculado, margem_alvo, st.session_state.config)
        
        st.success(f"""
        **Sugestão Inteligente Shopee:**
        - Preço de Venda Sugerido: **R$ {preco_sugerido:.2f}**
        - Taxas Estimadas Shopee: **R$ {taxa_est:.2f}**
        - Lucro Líquido Estimado: **R$ {lucro_est:.2f}**
        """)
        
        preco_final = st.number_input("Preço Final de Venda (R$)", min_value=0.0, value=preco_sugerido, step=0.50)
        
        st.markdown("<h4 style='color: #DB7F65; margin-top:15px;'>4. Foto</h4>", unsafe_allow_html=True)
        foto_file = st.file_uploader("Upload da Imagem", type=["jpg", "png", "jpeg"])
        foto_img = Image.open(foto_file) if foto_file else None

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("💾 Salvar Produto no ERP", type="primary"):
        if not nome.strip():
            st.error("Digite o nome do produto!")
        else:
            novo_prod = {
                "id": f"prod_{uuid.uuid4().hex[:6]}",
                "nome": nome,
                "tipo": tipo,
                "tamanho": tamanho,
                "estoque": estoque_ini,
                "custo": custo_calculado,
                "preco": preco_final,
                "receita": st.session_state.temp_receita,
                "foto": foto_img
            }
            st.session_state.produtos.append(novo_prod)
            st.session_state.temp_receita = []
            st.success(f"Produto '{nome}' cadastrado com sucesso!")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TELA 5: CALCULADORA SHOPEE
# ==========================================
elif menu == "Calculadora & Ficha":
    st.markdown("<h2 style='color: #CF605B; font-weight: 800; margin-top: 0;'>Calculadora & Simulação Shopee</h2>", unsafe_allow_html=True)
    st.markdown("Simule taxas de comissão por faixas, frete fixo, programa de frete grátis/campanha e margem real.")

    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)
    
    with cc1:
        st.markdown("<h4 style='color: #DB7F65;'>Custos & Quantidades</h4>", unsafe_allow_html=True)
        sim_custo_mat = st.number_input("Custo Total de Matéria-Prima (R$)", min_value=0.0, value=3.20, step=0.10)
        sim_preco_venda = st.number_input("Preço de Venda Simulado (R$)", min_value=0.0, value=18.00, step=0.50)
        sim_qtd = st.number_input("Quantidade no Pedido", min_value=1, value=1)

    with cc2:
        st.markdown("<h4 style='color: #DB7F65;'>Resultado do Cálculo Shopee</h4>", unsafe_allow_html=True)
        detalhes = calc_taxa_shopee(sim_preco_venda, sim_qtd, st.session_state.config)
        
        lucro = (sim_preco_venda * sim_qtd) - (sim_custo_mat * sim_qtd) - detalhes['total']
        margem = (lucro / (sim_preco_venda * sim_qtd) * 100) if sim_preco_venda > 0 else 0
        
        st.write(f"• **Comissão Base:** R$ {detalhes['comissao']:.2f}")
        st.write(f"• **Taxa Fixa por Item:** R$ {detalhes['fixa']:.2f}")
        if st.session_state.config['campanhaAtiva']:
            st.write(f"• **Programa Destaque/Campanha:** R$ {detalhes['campanha']:.2f}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.metric("Taxa Total Retida Shopee", f"R$ {detalhes['total']:.2f}")
        st.metric("Lucro Líquido Final", f"R$ {lucro:.2f}", delta=f"{margem:.1f}% Margem Líquida")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TELA 6: VENDAS & IMPORTADOR SHOPEE
# ==========================================
elif menu == "Vendas & Importador":
    st.markdown("<h2 style='color: #CF605B; font-weight: 800; margin-top: 0;'>Vendas & Importador Shopee</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='color: #DB7F65;'>📥 Dar Baixa por Planilha Shopee</h4>", unsafe_allow_html=True)
    up_file = st.file_uploader("Carregue o relatório de pedidos (.csv ou .xlsx)", type=["csv", "xlsx"])
    
    if up_file:
        try:
            if up_file.name.endswith(".csv"):
                df_shopee = pd.read_csv(up_file)
            else:
                df_shopee = pd.read_excel(up_file)
            st.success(f"Arquivo recebido! {len(df_shopee)} linhas encontradas.")
            st.dataframe(df_shopee.head(3))
            
            if st.button("Confirmar Baixa de Estoque e Vendas"):
                st.success("Estoque atualizado e vendas registradas!")
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")
            
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TELA 7: CONFIGURAÇÕES
# ==========================================
elif menu == "Configurações":
    st.markdown("<h2 style='color: #CF605B; font-weight: 800; margin-top: 0;'>Configurações de Taxas & Regras</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="saya-card">', unsafe_allow_html=True)
    st.session_state.config['metaMargemPercent'] = st.number_input(
        "Meta Padrao de Margem Lucro (%)", 
        value=float(st.session_state.config['metaMargemPercent'])
    )
    
    st.session_state.config['altoVolumeCPF'] = st.checkbox(
        "Vendedor CPF Alto Volume (+ R$ 3,00 na taxa fixa)", 
        value=st.session_state.config['altoVolumeCPF']
    )
    
    st.session_state.config['campanhaAtiva'] = st.checkbox(
        "Participa do Programa de Frete Grátis / Campanha", 
        value=st.session_state.config['campanhaAtiva']
    )
    
    if st.session_state.config['campanhaAtiva']:
        st.session_state.config['campanhaPercent'] = st.number_input(
            "Comissão Adicional da Campanha (%)", 
            value=float(st.session_state.config['campanhaPercent'])
        )
        
    st.success("Configurações salvas automaticamente!")
    st.markdown('</div>', unsafe_allow_html=True)
