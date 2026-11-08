#!/usr/bin/env python3
"""Example deck built with deck_kit: 6G network slicing, dark 16:9.

    uv run --with python-pptx python examples/example_deck.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from deck_kit import Deck, audit  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

d = Deck()
T = d.t

# ---- 1. cover -----------------------------------------------------------
d.title_slide(
    kicker="SEM FIO  ·  IA  ·  IoE",
    title="",
    parts=[("6G ", "x"), ("Fatiamento", "em"), (" de Rede", "x")],
    subtitle="Do 5G à Rede Inteligente de Tudo: como as fatias virtuais são criadas, selecionadas e tornadas autossustentáveis.",
    meta="REDE INTELIGENTE DE TUDO  ·  2026",
)

# ---- 2. three cards -----------------------------------------------------
s = d.content("Fundamentos", "5G: uma rede baseada em serviços")
d.text(s, "O 5G substituiu o modelo “tamanho único” por um modelo baseado em serviços, com três classes principais.")
d.cards(s, [
    ("eMBB", "Banda Larga Móvel Aprimorada", "Alta largura de banda e alto throughput.", T.accent),
    ("uRLLC", "Comunicação Ultraconfiável de Baixa Latência", "Latência submilissegundo para tarefas críticas.", T.accent2),
    ("mMTC", "Comunicação Massiva entre Máquinas", "Enorme número de dispositivos IoT.", T.accent2),
], top=2.8, height=1.7)
d.text(s, "Tecnologias: sub-6 GHz + mmWave, MIMO massivo, SDN, NFV e SBA.", top=4.85, size=14, color=T.text)

# ---- 3. callout + numbered steps ---------------------------------------
s = d.content("Fatiamento de Rede", "Uma rede, muitas fatias lógicas")
d.callout(s, [
    ("Divide uma rede física em ", "x"),
    ("múltiplas fatias lógicas", "em"),
    (". Cada uma com recursos virtuais dedicados, personalizada para um ", "x"),
    ("SLA", "q"), (" e ", "x"), ("QoS", "q"), (" específicos.", "x"),
], top=2.05)
d.text(s, "Três camadas, gerenciadas por um orquestrador:", top=3.4, size=16)
d.steps(s, [
    ("Serviço / Aplicação", "Requisitos de negócio e de usuário"),
    ("Função de Rede", "NFV · SDN · MANO"),
    ("Infra & RAN", "Rádio e espectro virtualizados"),
], top=3.95, height=1.05)

# ---- 4. bullets ---------------------------------------------------------
s = d.content("Camada de Função de Rede", "Virtualizando a função de rede")
d.text(s, "VNF  →  CNF  →  Pod Kubernetes        uma função = um pod", size=18, color=T.accent)
d.bullets(s, [
    ("NFV", "desacopla o software do hardware, executando VNFs em servidores comuns."),
    ("VNF → CNF → Pod", "uma VNF em uma VM; refatorada como nativa de nuvem, roda como contêiner."),
    ("SDN", "separa o plano de controle do plano de dados para rotear o tráfego."),
    ("NFV MANO", "coordena o ciclo de vida, a implantação e o mapeamento de recursos por fatia."),
], top=2.75)

# ---- 5. code block ------------------------------------------------------
s = d.content("Implementação", "Pseudo-implementação: K8s · VM · Bare-metal")
d.code(s, [
    ("# Kubernetes: CNF (contêiner)", T.faint),
    ("apiVersion: v1", T.muted),
    ("kind: Pod                 # 1 CNF = 1 Pod", T.muted),
    ("spec:", T.muted),
    ("  resources: { cpu: 4, memory: 8Gi }", T.text),
    ("  SR-IOV (Multus)  ->  NIC dedicada por fatia", T.accent),
    ("  DPDK (userspace) ->  sem passagem pelo kernel", T.accent),
    ("# VM: VNF (hipervisor)", T.faint),
    ("vnf: amf / upf / firewall      # imagem em VM", T.muted),
    ("# Bare-metal: sem camada extra", T.faint),
    ("binario nativo + DPDK + CPU pinning", T.accent2),
], top=2.0, height=4.3, size=12)
d.text(s, "A mesma fatia pode rodar em três substratos, do contêiner ao metal puro.", top=6.5, size=15)

# ---- 6. table -----------------------------------------------------------
s = d.content("Os Números", "IMT-2020  →  IMT-2030")
d.table(s,
        ["Métrica", "5G", "Meta 6G"],
        [["Taxa de pico", "20 Gbit/s", "50 / 100 / 200 Gbit/s"],
         ["Latência", "1 ms", "0,1–1 ms"],
         ["Confiabilidade", "10⁻⁵", "10⁻⁵ – 10⁻⁷"],
         ["Espectro", "sub-6 GHz + mmWave", "THz"]],
        accent_cols={1: T.accent2, 2: T.accent},
        col_w=[3.2, 3.5, 5.23])

# ---- 7. section divider -------------------------------------------------
d.section("Parte 2", "O 6G em operação", "Da métrica observada à fatia reconfigurada.")

# ---- 8. KPI row ---------------------------------------------------------
s = d.content("Ciclo Fechado", "O laço que roda sozinho")
d.flow(s, [
    ("Ler métricas", "throughput · latência · PER"),
    ("IA decide", "DRL / GNN escolhe a ação"),
    ("Mudar configuração", "SLA · recursos · rota"),
    ("Atualizar o cluster", "aplica na fatia (K8s)"),
], top=2.6)
d.kpis(s, [
    ("1 ms", "Latência uRLLC", "submilissegundo em tarefas críticas"),
    ("10⁸/km²", "Densidade de conexões", "meta IMT-2030"),
    ("THz", "Espectro 6G", "sensoriamento ISAC"),
], top=4.7, height=1.6)

# ---- 9. quote -----------------------------------------------------------
s = d.content("A Mudança Central", "5G encontra → 6G é a inteligência")
d.quote(s, "Anything can be made connected, intelligent, and aware of its environment.", "Princípio IoE", top=2.1, height=1.5)
d.text(s, "O 5G tornou a rede definida por software e fatiável. O 6G a torna inteligente, sobre três pilares: sem fio, IA e IoE.", top=4.0, size=16)

# ---- 10. references -----------------------------------------------------
s = d.content("Referências", "Fontes")
d.references(s, [
    ("X. Foukas et al.", "“Network Slicing in 5G: Survey and Challenges”, IEEE Commun. Mag., 2017."),
    ("H. Pennanen et al.", "“6G: The Intelligent Network of Everything”, IEEE Access, 2024."),
    ("A. Dogra et al.", "“Survey on Beyond 5G Network With the Advent of 6G”, IEEE Access, 2021."),
    ("C.-X. Wang et al.", "“On the Road to 6G: Visions, Requirements, Key Technologies and Testbeds”, IEEE Commun. Surveys Tuts., 2023."),
    ("M. Shafi et al.", "“5G: A Tutorial Overview of Standards, Trials, Challenges, Deployment and Practice”, IEEE JSAC, 2017."),
    ("P. Mach, Z. Becvar", "“Mobile Edge Computing: A Survey on Architecture and Computation Offloading”, IEEE Commun. Surveys Tuts., 2017."),
])

out = os.path.join(HERE, "example.pptx")
d.save(out)
print("saved", out)

problems = audit(out)
if problems:
    for p in problems:
        print("audit:", p)
else:
    print("audit: clean")
