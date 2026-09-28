# Collegare VS Code, GitHub e ChatGPT

Il progetto è già pronto da aprire in VS Code. Il collegamento al profilo GitHub e l'autorizzazione dell'app a leggere/scrivere uno specifico repository sono due passaggi distinti. Non inserire password o token nei file del progetto o nella chat.

## VS Code sul tuo computer

1. Estrai la cartella e apri `Fabio_Investment_Lab.code-workspace` in VS Code.
2. Installa le estensioni suggerite: Python, Pylance, Jupyter e **Codex di OpenAI** (`openai.chatgpt`). La documentazione ufficiale è https://learn.chatgpt.com/docs/codex/ide.
3. Apri la barra laterale Codex e accedi con lo stesso account ChatGPT. L'estensione usa la cartella aperta nell'editor; non rende automaticamente tutte le cartelle del computer accessibili alla chat web.
4. Crea `.venv`, installa `requirements.txt` e seleziona l'interprete Python della cartella. I comandi completi sono nel README. Puoi eseguire i task “Research: run all projects” e “Research: validate”.

## Repository GitHub

Repository pubblico: https://github.com/UmileClark/investment-research-lab

Per aprire una copia locale collegata al repository:

```bash
git clone https://github.com/UmileClark/investment-research-lab.git
cd investment-research-lab
code Fabio_Investment_Lab.code-workspace
```

Se il comando `code` non è disponibile, apri il file workspace dal menu di VS Code. Per le modifiche successive, usa Source Control: rivedi il diff, crea un commit e fai push. Il repository pubblico contiene i nove progetti, i dati congelati, i notebook e i test, pubblicati il 28 settembre 2026 tramite il browser GitHub autorizzato. L’autenticazione Git sul tuo computer resta da configurare in VS Code/GitHub quando richiesta. La pubblicazione via browser non modifica i permessi della connessione GitHub di ChatGPT: se quella connessione restituisce ancora 403, occorre verificarne l’accesso al repository nelle impostazioni.


## Dare accesso a questo account ChatGPT

Apri la connessione GitHub nelle impostazioni delle app/connessioni di ChatGPT o la configurazione dell'ambiente Codex collegato a GitHub. Nella schermata di GitHub autorizza il solo repository desiderato, se questa opzione è disponibile. Il consenso e l'accesso sul tuo dispositivo devono essere completati da te quando richiesti: non posso installare un'estensione sul tuo computer da questa sessione.

Il codice locale, GitHub e il sito non si sincronizzano per il solo fatto di aver effettuato l'accesso: commit/push aggiornano GitHub; una pubblicazione aggiorna il sito. Il workflow incluso riproduce i report su GitHub, ma non esegue ordini e non pubblica automaticamente nuove allocazioni.

Riferimenti ufficiali: https://learn.chatgpt.com/docs/codex/ide e https://learn.chatgpt.com/docs/cloud. La disponibilità delle funzioni dipende dal piano e dalle autorizzazioni dell'account.
