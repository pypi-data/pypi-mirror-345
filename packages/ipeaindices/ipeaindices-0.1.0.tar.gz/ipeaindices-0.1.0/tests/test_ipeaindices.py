from ipeaindices import get_ipca, get_incc, get_igpm
import pandas as pd

def test_get_ipca_ultimo():
    valor = get_ipca()
    assert isinstance(valor, float), "IPCA atual deve ser float"

def test_get_incc_ultimo():
    valor = get_incc()
    assert isinstance(valor, float), "INCC atual deve ser float"

def test_get_igpm_ultimo():
    valor = get_igpm()
    assert isinstance(valor, float), "IGPM atual deve ser float"

def test_get_igpm_ano_mensal():
    valores = get_igpm(2023)
    assert isinstance(valores, list), "Valores mensais devem estar em uma lista"
    assert all(isinstance(v, float) for v in valores), "Todos os valores devem ser float"

def test_get_igpm_ano_media():
    media = get_igpm(2023, average=True)
    assert isinstance(media, float), "Média deve ser float"

def test_get_igpm_multiplos_anos():
    df = get_igpm([2022, 2023])
    assert isinstance(df, pd.DataFrame), "Retorno para múltiplos anos deve ser um DataFrame"
    assert {'YEAR', 'MONTH', 'VALUE (-)'}.issubset(df.columns), "DataFrame deve conter colunas padrão"

def test_get_igpm_multiplos_anos_media():
    media = get_igpm([2022, 2023], average=True)
    assert isinstance(media, float), "Média de múltiplos anos deve ser float"

def test_get_ano_inexistente():
    resultado = get_ipca(100)  # assumindo que não há dados de "100"
    assert resultado is None, "Deve retornar None para anos sem dados"
