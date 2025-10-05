import pandas as pd
import geopandas as gpd
import requests
import os
import numpy as np
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import from_origin
from rasterstats import zonal_stats
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from shapely.geometry import box

# --- Carrega as variáveis de ambiente do ficheiro .env ---
load_dotenv()

# --- 1. CONFIGURAÇÃO GERAL ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)  # Cria /data/ se não existir

PATH_MALHA_2022_SHP = os.path.join(DATA_DIR, 'PE_setores_CD2022.shp')
PATH_POPULACAO_2022_CSV = os.path.join(DATA_DIR, 'Agregados_preliminares_por_setores_censitarios_PE.csv')
PATH_RENDA_2010_CSV = os.path.join(DATA_DIR, 'PessoaRenda_PE.csv')
CODIGO_MUNICIPIO_RECIFE = '2611606'
OUTPUT_GEOJSON_FILE = os.path.join(DATA_DIR, 'recife_vulnerabilidade.geojson')

FATOR_CORRECAO_RENDA = 2.03

# <-- Mapeamento de arquivos S3 -->
S3_BASE_URL = 'https://nasah5geojson.s3.us-east-1.amazonaws.com'
FILE_URLS = {
    'PE_setores_CD2022.shp': f'{S3_BASE_URL}/PE_setores_CD2022.shp',
    'PE_setores_CD2022.dbf': f'{S3_BASE_URL}/PE_setores_CD2022.dbf',
    'PE_setores_CD2022.shx': f'{S3_BASE_URL}/PE_setores_CD2022.shx',  # Assumindo que existe
    'PE_setores_CD2022.prj': f'{S3_BASE_URL}/PE_setores_CD2022.prj',
    'PE_setores_CD2022.cpg': f'{S3_BASE_URL}/PE_setores_CD2022.cpg',
    'Agregados_preliminares_por_setores_censitarios_PE.csv': f'{S3_BASE_URL}/Agregados_preliminares_por_setores_censitarios_PE.csv',
    'PessoaRenda_PE.csv': f'{S3_BASE_URL}/PessoaRenda_PE.csv',
    'ECOSTRESS_LST_Recife.tif': f'{S3_BASE_URL}/ECOSTRESS_LST_Recife.tif'
}

def download_if_missing(local_path, url):
    """Baixa arquivo do S3 se não existir localmente."""
    if os.path.exists(local_path):
        print(f"✅ Arquivo já existe: {local_path}")
        return True
    
    print(f"📥 Baixando {os.path.basename(local_path)} de {url}...")
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(resp.content)
            print(f"✅ Baixado com sucesso: {local_path}")
            return True
        else:
            print(f"❌ Falha no download (status {resp.status_code}): {url}")
            return False
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False

# --- 2. FUNÇÕES DE ANÁLISE DE DADOS (O "Cérebro") ---

def _normalize(series):
    """Função auxiliar para normalizar dados para a escala 0-1."""
    min_val, max_val = series.min(), series.max()
    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        return pd.Series(0.5, index=series.index)
    return (series - min_val) / (max_val - min_val)

def run_full_analysis():
    """Executa a análise completa e salva um ficheiro GeoJSON com os resultados."""
    print("--- INICIANDO ANÁLISE COMPLETA DOS DADOS ---")
    
    # Baixa arquivos do S3 se necessário
    print("--- Baixando arquivos do S3 ---")
    shp_components = ['shp', 'dbf', 'shx', 'prj', 'cpg']
    base_shp = 'PE_setores_CD2022'
    all_success = True
    
    # Baixa componentes do SHP
    for ext in shp_components:
        local = os.path.join(DATA_DIR, f'{base_shp}.{ext}')
        url_key = f'{base_shp}.{ext}' if ext != 'shp' else f'{base_shp}.shp'
        if not download_if_missing(local, FILE_URLS[url_key]):
            all_success = False
    
    # Baixa CSVs
    for csv in [PATH_POPULACAO_2022_CSV, PATH_RENDA_2010_CSV]:
        basename = os.path.basename(csv)
        if not download_if_missing(csv, FILE_URLS[basename]):
            all_success = False
    
    # Baixa TIFF (pra temperatura)
    geotiff_path = os.path.join(DATA_DIR, 'ECOSTRESS_LST_Recife.tif')
    if not download_if_missing(geotiff_path, FILE_URLS['ECOSTRESS_LST_Recife.tif']):
        all_success = False
    
    if not all_success:
        print("❌ Falha no download de um ou mais arquivos. Abortando análise.")
        return False
    
    # Verifica se todos existem agora
    required_files = [
        PATH_MALHA_2022_SHP,
        PATH_POPULACAO_2022_CSV,
        PATH_RENDA_2010_CSV,
        geotiff_path
    ]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Arquivo ainda não encontrado após download: {file_path}")
            return False
    
    # --- 1. Processamento IBGE ---
    print("--- 1. Processando e Unindo Dados do IBGE ---")
    try:
        gdf_malha = gpd.read_file(PATH_MALHA_2022_SHP, dtype={'CD_SETOR': str})
        df_pop_2022 = pd.read_csv(PATH_POPULACAO_2022_CSV, sep=';', encoding='latin-1', decimal=',', dtype={'CD_SETOR': str})
        df_renda_2010 = pd.read_csv(PATH_RENDA_2010_CSV, sep=';', encoding='latin-1', decimal=',', dtype={'Cod_setor': str})
    except FileNotFoundError as e:
        print(f"❌ ERRO: Ficheiro do IBGE não encontrado! {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO ao ler arquivos IBGE: {e}")
        return False

    gdf_malha.rename(columns={'CD_SETOR': 'CD_CENSITARIO'}, inplace=True)
    df_pop_2022.rename(columns={'CD_SETOR': 'CD_CENSITARIO'}, inplace=True)
    df_renda_2010.rename(columns={'Cod_setor': 'CD_CENSITARIO'}, inplace=True)

    for df in [gdf_malha, df_pop_2022, df_renda_2010]:
        df['CD_CENSITARIO'] = df['CD_CENSITARIO'].str.extract(r'(\d{15})').fillna('')
        df.dropna(subset=['CD_CENSITARIO'], inplace=True)
        df = df[df['CD_CENSITARIO'] != ''].copy()

    df_pop_sel = df_pop_2022[['CD_CENSITARIO', 'v0001', 'AREA_KM2']].rename(columns={'v0001': 'populacao_total', 'AREA_KM2': 'area_km2'})
    df_renda_sel = df_renda_2010[['CD_CENSITARIO', 'V003']].rename(columns={'V003': 'renda_media_2010'})
    
    gdf_final = gdf_malha.merge(df_pop_sel, on='CD_CENSITARIO', how='left')
    gdf_final = gdf_final.merge(df_renda_sel, on='CD_CENSITARIO', how='left')
    
    gdf_recife = gdf_final[gdf_final['CD_MUN'] == CODIGO_MUNICIPIO_RECIFE].copy()
    
    if gdf_recife.empty:
        print("❌ Nenhum dado para Recife encontrado após o filtro.")
        return False

    for col in ['populacao_total', 'area_km2', 'renda_media_2010']:
        gdf_recife[col] = pd.to_numeric(gdf_recife[col], errors='coerce')
        gdf_recife[col] = gdf_recife[col].fillna(gdf_recife[col].median())

    gdf_recife['renda_corrigida'] = gdf_recife['renda_media_2010'] * FATOR_CORRECAO_RENDA
    gdf_recife = gdf_recife[gdf_recife['area_km2'] > 0].copy()
    gdf_recife['densidade_pop'] = gdf_recife['populacao_total'] / gdf_recife['area_km2']
    
    if 'NM_BAIRRO' not in gdf_recife.columns: gdf_recife['NM_BAIRRO'] = 'Recife'
    print(f"✅ Dados do IBGE para {len(gdf_recife)} setores de Recife processados.")

    # --- 2. Processamento Temperatura com Dados da NASA (ECOSTRESS) ---
    print("\n--- 2. Processando Temperaturas do GeoTIFF do ECOSTRESS ---")
    
    GEOTIFF_NASA_PATH = os.path.join(DATA_DIR, 'ECOSTRESS_LST_Recife.tif')
    
    if not os.path.exists(GEOTIFF_NASA_PATH):
        print(f"❌ GeoTIFF não encontrado: {GEOTIFF_NASA_PATH}")
        print("🔄 Usando 29°C como fallback para todas as temperaturas.")
        gdf_recife['temperatura_media_estimada'] = 29.0
    else:
        try:
            with rasterio.open(GEOTIFF_NASA_PATH) as raster:
                gdf_recife_proj = gdf_recife.to_crs(raster.crs)
                
                stats = zonal_stats(
                    gdf_recife_proj, 
                    raster.read(1),
                    affine=raster.transform, 
                    stats="mean",
                    nodata=np.nan,
                    all_touched=True
                )
                
                gdf_recife['temperatura_media_estimada'] = [s['mean'] for s in stats]
                
                falhas = gdf_recife['temperatura_media_estimada'].isnull().sum()
                print(f"Setores com temp None/NaN após zonal_stats: {falhas} de {len(gdf_recife)} ({falhas/len(gdf_recife):.1%})")

                if 0 < falhas < len(gdf_recife):
                    print("⚠️ Falhas parciais detetadas. A iniciar interpolação espacial para preencher as lacunas.")

                    gdf_sucesso = gdf_recife[gdf_recife['temperatura_media_estimada'].notna()].copy()
                    gdf_falha = gdf_recife[gdf_recife['temperatura_media_estimada'].isna()].copy()
                    
                    projected_crs = "EPSG:31985"
                    gdf_sucesso_proj = gdf_sucesso.to_crs(projected_crs)
                    gdf_falha_proj = gdf_falha.to_crs(projected_crs)

                    points_sucesso = np.array([pt.coords[0] for pt in gdf_sucesso_proj.geometry.centroid])
                    values_sucesso = gdf_sucesso_proj['temperatura_media_estimada'].values
                    points_falha = np.array([pt.coords[0] for pt in gdf_falha_proj.geometry.centroid])

                    print("Interpolando valores...")
                    temp_interpolada = griddata(points_sucesso, values_sucesso, points_falha, method='nearest')
                    
                    gdf_recife.loc[gdf_falha.index, 'temperatura_media_estimada'] = temp_interpolada
                    print(f"✅ Interpolação concluída. {len(gdf_falha)} valores de temperatura foram estimados.")

                elif falhas == len(gdf_recife):
                    print("⚠️ Falha total no zonal_stats. Usando 29°C como fallback final.")
                    gdf_recife['temperatura_media_estimada'] = 29.0
                
                gdf_recife['temperatura_media_estimada'] = gdf_recife['temperatura_media_estimada'].fillna(gdf_recife['temperatura_media_estimada'].median())
                
                mean_temp_final = gdf_recife['temperatura_media_estimada'].mean()
                print(f"Média da cidade (antes do ajuste): {mean_temp_final:.2f}°C")

                # --- NOVO: Ajuste de Realidade ---
                REALISTIC_MIN_AVG_TEMP = 28.0 # Média mínima realista para a superfície de Recife
                if mean_temp_final < REALISTIC_MIN_AVG_TEMP:
                    adjustment_factor = REALISTIC_MIN_AVG_TEMP - mean_temp_final
                    print(f"⚠️ Média irrealista. Aplicando ajuste de +{adjustment_factor:.2f}°C em todos os setores.")
                    gdf_recife['temperatura_media_estimada'] += adjustment_factor
                
                print(f"✅ Temperaturas da NASA processadas. Média final da cidade: {gdf_recife['temperatura_media_estimada'].mean():.2f}°C")

        except Exception as e:
            print(f"❌ ERRO ao processar o GeoTIFF: {e}")
            print("🔄 Usando 29°C como fallback.")
            gdf_recife['temperatura_media_estimada'] = 29.0

    # --- 3. Cálculo do Índice e Salvamento ---
    print("\n--- 3. Calculando Índice de Vulnerabilidade e Salvando Resultados ---")
    temp_norm = _normalize(gdf_recife['temperatura_media_estimada'])
    dens_norm = _normalize(gdf_recife['densidade_pop'])
    renda_norm_inv = 1 - _normalize(gdf_recife['renda_corrigida'])
    gdf_recife['indice_vulnerabilidade'] = (temp_norm * 0.5) + (renda_norm_inv * 0.3) + (dens_norm * 0.2)

    colunas_frontend = ['CD_CENSITARIO', 'NM_BAIRRO', 'indice_vulnerabilidade', 'densidade_pop', 'renda_corrigida', 'temperatura_media_estimada', 'geometry']
    gdf_recife_4326 = gdf_recife.to_crs(epsg=4326)
    gdf_recife_4326[colunas_frontend].to_file(OUTPUT_GEOJSON_FILE, driver='GeoJSON')
    print(f"✅ Ficheiro de dados final '{OUTPUT_GEOJSON_FILE}' salvo com sucesso.")
    
    print("\n--- ANÁLISE COMPLETA CONCLUÍDA ---")
    return True

# --- 3. CONFIGURAÇÃO DO SERVIDOR FLASK ---
app = Flask(__name__)
app.name = "main"

# CORS dinâmico para produção
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CORS(app, resources={r"/api/*": {"origins": FRONTEND_URL}})

gdf_cache = None

def get_data():
    global gdf_cache
    if gdf_cache is None:
        if not os.path.exists(OUTPUT_GEOJSON_FILE):
            # Tenta rodar a análise se o arquivo não existir na inicialização
            print(f"Ficheiro de dados '{OUTPUT_GEOJSON_FILE}' não encontrado. Tentando gerar agora...")
            if not run_full_analysis():
                 print("❌ Falha ao gerar o ficheiro de dados. A API de dados não funcionará.")
                 return None
        
        try:
            gdf_cache = gpd.read_file(OUTPUT_GEOJSON_FILE)
        except Exception as e:
            print(f"❌ Erro ao ler o ficheiro GeoJSON: {e}")
            return None
    return gdf_cache

@app.route('/api/data')
def get_vulnerability_data():
    data = get_data()
    if data is None:
        return jsonify({"error": "Ficheiro de dados não encontrado ou inválido."}), 500
    return jsonify(json.loads(data.to_json()))

@app.route('/api/bairros/summary')
def get_bairros_summary():
    data = get_data()
    if data is None:
        return jsonify({"error": "Dados não disponíveis."}), 500
    
    bairro_summary = data.groupby('NM_BAIRRO').agg(
        NM_BAIRRO=('NM_BAIRRO', 'first'),
        indice_vulnerabilidade_media=('indice_vulnerabilidade', 'mean'),
        temperatura_media=('temperatura_media_estimada', 'mean'),
        renda_media=('renda_corrigida', 'mean'),
        densidade_media=('densidade_pop', 'mean'),
        contagem_setores=('CD_CENSITARIO', 'count')
    )
    
    bairro_summary = bairro_summary.sort_values(by='indice_vulnerabilidade_media', ascending=False).reset_index(drop=True)
    bairro_summary['rank'] = bairro_summary.index + 1
    
    return jsonify(bairro_summary.to_dict('records'))

@app.route('/api/llm', methods=['POST'])
def get_llm_analysis():
    sector_data = request.json
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        return jsonify({"error": "Chave da API Gemini não configurada no backend."}), 500
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
    system_prompt = "Aja como um planejador urbano especialista em justiça climática. A sua resposta deve ser em português."
    user_prompt = f"""Analise os dados do seguinte setor censitário em Recife:
- Bairro: {sector_data.get('NM_BAIRRO', 'N/A')}
- Índice de Vulnerabilidade (0 a 1): {sector_data.get('indice_vulnerabilidade', 0):.2f}
- Temperatura Média Estimada: {sector_data.get('temperatura_media_estimada', 0):.1f}°C
- Densidade Populacional: {sector_data.get('densidade_pop', 0):.0f} hab/km²
- Renda Média Corrigida (Estimativa): R$ {sector_data.get('renda_corrigida', 0):.0f}

Com base nestes dados:
1. Faça um diagnóstico conciso da criticidade da área.
2. Proponha UMA intervenção de pequena escala e alto impacto (ex: parque de bolso, corredor verde, pintura de telhados com cores claras).
3. Estime o impacto da sua sugestão. Por exemplo, assuma que a intervenção reduz a temperatura local em 2°C e recalcule o índice de vulnerabilidade (apresente o cálculo de forma simplificada).
Use **negrito** para destacar a recomendação e a melhoria percentual."""
    try:
        response = requests.post(api_url, json={"contents": [{"parts": [{"text": user_prompt}]}], "systemInstruction": {"parts": [{"text": system_prompt}]}})
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"analysis_text": text})
    except Exception as e:
        return jsonify({"error": f"Falha na comunicação com a API da Gemini: {str(e)}"}), 500

# --- 4. EXECUÇÃO PRINCIPAL ---
if __name__ == '__main__':
    # O Gunicorn, em produção, não executa esta parte. Isto é apenas para desenvolvimento local.
    if not os.path.exists(OUTPUT_GEOJSON_FILE):
        run_full_analysis()
    else:
        print(f"Ficheiro de dados '{OUTPUT_GEOJSON_FILE}' já existe. A saltar a análise inicial.")
        
    print("\n--- INICIANDO SERVIDOR FLASK ---")
    
    # A Render e outros provedores de nuvem definem a porta via variável de ambiente PORT
    port = int(os.environ.get('PORT', 5001))
    
    # Em produção, o Gunicorn é o responsável. O app.run() é para rodar localmente.
    app.run(debug=True, port=port)