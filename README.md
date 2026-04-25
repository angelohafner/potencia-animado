# Animacao de potencia em regime senoidal

Projeto Python didatico para gerar um GIF mostrando como a defasagem entre tensao e corrente altera a potencia instantanea, a potencia ativa, a potencia reativa, a potencia aparente e o triangulo de potencias.

## Estrutura

- `main.py`: ponto de entrada do projeto.
- `config.py`: parametros da simulacao na classe `SimulationConfig`.
- `signal_model.py`: calculo de `v(t)`, `i(t)` e `p(t)`.
- `power_model.py`: calculo de `P`, `Q`, `S` e `FP`.
- `animator.py`: montagem do grafico temporal combinado, triangulo de potencias e gravacao do GIF.
- `output/`: pasta gerada automaticamente com o GIF final.

## Instalar dependencias

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Em Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Rodar

```bash
python main.py
```

O GIF sera salvo em:

```text
output/power_triangle_animation.gif
```

## Layout da animacao

O grafico temporal mostra um ciclo completo de tensao, corrente e potencia instantanea no mesmo eixo. Para deixar as amplitudes comparaveis, os sinais sao normalizados como `1.4 * v(t) / Vp`, `1.1 * i(t) / Ip` e `p(t) / 2S`. A potencia instantanea aparece como area translucida e linha azul opaca.

O triangulo de potencias fica abaixo do grafico temporal e ocupa uma area maior da figura para facilitar a leitura.

As escalas do grafico temporal e do triangulo de potencias sao fixas durante toda a animacao. Os eixos mantem os rotulos, mas nao exibem numeros.

Nao ha varredura amostra por amostra dentro do ciclo temporal. Cada quadro mostra o ciclo completo para um valor de `phi`, e a animacao principal e a mudanca do triangulo de potencias conforme o angulo varia.

## Ajustar parametros

Edite os valores padrao em `config.py` ou crie uma instancia personalizada de `SimulationConfig` em `main.py`.

Principais parametros:

- `phi_start_deg`, `phi_end_deg`, `phi_step_deg`: faixa de defasagem em graus. O padrao atual usa `phi_start_deg = -90`, `phi_end_deg = -90` e `phi_step_deg = 15`, interpretando inicio e fim iguais como uma volta completa.
- `samples_per_cycle`: quantidade de pontos usados para desenhar o ciclo completo no grafico temporal.
- `fps`: quadros por segundo do GIF.
- `hold_time_seconds`: duracao de cada angulo no GIF.
- `voltage_rms`, `current_rms`, `frequency_hz`: parametros eletricos da simulacao.
- `figure_dpi`: resolucao da figura gerada para cada frame.

Para testes mais rapidos, aumente `phi_step_deg` ou reduza `samples_per_cycle`.

## Observacao sobre GIFs longos

O projeto usa o writer `GIF-FI` do `imageio`, baseado em FreeImage. O GIF e gravado com frames completos para evitar artefatos de recorte em alguns visualizadores. Na primeira execucao, se o binario do FreeImage ainda nao existir na maquina, o proprio script tenta baixa-lo automaticamente.
