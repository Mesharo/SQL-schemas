# SQL-schemas

Extrakce schématu databáze z kolekce otázek na StackOverflow s využitím analýzy SQL

StackOverflow je jedna z největších question and answer sítí. Je zde statisíce otázek s tématem SQL a velké množství SQL dotazů. Pro další analýzu SQL dotazů by byla vhodná znalost schématu databáze, kterých se dotazy týkají. Schéma bývá v textu uvedeno v různých formách. Cílem této práce je zautomatizovat čtení schémat pro co největší množství SQL.

- Seznámení se s možnostmi parsrování SQL a extrakce schématu z SQL dotazu.
- Implementace knihovny, která pro vstupní SQL dotaz vrátí seznam tabulek spolu se seznamem atributů a případně i s návrhy datových typů jednotlivých atributů.
- Příprava trénovací kolekce pro umělou inteligenci, kde pro StackOverflow dotaz bude uveden očekávaný DDL skript. Kolekce bude mít alespoň sto prvků.
- Implementace ověřovací aplikace, která pro DDL skript vykoná dotaz.
