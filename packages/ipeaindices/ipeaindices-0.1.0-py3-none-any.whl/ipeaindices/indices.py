import ipeadatapy as ipea
import pandas as pd

__all__ = ['get_ipca', 'get_incc', 'get_igpm']

# Códigos das séries conforme API do IPEA
_SERIES = {
    'ipca': 'PRECOS12_IPCA12',   # IPCA mensal
    'incc': 'IGP12_INCC12',      # INCC-M mensal
    'igpm': 'IGP12_IGPM12'       # IGP-M mensal
}

class IpeaIndex:
    """
    Classe para obter e consultar a IPEADATAPY de uma forma simples para humanos.

    Métodos:
        fetch() -> pd.DataFrame
            Busca toda a série e retorna um DataFrame.
        get(year=None, average=False)
            Se year for None, retorna último valor.
            Se year for int, retorna lista de valores mensais ou média.
            Se year for coleção de ints, retorna DataFrame filtrado ou média.
    """
    def __init__(self, key: str):
        if key not in _SERIES:
            raise ValueError(f"Série desconhecida: {key}")
        self.series_id = _SERIES[key]
        self.df = None

    def fetch(self) -> pd.DataFrame:
        # Carrega dados da API
        self.df = ipea.timeseries(self.series_id)
        return self.df

    def get(self, year=None, average: bool = False):
        df = self.fetch() if self.df is None else self.df

        # Caso nenhum ano seja fornecido, retorna o último valor disponível
        if year is None:
            last = df.iloc[-1]
            print(f"Ano: {last['YEAR']} - Valor: {last['VALUE (-)']:.3f}")
            return last['VALUE (-)']

        # Consulta para um único ano
        if isinstance(year, int):
            subset = df[df['YEAR'] == year]
            if subset.empty:
                print(f"Nenhum valor encontrado para o ano {year}.")
                return None
            if average:
                media = subset['VALUE (-)'].mean()
                print(f"Média de {year}: {media:.3f}")
                return media
            else:
                for _, row in subset.iterrows():
                    print(f"Mês {row['MONTH']:02d}/{year} - Valor: {row['VALUE (-)']:.3f}")
                return subset['VALUE (-)'].tolist()

        # Consulta para múltiplos anos
        if isinstance(year, (list, tuple, set)):
            subset = df[df['YEAR'].isin(year)]
            if subset.empty:
                print(f"Nenhum valor encontrado para os anos: {year}")
                return None
            if average:
                media = subset['VALUE (-)'].mean()
                print(f"Média dos anos {year}: {media:.3f}")
                return media
            else:
                for _, row in subset.iterrows():
                    print(f"Mês {row['MONTH']:02d}/{row['YEAR']} - Valor: {row['VALUE (-)']:.3f}")
                return subset

        raise ValueError("Parâmetro 'year' deve ser None, int ou coleção de ints.")

def get_ipca(year=None, average: bool = False):
    """Retorna IPCA. year=None -> último; int -> mensal ou média; coleção -> DataFrame ou média."""
    return IpeaIndex('ipca').get(year=year, average=average)


def get_incc(year=None, average: bool = False):
    """Retorna INCC-M. year=None -> último; int -> mensal ou média; coleção -> DataFrame ou média."""
    return IpeaIndex('incc').get(year=year, average=average)


def get_igpm(year=None, average: bool = False):
    """Retorna IGP-M. year=None -> último; int -> mensal ou média; coleção -> DataFrame ou média."""
    return IpeaIndex('igpm').get(year=year, average=average)
