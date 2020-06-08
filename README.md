Note - EN: _Development is currently stalled (mostly because I'm lazy). I'm planning to do a second iteration of this project, focused more generally – you create an account, and then you can import homework from various services like Bakaláři, Google Classroom or Moodle. ETA September_

CS: _Vývoj je aktuálně pozastavený (převážně z důvodu mojí lenosti). Plánuji vytvořit druhou verzi tohoto projektu, zaměřenou více obecně – vytvoříte si účet, a poté můžete importovat úkoly z různých zdrojů, například Bakalářů, Google Classroom, Moodle… Aplikace bych chtěl mít hotovou před začátkem nového školního roku._

# Bakaláři-homework-tasklist

Zadávají vám učitelé domácí úkoly přes Bakaláře a je to pro vás nepřehledné a chtěli
byste si sami spravovat, které úkoly jsou hotové, a které ještě pár dní počkají?  
_Ano, nejste sami._

Tato aplikace vám zobrazí všechny úkoly z Bakalářů a umožní vám si je třídit do několika
skupin (hotové, odložené&hellip;)

## Jak to funguje?

Do aplikace zadáte adresu vašich bakalářů, uživatelské jméno a heslo. Heslo není nikde
uloženo, jen je použito k vygenerování přístupového tokenu. Tento token je pak použit
pro stáhnutí všech úkolů z Bakalářů. Samotné třídění úkolů pak probíhá a je uloženo
pouze v této aplikaci.

## Vývoj aplikace

Tuto aplikaci jsem vytvořil v březnu 2020 během přerušení výuky na školách kvůli šíření
virového onemocnění COVID-19, způsobeného virem SARS-CoV-2 (&ldquo;wuchanský
koronavirus&rdquo;).

Zdrojové kódy jsou k dispozici v tomto repozitáři.

## Kontakt

Uvítám hlášení o chybách, návrhy na vylepšení i jakoukoliv jinou zpětnou vazbu ohledně
aplikace.

Preferuji komunikaci přes Telegram. Je tam tedy založený kanál
[@bakatasklist](https://t.me/bakatasklist) a k němu připojená diskuzní skupina. Další
způsoby kontaktu jsou uvedené na stránce
[Kontakt](https://bakalari-homework-tasklist.herokuapp.com/contact).

# Disclaimer

Tato aplikace je vyvíjena kompletně nezávisle na společnosti BAKALÁŘI Software,
s. r. o., a nemá s touto společností nic společného, ani jí není schvalována.  
Tato aplikace pouze stahuje data ze systémů vyvinutých touto firmou a následně umožňuje
uživatelům zobrazit stejná data, která by viděli v těchto systémech, ale mírně odlišným
způsobem.
