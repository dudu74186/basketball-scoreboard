#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Combina o dataset público com os dados anotados no CVAT.

O ponto crítico aqui é a **ordem das classes**. Os arquivos de label do YOLO
guardam o índice numérico, não o nome: se `ball` for 0 num dataset e 1 no
outro, o treino aprende trocado — e **não emite erro nenhum**. O problema só
aparece no resultado ruim, depois de horas de GPU.

Por isso este script recusa a juntar quando as listas divergem, em vez de
tentar adivinhar. Melhor falhar aqui do que descobrir depois.

Uso:
    python juntar_datasets.py
    python juntar_datasets.py --saida ../datasets/combinado.yaml
"""

import sys
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
DATASETS = RAIZ_IA / "datasets"

PUBLICO = DATASETS / "basketball-detection-dn6fg"
PROPRIO = DATASETS / "proprio"


def ler_classes(yaml_path: Path) -> list[str] | None:
    """Extrai a lista `names` de um data.yaml, sem depender de pyyaml.

    O formato do Roboflow/CVAT é simples o bastante para isso, e evitar a
    dependência mantém o script utilizável em qualquer ambiente.
    """
    if not yaml_path.exists():
        return None

    texto = yaml_path.read_text(encoding="utf-8")
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha.startswith("names:"):
            continue
        valor = linha.split(":", 1)[1].strip()
        if valor.startswith("["):                      # names: ['a', 'b']
            itens = valor.strip("[]").split(",")
            return [i.strip().strip("'\"") for i in itens if i.strip()]

    # Formato em lista, uma classe por linha:
    #   names:
    #     - ball
    #     - basket
    classes, coletando = [], False
    for linha in texto.splitlines():
        if linha.strip().startswith("names:"):
            coletando = True
            continue
        if coletando:
            despido = linha.strip()
            if despido.startswith("-"):
                classes.append(despido[1:].strip().strip("'\""))
            elif despido and not despido.startswith("#"):
                break                                   # acabou o bloco
    return classes or None


def achar_splits(raiz: Path) -> dict[str, Path]:
    """Localiza as pastas de imagens de treino/validação dentro do dataset.

    O CVAT exporta com nomes um pouco diferentes do Roboflow, então vale
    procurar em vez de assumir uma estrutura só.
    """
    encontrados = {}
    for nome, alternativas in (("train", ("train", "Train", "images/train")),
                               ("val", ("valid", "val", "Validation", "images/val"))):
        for alt in alternativas:
            for candidato in (raiz / alt / "images", raiz / alt):
                if candidato.is_dir() and any(candidato.iterdir()):
                    encontrados[nome] = candidato
                    break
            if nome in encontrados:
                break
    return encontrados


def main() -> int:
    saida = Path(sys.argv[sys.argv.index("--saida") + 1]) if "--saida" in sys.argv \
        else DATASETS / "combinado.yaml"

    classes_publico = ler_classes(PUBLICO / "data.yaml")
    if not classes_publico:
        print(f"não achei as classes em {PUBLICO / 'data.yaml'}", file=sys.stderr)
        return 1
    print(f"  público: {classes_publico}")

    if not PROPRIO.exists():
        print(f"\n{PROPRIO} não existe.\n"
              "  Exporte do CVAT em formato YOLOv8 Detection (com 'Save images')\n"
              "  e descompacte lá, uma pasta por tarefa.", file=sys.stderr)
        return 1

    # Cada tarefa exportada do CVAT vira uma subpasta com seu próprio yaml.
    proprios = sorted(p for p in PROPRIO.iterdir() if p.is_dir())
    if not proprios:
        print(f"nenhuma pasta dentro de {PROPRIO}", file=sys.stderr)
        return 1

    treinos = [achar_splits(PUBLICO).get("train")]
    validacoes = [achar_splits(PUBLICO).get("val")]

    for pasta in proprios:
        yaml_proprio = next(pasta.glob("*.yaml"), None)
        classes = ler_classes(yaml_proprio) if yaml_proprio else None

        if classes is None:
            print(f"  {pasta.name}: sem data.yaml legível — PULANDO", file=sys.stderr)
            continue

        # A verificação que justifica este script existir.
        if classes != classes_publico:
            print(f"\n  ✗ {pasta.name}: {classes}", file=sys.stderr)
            print("\n  As classes NÃO batem com as do dataset público.", file=sys.stderr)
            print("  Os labels YOLO guardam o índice, não o nome: juntar assim", file=sys.stderr)
            print("  faria o treino aprender trocado, sem dar erro.", file=sys.stderr)
            print(f"\n  Esperado: {classes_publico}", file=sys.stderr)
            print("  Corrija a ordem dos labels no CVAT e exporte de novo.", file=sys.stderr)
            return 1

        splits = achar_splits(pasta)
        if "train" not in splits:
            print(f"  {pasta.name}: sem imagens de treino — PULANDO", file=sys.stderr)
            continue

        print(f"  ✓ {pasta.name}: {len(list(splits['train'].glob('*')))} imagens")
        treinos.append(splits["train"])

    treinos = [t for t in treinos if t]
    validacoes = [v for v in validacoes if v]

    if len(treinos) < 2:
        print("\nnada do CVAT foi aproveitado — nada a combinar", file=sys.stderr)
        return 1

    # A validação fica SÓ com o dataset público, de propósito: medir no
    # mesmo conjunto de antes é o que permite comparar o treino novo com o
    # anterior. Misturar dados novos na validação mudaria a régua.
    linhas = ["# Gerado por juntar_datasets.py — não editar à mão.",
              "# Validação usa apenas o dataset público, para a métrica",
              "# continuar comparável com o treino anterior.",
              "train:"]
    linhas += [f"  - {t.resolve()}" for t in treinos]
    linhas.append("val:")
    linhas += [f"  - {v.resolve()}" for v in validacoes]
    linhas.append(f"nc: {len(classes_publico)}")
    linhas.append(f"names: {classes_publico}")

    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"\n  {saida}")
    print(f"  {len(treinos)} fontes de treino, classes {classes_publico}")
    print(f"\n  treinar com:  DATA_YAML={saida} NOME_RUN=bola_aro_v2 python treinar.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
