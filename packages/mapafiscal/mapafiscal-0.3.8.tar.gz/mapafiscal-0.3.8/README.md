
# Mapa Fiscal Tributário

## Descrição
O projeto **Mapa Fiscal Tributário** é uma solução desenvolvida para gerenciar cenários e operações fiscais, considerando diferentes contextos tributários como classe fiscal do produto, natureza da operação e estados de origem e destino. Ele foi projetado para ser altamente configurável e modular, permitindo o uso em diversos regimes tributários e perfis de contribuintes.

---

## Principais Componentes

### 1. **Modelos de Dados**
- **`MapaFiscal`**: Representa o mapa fiscal, com classes fiscais, cenários e operações.
- **`ClasseFiscal`**: Detalha a classificação fiscal de produtos, como NCM, origem, segmento e alíquotas.
- **`CenarioFiscal`**: Representa configurações específicas para operações fiscais em determinado contexto.
- **`OperacaoFiscal`**: Define detalhes operacionais como CFOP, CST, alíquotas de ICMS, PIS, COFINS e IPI.

### 2. **Regras Fiscais**
- **`RegraFiscalProcessor`**: Processa as regras tributárias com base no contexto fiscal e nos parâmetros fornecidos, calculando alíquotas de ICMS, PIS, COFINS e IPI.

### 3. **Contextos Fiscais**
- **`ContextoFiscal`**: Interface base para diferentes fontes de dados fiscais.
- **`JSONContexto`**: Implementação que carrega dados fiscais a partir de arquivos JSON.
- **`ContextoFiscalFactory`**: Fabrica contextos fiscais dinamicamente com base em registros.

---

## Casos de Uso

### Cenário: Gerar um Mapa Fiscal com Base em um Arquivo JSON

#### 1. Inicializar repositorio,
Registre um contexto fiscal baseado no formato JSON:
```python
    from mapafiscal.infrastructure.persistence import JSONRepositorio
    from mapafiscal.infrastructure.admin import iniciar_repositorio

    repositorio = JSONRepositorio(".\\etc")        
    iniciar_repositorio(repositorio)   
```

#### 2. Construir o Mapa Fiscal
Use o processador de regras fiscais para criar um mapa fiscal:
```python
from mapafiscal.application.cenario_builder import CenarioBuilder

builder = CenarioBuilder(repositorio)
mapa_fiscal = builder.build_from_file("cenario_example.json")     
```

#### 3. Exportar Resultado
Exporte os resultados para um arquivo Excel:
```python
from mapafiscal.application import ExcelExporter

excel = ExcelExporter(mapa_fiscal)
excel.to_excel("output.xlsx")
```

---

## Como Executar

### Executar via Linha de Comando
O script 'create_env.py' permite criar o repositorio de dados via terminal:
```bash
python create_env.py -r caminho/para/repositorio
```
A execução também irá criar o arquivo cenario_example.json.
Este arquivo pode ser utilizado para efetuar seus primeiros testes com o mapa fiscal.

O script `build_cenario.py` permite gerar um mapa fiscal diretamente via terminal:
```bash
python build_cenario.py --filename caminho/para/dados.json
```
Este comando gerará um arquivo `mapafiscal.xlsx` contendo os cenários processados.

---

## Estrutura de Arquivos do Projeto
- **`common.py`**: Contém enums e classes comuns usadas em todo o projeto.
- **`model.py`**: Define os modelos de dados principais.
- **`contexto_fiscal.py`**: Define a interface base e funcionalidades gerais para contextos fiscais.
- **`contexto_factory.py`**: Permite criar contextos fiscais dinamicamente.
- **`contexto_registry.py`**: Gerencia registros de diferentes implementações de contexto.
- **`json_contexto.py`**: Implementação de contexto fiscal baseado em JSON.
- **`mapa_fiscal_processor.py`**: Processa cenários e operações fiscais.
- **`build_cenario.py`**: Script para gerar mapas fiscais via terminal.

---

## Contribuições
Contribuições são bem-vindas! Para relatar problemas ou sugerir melhorias, crie uma issue ou envie um pull request.

---

## Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.
