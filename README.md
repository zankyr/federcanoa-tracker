# federcanoa-tracker
Notifica la pubblicazione di nuovi corsi FICK

<!-- TOC -->
* [federcanoa-tracker](#federcanoa-tracker)
  * [Installazione](#installazione)
  * [Utilizzo](#utilizzo)
  * [Configurazione](#configurazione)
  * [Licenza](#licenza)
<!-- TOC -->

## Descrizione
Il progetto è stato realizzato per monitorare la pubblicazione di nuovi corsi di canoa/kayak sul sito della [FICK](https://www.federcanoa.it/).

Il programma effettua una richiesta HTTP al sito della FICK e cerca la parola chiave specificata nel file di configurazione. Se la parola chiave viene trovata, viene inviata una notifica Telegram.

Al momento, il programma è stato testato solo con i corsi del comitato della regione Lombardia.

## Installazione
```bash
make install
```

## Utilizzo
```bash
make run
```

## Configurazione
1. Copia il file di esempio
```bash
cp config.example.json config.json
```

2. Modifica il file `config.json` con i tuoi dati
```json
{
  "site_url": "https://www.federcanoa.it/",
  "courses_url": "lombardia.html?id=25&layout=menu4",
  "keyword": "corso",
  "telegram_bot_token": "1234567890:ABCDEF",
  "telegram_chat_id": "1234567890"
}
```

## Licenza
[MIT](LICENSE)

