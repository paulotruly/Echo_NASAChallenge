import h5py
import numpy as np
import rasterio
from rasterio.transform import from_bounds
import os
import requests  # Adicionado pra download

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
DATA_DIR = os.path.join(BASE_DIR, 'data')  
os.makedirs(DATA_DIR, exist_ok=True)

S3_BASE_URL = 'https://nasah5geojson.s3.us-east-1.amazonaws.com'
HDF5_FILENAME = os.path.join(DATA_DIR, 'ECOv002_L2G_LSTE_41064_015_20251002T225109_0713_01.h5')
OUTPUT_GEOTIFF_PATH = os.path.join(DATA_DIR, 'ECOSTRESS_LST_Recife.tif')

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

INTERNAL_LST_PATH = 'HDFEOS/GRIDS/ECO_L2G_LSTE_70m/Data Fields/LST'
INTERNAL_GEO_METADATA_PATH = 'HDFEOS/ADDITIONAL/FILE_ATTRIBUTES/StandardMetadata'

def process_hdf5_to_geotiff():
    """
    Lê um ficheiro HDF5 do ECOSTRESS, extrai e limpa a camada de Temperatura e salva como GeoTIFF.
    """
    # Baixa HDF5 do S3 se necessário
    hdf5_url = f'{S3_BASE_URL}/ECOv002_L2G_LSTE_41064_015_20251002T225109_0713_01.h5'
    if not download_if_missing(HDF5_FILENAME, hdf5_url):
        print("❌ Falha no download do HDF5. Abortando.")
        return

    if not os.path.exists(HDF5_FILENAME):
        print(f"❌ ERRO: Ficheiro '{HDF5_FILENAME}' não encontrado.")
        return

    print(f"--- Abrindo o ficheiro HDF5: {HDF5_FILENAME} ---")
    
    try:
        with h5py.File(HDF5_FILENAME, 'r') as hdf_file:
            if INTERNAL_LST_PATH not in hdf_file or INTERNAL_GEO_METADATA_PATH not in hdf_file:
                print("❌ ERRO: A estrutura interna do ficheiro HDF5 não é a esperada. Não foi possível encontrar os caminhos para LST ou Metadados.")
                return

            lst_dataset = hdf_file[INTERNAL_LST_PATH]
            lst_data = lst_dataset[:]
            metadata = lst_dataset.attrs
            
            scale_factor = metadata.get('scale_factor')
            add_offset = metadata.get('add_offset')
            fill_value = metadata.get('_FillValue', metadata.get('FillValue', metadata.get('_Fillvalue')))

            if scale_factor is None or add_offset is None or fill_value is None:
                print("❌ ERRO: Metadados essenciais (scale_factor, add_offset, FillValue) não foram encontrados.")
                return

            geo_metadata_group = hdf_file[INTERNAL_GEO_METADATA_PATH]
            lon_min = geo_metadata_group['WestBoundingCoordinate'][()]
            lon_max = geo_metadata_group['EastBoundingCoordinate'][()]
            lat_min = geo_metadata_group['SouthBoundingCoordinate'][()]
            lat_max = geo_metadata_group['NorthBoundingCoordinate'][()]
            
            print("--- Dados e metadados extraídos com sucesso. ---")

            # Conversão para Celsius
            lst_data = lst_data.astype(np.float32)
            lst_data[lst_data == fill_value] = np.nan
            lst_kelvin = (lst_data * scale_factor) + add_offset
            lst_celsius = lst_kelvin - 273.15
            
            # --- Filtro de Qualidade de Dados ---
            lst_celsius[lst_celsius > 80] = np.nan
            lst_celsius[lst_celsius < -50] = np.nan
            
            print(f"Temperaturas convertidas e FILTRADAS. Nova Mín: {np.nanmin(lst_celsius):.2f}°C, Nova Máx: {np.nanmax(lst_celsius):.2f}°C")

            height, width = lst_celsius.shape
            transform = from_bounds(lon_min, lat_min, lon_max, lat_max, width, height)

            print(f"--- Salvando o ficheiro GeoTIFF de saída: {OUTPUT_GEOTIFF_PATH} ---")
            with rasterio.open(
                OUTPUT_GEOTIFF_PATH, 'w', driver='GTiff', height=height, width=width,
                count=1, dtype=lst_celsius.dtype, crs='EPSG:4326', transform=transform, nodata=np.nan
            ) as dst:
                dst.write(lst_celsius, 1)

            print("\n✅ Processamento concluído com sucesso!")
            print(f"➡️ Ficheiro '{OUTPUT_GEOTIFF_PATH}' foi criado com dados válidos e CRS correto!")
            print("➡️ Agora siga os próximos passos.")

    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    process_hdf5_to_geotiff()