Features:
 - Generare fisier pentru program de tiparit Bon Fiscal din POS
 - Căutare în POS după codul fiscal


Case de marcat compatibile cu acest modul:
 - Datecs - variantele noi (2018), impreună cu driver-ul FiscalWire
 - Optima - împreună cu driver-ul QComm
 - Incotex Succes - împreună cu driver-ul FiscalPrinterDevice


In teste:
 - Datecs - cu driver-ul FiscalNet
 - Datecs - cu driverul de la Incotex Group


Deltatech ECR face legătura între punctul de vânzare Odoo și casa de marcat configurată pentru a putea
tipari bonuri fiscale în modul conexiune PC. Mai exact, generează un fișier în formatul adecvat tipăririi
de către o casă de marcat. In funcție de modelul casei de marcat, aveți nevoie de un driver de comunicație.

După instalarea driverului și configurarea licentei, aveți acces la functiile casei de marcat in
modul Conexiune PC direct din Odoo. Nu va mai fi nevoie sa operati din utilitarul instalat.
Se vor putea introduce/scoate bani in/din casa, tipari rapoarte X sau rapoarte Z si desigur bonuri fiscale.

Bonul va fi tipărit obligatoriu după finalizarea comenzii și selectarea modalității de plată.
Sistemul va genera un mesaj de eroare dacă nu se apasă butonul de tipărire.

Modulul Deltatech ECR se va integra în Odoo și va permite accesul la setari și functionalitati standard
sau personalizate. Se vor putea configura din setarile punctului de vanzare modalitatile de plata specifice.

Corespondenţa modalităţilor de plată (Numerar, Card, Tichet masă) din casa de marcat cu jurnalul Odoo
se poate configura în metodele de plată.

.. figure:: https://apps.odoocdn.com/apps/assets/14.0/deltatech_pos/settings.png
    :align: center
    :alt: Settings
