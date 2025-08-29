import numpy as np
import matplotlib.pyplot as plt

def afronden():
    # Afrondingsfunctie volgens jouw regels
    def afronden(x):
        laatste_cijfer = int(x * 100) % 10
        afrond_map = {
            0: 0,
            1: 0,
            2: 0,
            3: 5,
            4: 5,
            5: 5,
            6: 5,
            7: 5,
            8: 0,
            9: 0
        }
        afrond_cent = afrond_map[laatste_cijfer]
        origineel_cent = int(round((x - int(x)) * 100))
        nieuwe_cent = origineel_cent - (origineel_cent % 10) + afrond_cent
        if nieuwe_cent >= 100:
            x = int(x) + 1 + (nieuwe_cent - 100)/100
        else:
            x = int(x) + nieuwe_cent/100
        return round(x, 2)

    # Benford-verdeling voor eerste cijfers
    def benford_samples(n):
        benford_probs = [np.log10(1 + 1/d) for d in range(1, 10)]
        eerste_cijfers = np.random.choice(range(1, 10), size=n, p=benford_probs)
        rest = np.random.uniform(0, 100, size=n)
        return eerste_cijfers * 10 + rest

    # Simulatie
    np.random.seed(42)
    n = 1_000_000
    bedragen = benford_samples(n)
    bedragen = np.round(bedragen, 2)

    afgerond = np.array([afronden(b) for b in bedragen])
    verschil = afgerond - bedragen

    # Resultaten
    gemiddeld_verschil = np.mean(verschil)
    print(f"Gemiddeld afrondverschil: {gemiddeld_verschil:.5f} euro")

    # Optioneel: histogram tonen
    plt.hist(verschil, bins=np.arange(-0.1, 0.11, 0.01), edgecolor='black')
    plt.title("Verdeling van afrondverschillen")
    plt.xlabel("Afrondverschil (euro)")
    plt.ylabel("Aantal")
    plt.show()


def kassaverschil():
    import matplotlib.pyplot as plt

    # Realistische verdeling van eindcijfers op basis van kassadata (bijvoorbeeld uit studies)
    # Veelgebruikte verdeling voor laatste cijfers in prijzen (uit prijspsychologie en retaildata)
    # Bronnen wijzen vaak op een piek bij 9 en 5
    kassa_verdeling = {
        0: 0.08,
        1: 0.05,
        2: 0.06,
        3: 0.07,
        4: 0.08,
        5: 0.15,
        6: 0.10,
        7: 0.09,
        8: 0.12,
        9: 0.20
    }

    # Aantal samples
    n = 1_000_000
    last_cent_values = list(kassa_verdeling.keys())
    probabilities = list(kassa_verdeling.values())

    # Genereer bedragen volgens deze verdeling
    eindcenten = np.random.choice(last_cent_values, size=n, p=probabilities)
    basisbedragen = np.random.uniform(1, 100, size=n)
    bedragen_kassa = np.floor(basisbedragen) + eindcenten / 100

    # Bereken afrondverschillen
    verschillen_kassa = np.array([afronding_verschil(x) for x in bedragen_kassa])
    gemiddeld_kassa_verschil = verschillen_kassa.mean()
    gemiddeld_kassa_verschil_cent = gemiddeld_kassa_verschil * 100  # in centen

    # Toon ook histogram van afrondverschillen
    plt.hist(verschillen_kassa * 100, bins=np.arange(-3, 3.5, 0.5), edgecolor='black')
    plt.title("Afrondverschillen bij realistische kassadata")
    plt.xlabel("Afrondverschil (cent)")
    plt.ylabel("Aantal")
    plt.grid(True)
    plt.show()

    gemiddeld_kassa_verschil_cent

kassaverschil()