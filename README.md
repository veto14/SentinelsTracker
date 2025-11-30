### O Sentinels Tracker é uma aplicação desktop desenvolvida em Python, utilizando a biblioteca customtkinter (CTK) para fornecer uma interface gráfica moderna e focada em UX. O objetivo principal é permitir que jogadores de Sentinels of the Multiverse registrem suas partidas, rastreiem estatísticas de desempenho e obtenham insights estratégicos sobre seus heróis, vilões e ambientes favoritos. Todos os dados são armazenados localmente em um banco de dados SQLite, garantindo privacidade e acesso rápido.

# Funcionalidades em Destaque

Registro Intuitivo: Interface simplificada para registrar jogos Solo e com Time de Vilões (Villain Teams), rastreando a seleção de heróis, vilões, dificuldades e o ambiente.

Dashboard de Visão Geral: Exibe o total de partidas jogadas e rankings rápidos dos heróis e vilões mais usados, além das listas dos melhores e piores heróis por Taxa de Vitória (WR).

Análise Estratégica de Heróis: Uma aba dedicada para analisar o desempenho de Herói + Variante filtrando por dificuldade (Normal, Advanced, Challenge, Ultimate). Os insights incluem:

Vilão mais fácil e mais difícil de enfrentar.

Parceiros e Ambientes mais comuns.

Métrica de Consistência (Desvio Padrão) do desempenho.

Tabelas de Detalhes: Geração de rankings tabulares completos por Vilão, Ambiente, Tamanho do Time e Heróis. O uso de fonte monoespaçada garante alinhamento perfeito das porcentagens de vitória para fácil leitura.

# Tecnologias Utilizadas

#### Python
#### CustomTkinter (CTK)
#### SQLite3

# Como Executar o Projeto

## Instalação e Execução

#### Clone o repositório (ou baixe o arquivo):

git clone [LINK_DO_SEU_REPOSITORIO]
cd SentinelsTracker

## Instale a dependência customtkinter:

pip install customtkinter

## Execute a aplicação:

python tracker.py

##### Ao executar pela primeira vez, o aplicativo criará automaticamente o arquivo de banco de dados sentinels_history.db no mesmo diretório.

###### Este projeto está sob a licença MIT.
