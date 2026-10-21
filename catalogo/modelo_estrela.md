# Modelo estrela (camada gold)

Grão da fato: **uma entrevista do Vigitel**, edições de 2010 a 2024 (sem 2022), 615.877 linhas. As medidas são indicadores 0/1 (`alcabu`, `bebe_mensal`, `costuma_beber_q35`) e pesos; as prevalências são calculadas na análise como média ponderada pelo `peso_norm` (D4), e não guardadas na fato.

```mermaid
erDiagram
    fato_entrevista }o--|| dim_edicao : edicao_sk
    fato_entrevista }o--|| dim_capital : capital_sk
    fato_entrevista }o--|| dim_geracao : geracao_sk
    fato_entrevista }o--|| dim_escolaridade : escolaridade_sk
    fato_entrevista }o--|| dim_faixa_etaria : faixa_etaria_sk
    fato_entrevista }o--|| dim_sexo : sexo_sk

    fato_entrevista {
        string entrevista_id PK "edicao + linha do arquivo (D10)"
        bigint edicao_sk FK
        bigint capital_sk FK
        bigint geracao_sk FK
        bigint escolaridade_sk FK
        bigint faixa_etaria_sk FK
        bigint sexo_sk FK
        bigint idade
        bigint ano_nascimento
        string modo_coleta "fixo ou celular"
        boolean escolaridade_estimada "D8"
        bigint alcabu "consumo abusivo (0/1)"
        bigint bebe_mensal "bebe ao menos 1x/mes (0/1, D6)"
        bigint costuma_beber_q35 "conferencia ate 2023"
        double peso "pesorake2025"
        double peso_norm "soma 1 por edicao (D4)"
        bigint linha_origem "rastreabilidade"
    }
    dim_edicao {
        bigint edicao_sk PK
        bigint ano
        bigint entrevistas
        double pct_celular
        boolean pandemia "D11"
        string filtro_bloco_alcool "D13"
    }
    dim_capital {
        bigint capital_sk PK
        string capital
        string uf
        string regiao "derivada da capital (D12)"
    }
    dim_geracao {
        bigint geracao_sk PK
        string geracao "millennials, zillennials, geracao_z, outra"
        bigint nascimento_inicio
        bigint nascimento_fim
    }
    dim_escolaridade {
        bigint escolaridade_sk PK
        string escolaridade
    }
    dim_faixa_etaria {
        bigint faixa_etaria_sk PK
        string faixa_etaria
    }
    dim_sexo {
        bigint sexo_sk PK
        string sexo
    }
```

**Por que estrela:** as cinco perguntas cortam o mesmo fato (a entrevista) por geração, escolaridade, sexo, faixa etária, capital/região e edição. Cada corte é uma dimensão; nenhuma pergunta precisa de outra tabela de fatos.

**Camadas:**

| Camada | Tabela | Conteúdo |
|---|---|---|
| raw (Volume) | `vigitel-2006-2024-peso-rake-csv.zip` | arquivo oficial, conferido pelo SHA-256 |
| bronze | `bronze_vigitel`, `bronze_coleta_log` | cópia fiel do CSV (486 colunas, texto) + linha de origem; log da coleta |
| silver | `silver_vigitel` | 2010 em diante, 28 colunas, regras S1 a S11 (decisões D1 a D13); sem texto livre (D12) |
| gold | `fato_entrevista` + 6 dimensões | modelo estrela |
| qualidade | `qa_checagens`, `qa_perfil_atributos`, `qa_cobertura` | notebook 04 |
| resultados | `res_*` | P1 a P5, sensibilidades e veredito (notebook 05) |
