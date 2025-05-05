# ipeaindices
Biblioteca Python para obter índices econômicos (IPCA, INCC-M e IGP-M).

O [IPEA](https://www.ipea.gov.br/portal/) (Instituto de Pesquisa Econômica Aplicada) é uma fundação pública federal vinculada ao Ministério do Planejamento e Orçamento. Suas atividades de pesquisa fornecem suporte técnico e institucional às ações governamentais para a formulação e reformulação de políticas públicas e programas de desenvolvimento brasileiros. Os trabalhos do Ipea são disponibilizados para a sociedade por meio de inúmeras e regulares publicações eletrônicas, impressas, e eventos.

## Instalação
### Usando o pip
TODO

### Manual
1. Clone este repositório ou faça download do pacote:  
```
https://github.com/nukhes/ipeaindices
cd ipeaindices
```

2. Crie e ative um ambiente virtual:  
```bash
python3 -m venv .venv  
source .venv/bin/activate      # Linux/macOS  
.venv\Scripts\activate.bat     # Windows
```

3. Instale o pacote em modo “editable”:  
```bash
pip install -e .
```

## Uso
```python
from igpmcalc.indices import get_ipca, get_incc, get_igpm

# Últimos valores disponíveis  
ipca_valor = get_ipca()  
incc_valor = get_incc()  
igpm_valor = get_igpm()

# Valores mensais de um ano específico  
valores_2024 = get_igpm(2024)

# Média anual de um único ano  
media_2024 = get_igpm(2024, average=True)

# Valores mensais de vários anos  
df_anos = get_igpm([2022, 2023])

# Média de vários anos  
media_2022_23 = get_igpm([2022, 2023], average=True)
```
