# Endpoints et sources de données

> Annexe de `00_Prompt_MapDee.md`. Tout ce qui suit est **relevé dans le code ou
> dans les rapports**, pas de mémoire. Chaque piège porte le coût qu'il a
> réellement fait payer.

---

## 1. Acquisition temps réel — recorder P1, 5 venues @ 100 ms

Code : `_recupere/recorder/adapters/`. Tourne depuis le 28/07/2026, 10 flux/10.

| venue | WebSocket | souscriptions | REST |
|---|---|---|---|
| **Binance** USDⓈ-M | `wss://fstream.binance.com/stream?streams=` | `<sym>@depth@100ms` | `https://fapi.binance.com/fapi/v1/depth` · `limit=1000` |
| | `wss://fstream.binance.com/market/stream?streams=` | `<sym>@aggTrade` | — |
| **Bybit** linear | `wss://stream.bybit.com/v5/public/linear` | `orderbook.200.<sym>` · `publicTrade.<sym>` | aucun |
| **OKX** SWAP | `wss://ws.okx.com:8443/ws/v5/public` | `{"channel":"books"}` · `{"channel":"trades"}` | `https://www.okx.com/api/v5/public/instruments?instType=SWAP` |
| **Coinbase** | `wss://ws-feed.exchange.coinbase.com` | `level2_batch` · `matches` | aucun |
| **Hyperliquid** | `wss://api.hyperliquid.xyz/ws` | `{"type":"l2Book","coin":…}` · `{"type":"trades","coin":…}` · **`nSigFigs` — voir §1 bis** | aucun |

Keep-alive : Bybit `{"op":"ping"}` · Hyperliquid `{"method":"ping"}`.

### 1 bis. `nSigFigs` — ce qui débloque la portée d'Hyperliquid

**Mesuré et mis en production le 04/08/2026.**

`l2Book` rend **toujours 20 paliers par côté**. À la résolution native ça ne
porte qu'à **±0,03 % du mid**, alors que la bande d'étude va de 0,12 à 0,80 %.
**Le recorder a enregistré Hyperliquid pendant huit jours à 26 fois trop court
pour voir ses propres objets.** `SNAP_BAND` n'y pouvait rien : la limite ne vient
pas de ce qu'on garde, mais de ce que la venue envoie.

`nSigFigs` regroupe les prix — les 20 paliers portent alors bien plus loin.
Mesuré sur BTC à 64 295 $, **une connexion par résolution** :

| `nSigFigs` | pas du prix | portée | couvre 0,12–0,80 % ? |
|---|---|---|---|
| absent | 1 $ | 0,030 % | ❌ |
| 5 | 1 $ | 0,032 % | ❌ — identique au natif |
| **4** | 10 $ | 0,304 % | partiellement |
| **3** | **100 $** | **3,030 %** | ✅ |
| 2 | 1 000 $ | 30,2 % | inexploitable |

En production : deux venues de plus, `hyperliquid_fin` (nSigFigs 4) et
`hyperliquid_large` (nSigFigs 3). Portée réellement enregistrée : **0,857 %**,
écrêtée par `SNAP_BAND = ±1 %`. Code :
`_recupere/recorder/adapters/hyperliquid_agg.py`.

> ⚠️ **Le piège, et il a mordu.** Les messages agrégés ne portent que `coin`,
> `time` et `spread` — **ils ne disent pas de quelle résolution ils viennent**.
> Sur une connexion unique, deux résolutions sont indiscernables. Une première
> attribution faite ainsi s'est révélée **fausse d'un cran** : on croyait qu'il
> fallait `nSigFigs = 4`, c'est **3**. D'où la règle — **une connexion par
> résolution**, jamais de déduction par l'ordre des réponses.

Ce n'est **pas** de la profondeur au sens du L4 : les paliers sont des seaux de
100 $, pas des ordres individuels. Ça sert à **voir** les murs en direct, pas à
les étudier un par un.

**Protocole d'intégrité, un par venue** — ils ne se ressemblent pas, et c'est ce
qui coûte le plus cher à porter :

| venue | mécanisme | resynchronisation |
|---|---|---|
| Binance | chaînage `U` / `u` / `pu` + photo REST | photo REST puis rejeu du tampon |
| Bybit | snapshot/delta chaînés par `u` | **réabonnement au topic** — pas de photo REST |
| OKX | `prevSeqId` (+ CRC32, voir §5) | réabonnement au canal |
| Coinbase | **aucune séquence** | — |
| Hyperliquid | photo complète à chaque message | sans objet |

---

## 2. Temps réel — GON-TV en production

**WebSocket.** Migration du 19/07/2026 vers les **chemins routés**, obligatoire :

```
wss://fstream.binance.com/market/ws/<sym>@aggTrade         POI M15
wss://fstream.binance.com/market/ws/!forceOrder@arr        liquidations
wss://fstream.binance.com/market/ws/!markPrice@arr@1s      mark price
wss://fstream.binance.com/market/stream?streams=…          kline G-Bot
wss://fstream.binance.com/stream?streams=…                 depth (démon)
```

Les trois bases et leurs contenus :

| base | contenu |
|---|---|
| `…/market` | aggTrade, kline, ticker, markPrice, **forceOrder** |
| `…/public` | haute fréquence : **depth**, bookTicker |
| `…/private` | données utilisateur (non utilisé) |

Deux modes sur chaque base : `<base>/ws/<stream>` ou
`<base>/stream?streams=<s1>/<s2>`.

**REST** `https://fapi.binance.com` — **non concerné** par la migration :

```
/fapi/v1/depth?symbol=          /fapi/v1/klines?symbol=
/fapi/v1/aggTrades?symbol=      /fapi/v1/openInterest?symbol=
/fapi/v1/premiumIndex?symbol=   /fapi/v1/time
```

Tout appel des outils passe par `tools/http.js` (`politeFetch`, respect du
`Retry-After`) : le REST `fapi` a un **budget de poids par IP**.

**Spot** (inchangé pendant toute la panne futures, utile comme témoin) :

```
wss://stream.binance.com:9443/ws       ·  /stream
wss://data-stream.binance.vision/ws       miroir data, testé OK
```

---

## 3. Sources historiques

| source | ce que c'est | état |
|---|---|---|
| `data/l4/openbook-202512/` | **L4 Hyperliquid, décembre 2025** — 197 Gio, sur disque | ✅ en place |
| Zenodo **`10.5281/zenodo.18184441`** | l'origine du précédent — CC BY 4.0, attribution obligatoire | référence |
| `https://data.binance.vision/data/futures/um/daily/aggTrades/` | dumps quotidiens Binance — reconstruction des POI | ✅ utilisé (`tools/regen-archive.js`) |
| Kaggle `marvingozo/hyperliquid-btc-high-frequency-microstructure` `versions/1` | carnet HL **fin à 537 ms** | ⚠️ **BTC seulement**, commence au 2026-05-08 |
| **London Strategic Edge** | archive gratuite multi-actifs + WebSocket live | ❌ **pas de profondeur de carnet** — voir §3 bis |
| **0xArchive** | L4 Hyperliquid | ⚠️ **photo fausse, diffs bons** — voir §5 |
| Artemis (S3 requester-pays, ~0,09 $/Go) | L4 depuis le 17/08/2025 | jamais acheté |
| SonarX · QuickNode | fournisseurs L4 | jamais évalués |

**Le dataset Kaggle a une valeur particulière** : c'est le seul carnet HL à
537 ms disponible, et c'est en le comparant à l'archive de travail (62 642 ms)
qu'on a découvert que **la grille de contact était 117× trop grossière**. Le
garder comme étalon.

---

## 3 bis. London Strategic Edge — qualifié le 04/08/2026

Vérifié **dans la documentation officielle**, pas de seconde main :
`londonstrategicedge.com/websocket-documentation`.

### Les endpoints réels

```
wss://data-ws.londonstrategicedge.com              flux live + rejeu 24 h
https://api.londonstrategicedge.com/vault          historique, options, exports
                    /candles   /series   /options/chain   /export   /usage
```

Authentification : en-tête `x-api-key` côté HTTP, message `{"action":"auth",
"api_key":…}` côté WS. Client Python : `pip install lse-data`.

**Ce qui est vrai et bien fait** — protocole JSON propre (`auth`, `subscribe`,
`unsubscribe`, `subscribe_options`, `list_symbols`, `ping`), accusés de réception
typés, codes d'erreur nommés, 100 connexions concurrentes par clé, et un
**rejeu jusqu'à 24 h en arrière qui bascule en live sur la même connexion**
(`replay: true` puis `replay_complete`) — pratique pour un bot qui redémarre.

Catalogue : ~4 100 instruments + ~263 000 contrats d'options vivants.

| catégorie | nombre |
|---|---|
| actions | ~3 987 |
| forex | ~62 |
| **crypto** | **~58** — `BTC/USD`, `ETH/USD`, `SOL/USD` |
| ETF | ~25 · commodities ~23 · indices ~13 |
| options | ~263 000 contrats sur 56 sous-jacents |

### Les trois points vérifiés — deux sont faux

| supposé | documentation officielle |
|---|---|
| WebSocket | ✅ **oui** — `wss://data-ws.londonstrategicedge.com` |
| « toutes les cryptos » | ❌ **~58**, listées au catalogue |
| « nanoseconde » | ❌ **la SECONDE** — voir citation ci-dessous |

> *« `ts` carries the source timestamp: **replay ticks always use epoch
> seconds**, live ticks may use **epoch seconds or an ISO string** depending on
> the asset class. »*

Et le champ du SDK : `timestamp` · type `float` · *« Unix timestamp »*. C'est
**neuf ordres de grandeur** au-dessus de la nanoseconde. Pire : le format n'est
même pas constant — il dépend de la classe d'actif.

### Ce qui disqualifie la source pour ce projet

Le tick, en entier :

```json
{"type":"tick","symbol":"AAPL","price":213.78,
 "bid":213.77,"ask":213.79,"volume":100,"ts":"2026-04-10T16:32:00Z"}
```

**Un seul bid, un seul ask** — et encore, « when available ». Aucune notion de
niveau, de palier, de L2, de profondeur, nulle part dans la documentation.

> C'est le **haut du carnet à la seconde**. Ce projet étudie des murs situés
> entre **0,12 et 0,80 % du mid**, à des centaines de paliers de là, sur des
> événements à **100 ms**. Une source sans profondeur ne peut ni fabriquer un
> label, ni porter une feature, ni alimenter une heatmap.

**Verdict : hors sujet pour la question centrale.** Utilisable comme série de
référence de prix, contexte macro, cross-asset ou options avec grecques — pas
comme source de microstructure.

### Un piège à connaître si on l'utilise quand même

> *« Subscribing to a symbol that is not in the catalog is **not an error**: the
> subscription is accepted and simply **delivers no ticks**. »*

C'est **exactement** le motif de la panne Binance du §5.1 : la connexion
acquitte et ne sert rien. Valider les symboles contre `client.catalog()` avant
de souscrire.

Autre point d'attention : les octets streamés **comptent sur le même quota
mensuel** que les téléchargements HTTP. `QUOTA_EXCEEDED` ferme la connexion.
Surveiller avec `GET /usage`.

---

## 4. Ce que Hyperliquid ne donne PAS — vérifié, et c'est structurant

* **L'API publique ne donne pas le L4.** `orderUpdates` et `openOrders` sont
  limités à **sa propre adresse**.
* Seul `trades` porte les adresses des contreparties — et **un spoof ne
  s'exécute jamais**, donc il est **invisible** dans les trades.
* ⇒ **La voie API seule est morte.** Le L4 vient soit d'un **nœud
  non-validateur** (`--write-order-statuses --write-fills
  --write-raw-book-diffs`, aucune compilation particulière), soit d'une archive.
* **Le nœud ne produit aucun historique** : il démarre le jour où on le lance.

À l'inverse, un point noté comme unique à Hyperliquid : `orderUpdates` **accepte
un portefeuille tiers nommé** — 1 513 mises à jour d'ordres en 45 s pour trois
portefeuilles. Aucune autre venue ne le permet.

---

## 5. Limites dures et pièges déjà payés

### La profondeur publique n'est pas la même partout

| venue | profondeur | portée relative |
|---|---|---|
| Binance, Coinbase | carnet complet | ±0,4 % |
| OKX | 400 paliers | ±0,069 % |
| Bybit | 200 paliers | ±0,039 % |
| **Hyperliquid (L2 public)** | **20 paliers/côté** | **±0,031 %** |

⇒ La cohérence 5 venues n'est mesurable que sur **±0,031 % (BTC)** /
**±0,101 % (ETH)** — **moins** que la bande des événements étudiés (0,12–0,8 %
du mid). Au-delà, **absence ≠ retrait**. Ne se contourne pas sans compte
privilégié (OKX `books-l2-tbt` = VIP4+).

Effet secondaire non prévu : **ETH est 3× mieux couvert que BTC**.

### Cinq pièges, avec leur coût

1. **Chemin Binance non routé = panne SILENCIEUSE.** La connexion s'ouvre, les
   SUBSCRIBE sont **acquittés** (`{"result":null}`), et **aucune donnée** n'est
   servie. Testé le 19/07/2026 : `…/ws/btcusdt@aggTrade` → **0 message**.
   `…/market/ws/btcusdt@aggTrade` → 21 msgs/10 s.
2. **Le depth et l'aggTrade ne prennent pas le même chemin.** Le routé est
   **obligatoire** pour `aggTrade` et **muet pour le depth**. Ce n'est pas une
   incohérence du code, c'est mesuré.
3. **`orderbook.500` est refusé par Bybit en linear** — « handler not found ».
   → 200.
4. **OKX publie `checksum: 0`** sur le canal `books` : le champ n'est pas
   alimenté, la **validation CRC32 est inactive** (elle se rallume seule si OKX
   se remet à l'alimenter). L'intégrité repose sur `prevSeqId` seul.
5. **0xArchive : la photo est fausse, les diffs sont bons.** Mesuré le
   02/08/2026. Ne jamais consommer sa photo L4 telle quelle.

### Le nommage n'est pas portable

L'appariement « même niveau entre venues » se fait sur **l'écart RELATIF au
mid**, jamais sur le prix absolu — tick sizes, basis et mid diffèrent. Basis
mesuré contre Binance : Bybit −0,7 bp · OKX −0,3 bp · Hyperliquid −0,9 bp ·
**Coinbase −9,0 bp** (spot : Coinbase n'expose pas de perp sans compte).

---

## 6. Ce qui reste à documenter

* **London Strategic Edge** — qualifié le 04/08/2026, voir §3 bis. Verdict :
  pas de profondeur de carnet, donc hors sujet pour la question centrale. Rien
  n'en avait jamais été tiré dans aucune itération : l'URL n'apparaissait que
  dans `-NinjaCat-/docs/links.txt` et dans les permissions d'une session
  `-OrderFlowAntho-`, sans un seul fichier ni script pour la consommer.
* **L'archive de production `gon-sec-recorder` se dégrade** : volume divisé par
  ~40 après le 27/07 (39,2 Mo → 1 Mo/jour) et le **03/08 manque entièrement**.
  Si cette source doit alimenter l'affichage, la diagnostiquer est un préalable.
* **Les clés d'API** : aucune n'est nécessaire pour ce qui précède — tout est
  public. Si un compte privilégié devient nécessaire (OKX VIP4+), il change le
  périmètre de la §5 et se décide (voir la répartition des rôles du prompt, §12).
