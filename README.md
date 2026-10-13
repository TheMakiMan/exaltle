# Exaltle · Das tägliche Preis-Ratespiel für Path of Exile 2

Inoffizielles, nicht-kommerzielles Fan-Projekt. Jeden Tag ein Item aus PoE 2, dessen aktuellen Marktpreis man schätzt, dazu der Modus „Höher oder tiefer“. Preise von [poe.ninja](https://poe.ninja), für jede Liga.

This product isn't affiliated with or endorsed by Grinding Gear Games in any way.

## So funktioniert's technisch

- `site/` ist die fertige Website. Sie wird kostenlos über **GitHub Pages** veröffentlicht.
- `scripts/update_data.py` holt **einmal täglich um 00:07 UTC** die Preise von poe.ninja: alle Ligen, Währung, Handelsgüter und Unique-Items. Dabei lädt es auch die Item-Bilder herunter und legt das Tagesrätsel fest. Das erledigt GitHub automatisch über `.github/workflows/update.yml`.
- Besucher deiner Seite verbinden sich nie mit poe.ninja, Google oder GGG. Alles kommt von deiner eigenen Seite. Das schont poe.ninja und ist gut für den Datenschutz.
- Die Seite gibt es auf **Englisch, Deutsch, Spanisch, Französisch, Portugiesisch und Russisch**. Sie startet in der Sprache des Browsers (sonst Englisch), oben lässt sie sich per Dropdown umstellen. Die Texte stehen in `site/index.html` im Abschnitt `I18N`. Item-Namen bleiben englisch, so wie poe.ninja sie liefert.
- Beim Veröffentlichen trägt die Automatik die echte Adresse deiner Seite ein. Daraus entstehen die Link-Vorschau mit Bild für Discord und Reddit sowie `robots.txt` und `sitemap.xml` für Google.

## Online stellen (einmalig, ca. 15 Minuten)

1. **GitHub-Konto anlegen** auf [github.com](https://github.com), falls du noch keins hast.
2. **Neues Repository erstellen:** oben rechts auf **+** → **New repository**.
   - Name: `exaltle` (der Name des Repositorys wird Teil der Adresse)
   - **Public** auswählen (GitHub Pages ist für öffentliche Repositories kostenlos)
   - Auf **Create repository** klicken.
3. **Dateien hochladen:** Im neuen Repository auf **uploading an existing file** klicken. Den **Inhalt** des entpackten ZIP-Ordners (`site`, `scripts`, `.github`, `README.md`, `.gitignore`) hineinziehen und mit **Commit changes** bestätigen.
   - Wichtig: Der Ordner `.github` beginnt mit einem Punkt und ist auf Mac und Windows oft versteckt. Prüf danach, ob es im Repository die Datei `.github/workflows/update.yml` gibt. Falls nicht: **Add file → Create new file**, als Namen `.github/workflows/update.yml` eintippen (die Schrägstriche legen die Ordner automatisch an), den Inhalt der Datei aus dem ZIP hineinkopieren und auf **Commit changes** klicken.
4. **GitHub Pages einschalten:** **Settings → Pages**, bei **Source** die Option **GitHub Actions** auswählen.
5. **Schreibrechte für die Automatik:** **Settings → Actions → General**, ganz unten bei **Workflow permissions** die Option **Read and write permissions** auswählen und auf **Save** klicken.
6. **Erste Preise holen:** Reiter **Actions** → links **Preise aktualisieren und Seite veröffentlichen** → **Run workflow** → **Run workflow**. Nach ca. 3 bis 5 Minuten ist alles grün.
7. **Fertig!** Deine Seite ist dann unter `https://DEIN-NAME.github.io/exaltle/` erreichbar. Den Link siehst du auch unter **Settings → Pages**.

Ab jetzt aktualisiert sich alles von selbst: jeden Tag neue Preise und ein neues Tagesrätsel.

## Bei Google anmelden (optional, ca. 5 Minuten)

Google findet die Seite irgendwann auch von selbst. Mit der kostenlosen Search Console geht es meist in wenigen Tagen:

1. Auf [search.google.com/search-console](https://search.google.com/search-console) mit deinem Google-Konto anmelden.
2. **Property hinzufügen** → **URL-Präfix** wählen → deine Adresse eintragen, z. B. `https://DEIN-NAME.github.io/exaltle/`.
3. Als Bestätigungsmethode **HTML-Datei** wählen und die Datei herunterladen (sie heißt z. B. `google1234abcd.html`).
4. Die Datei im Repository in den Ordner `site` hochladen: In `site` auf **Add file → Upload files** klicken und mit **Commit changes** bestätigen. Nach ca. 2 Minuten ist sie online.
5. In der Search Console auf **Bestätigen** klicken.
6. Links unter **Sitemaps** die Adresse `sitemap.xml` eintragen und senden.

**Tipp:** Noch mehr bringen Links von anderen Seiten. Poste die Seite auf r/PathOfExile2 und schlag sie für die Liste mit 500+ Daily-Games vor: [github.com/qubit10/dles](https://github.com/qubit10/dles).

## Vor dem Teilen: Impressum ausfüllen

In Österreich braucht jede Website eine Offenlegung nach § 25 Mediengesetz, auch eine private. Öffne im Repository `site/impressum.html`, klick auf den Stift (**Edit**) und ersetz die drei Platzhalter in eckigen Klammern:

- `[Vorname Nachname]`
- `[Ort]`
- `[E-Mail-Adresse]`

Danach auf **Commit changes** klicken. Die Seite aktualisiert sich nach ein paar Minuten.

## Regeln, damit es rechtlich entspannt bleibt

- **Keine Werbung, keine Einnahmen.** GGG duldet die nicht-kommerzielle Nutzung von Item-Namen und Bildern, erlaubt aber keine Einnahmen mit ihrem geistigen Eigentum.
- Der Hinweis „This product isn't affiliated with or endorsed by Grinding Gear Games in any way.“ bleibt auf der Seite.
- Kein GGG- oder PoE-Logo verwenden und nicht wie eine offizielle Seite auftreten. „Path of Exile“ gehört auch nicht in den Seitennamen oder die Domain.
- Bittet GGG oder poe.ninja um eine Änderung, setz sie einfach um.

Das ist keine Rechtsberatung, sondern der Stand der öffentlichen Regeln von GGG und poe.ninja (Oktober 2026).

## Häufige Fragen

**Der Workflow ist rot. Was nun?**
Klick im Reiter **Actions** auf den fehlgeschlagenen Lauf und dann auf den roten Schritt, dort steht der Grund. Häufige Ursachen:
- **Bei „Neue Daten im Repository speichern“:** Schritt 5 (Schreibrechte) fehlt.
- **Bei „deploy“:** Schritt 4 (Pages auf „GitHub Actions“) fehlt. Danach einfach nochmal **Run workflow** klicken.
- **Bei „Preise holen“:** poe.ninja war kurz nicht erreichbar. Morgen läuft es automatisch wieder, oder du startest den Lauf später per Hand.

**Eine Kategorie fehlt (z. B. „Runes: übersprungen“).**
Dann hat poe.ninja für diese Kategorie gerade keine Daten geliefert. Die Seite funktioniert mit allen anderen Kategorien weiter.

**Ich will den Namen ändern.**
In `site/index.html` nach `Exaltle` suchen und überall ersetzen (Titel, Logo, Link-Vorschau, Teilen-Texte in allen Sprachen), genauso in `site/impressum.html` und `site/datenschutz.html`. Das Vorschaubild `site/og-image.png` zeigt den alten Namen und müsste dann neu gemacht werden.

**Ich will die Seite lokal ansehen.**
Im Ordner `python -m http.server -d site` ausführen und `http://localhost:8000` öffnen. Ohne Preisdaten zeigt sie nur eine Fehlermeldung. Die Daten entstehen erst durch `python scripts/update_data.py`.

**Die tägliche Automatik ist stehengeblieben.**
GitHub pausiert geplante Abläufe, wenn ein Repository 60 Tage lang inaktiv war. Weil die Automatik täglich neue Preise speichert, passiert das normalerweise nicht. Falls doch: **Actions** → Workflow → **Enable workflow**.

## Quellen & Lizenzen

- Preisdaten: [poe.ninja](https://poe.ninja) ([API-Regeln](https://poe.ninja/docs/api))
- Item-Namen und Bilder: © Grinding Gear Games
- Schriften: Cinzel und Alegreya Sans, SIL Open Font License, über [Fontsource](https://fontsource.org)
